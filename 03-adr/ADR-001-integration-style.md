# ADR-001: Kiểu tích hợp đơn thuốc với nhà thuốc và Hệ thống đơn thuốc quốc gia — Gateway + hàng đợi bền (outbox, idempotency)

- **Trạng thái:** Đề xuất (chờ nhóm duyệt) | **Ngày:** 2026-11-03 | **Tác giả:** TV2 | **Người duyệt:** TV1, TV3
- **Liên quan:** G-04, FR-06, FR-07, NFR-DAT-01, NFR-INT-01, NFR-INT-02, NFR-AVL-01, CON-06, CON-07, PR-06, PR-08; ADR-004 (mô hình lưu đơn); RSK-03, RSK-04, RSK-07

## 1. Bối cảnh
- Mỗi đơn phát hành phải tới 2 nơi ngoài phòng khám: Hệ thống đơn thuốc quốc gia (FR-06) và nhà thuốc BN chọn (8 nhà thuốc: 2 nội bộ + 6 đối tác, ASSUMP-04). OC-04 đòi ≥ 95% đơn đẩy xong trong ≤ 5 phút.
- Nhà thuốc đối tác dùng phần mềm riêng, không bắt buộc đổi (CON-06); kết nối Internet của họ không ổn định (RSK-03).
- Không được mất đơn và không được ghi nhận cấp thuốc hai lần (NFR-DAT-01). Gửi lại sau lỗi mạng là chuyện thường, nên mỗi thông điệp phải xử lý được nhiều lần mà kết quả như một lần.
- Thêm nhà thuốc mới không được sửa hệ thống lõi (NFR-INT-02). Đội CNTT nhỏ (CON-07).

## 2. Phương án
| | Mô tả |
|---|---|
| **A. API đồng bộ điểm–điểm** | Khi bác sĩ phát hành đơn, AC-ePrescription gọi thẳng API của nhà thuốc được chọn và API hệ thống quốc gia trong cùng yêu cầu; lỗi thì báo bác sĩ thử lại. Mỗi nhà thuốc một đoạn code tích hợp riêng trong AC-ePrescription. |
| **B. Cổng tích hợp + hàng đợi bền** | AC-ePrescription ghi đơn và một bản ghi `DO-OutboxEvent` trong **cùng giao dịch** (transactional outbox). Bộ phát đẩy sự kiện vào hàng đợi bền (TS-Messaging). AC-PharmacyGateway tiêu thụ, chuyển sang FHIR (MedicationRequest), gửi webhook cho nhà thuốc có tích hợp, gửi lên hệ thống quốc gia, thử lại có backoff, hỏng quá N lần thì vào hàng lỗi (DLQ) để người xử lý. Nhà thuốc không tích hợp dùng AI-PharmacyWebUI. Chiều về: nhà thuốc gọi `POST /pharmacy/dispenses` với `Idempotency-Key = dispenseId`. |
| **C. CSDL dùng chung / trao đổi file theo lô** | Phòng khám mở một view CSDL (hoặc xuất file CSV/SFTP mỗi 15 phút) để nhà thuốc đọc đơn và ghi kết quả cấp vào bảng chung; đẩy lên hệ thống quốc gia theo lô cuối ngày. |

## 3. Tiêu chí và chấm điểm (1–5, cao là tốt; với chi phí, 5 = rẻ/đơn giản)
| Tiêu chí | Trọng số | A | B | C |
|---|---|---|---|---|
| Không mất, không trùng đơn/bản ghi cấp (NFR-DAT-01) | 25% | 2 | 5 | 3 |
| Chịu được đối tác mất kết nối (NFR-AVL-01, RSK-03) | 20% | 1 | 5 | 4 |
| Thêm nhà thuốc không sửa lõi (NFR-INT-02, CON-06) | 20% | 2 | 4 | 3 |
| Độ trễ liên thông ≤ 5 phút (OC-04) | 15% | 5 | 4 | 1 |
| Chi phí và độ phức tạp vận hành (CON-07) | 10% | 4 | 2 | 4 |
| Truy vết được từng lần gửi/nhận (NFR-SEC-03) | 10% | 3 | 5 | 2 |
| **Tổng có trọng số** | 100% | **2,55** | **4,35** | **2,90** |

Giải thích điểm đáng chú ý:
- A nhanh nhất khi mọi thứ chạy tốt, nhưng một nhà thuốc mất mạng làm bác sĩ không phát hành được đơn: lỗi của đối tác chặn nghiệp vụ lõi (trái PR-08). Gọi lại sau timeout dễ tạo bản ghi trùng vì không biết lần trước đã tới hay chưa.
- C giữ được đơn khi đối tác mất mạng (file vẫn nằm đó), nhưng chu kỳ lô 15 phút và đẩy quốc gia cuối ngày vi phạm OC-04; mở CSDL cho đối tác trái PR-08 và khó cấp quyền theo từng nhà thuốc.
- B mất điểm chi phí vì thêm broker, bộ phát outbox và DLQ phải vận hành; đây là đánh đổi được chấp nhận vì TV3 đã có ND-MessageBroker cho AC-Notification và AC-Audit.

## 4. Quyết định
Chọn **B**. Hàng đợi bền + outbox bảo đảm "ghi đơn thành công thì sự kiện chắc chắn được phát" (at-least-once); idempotency key ở chiều về và khóa `prescriptionId + eventId` ở chiều đi biến "ít nhất một lần" thành "hiệu quả đúng một lần". Lỗi của một nhà thuốc chỉ làm chậm đơn của nhà thuốc đó.

## 5. Đánh đổi
- **Được:** bác sĩ không bao giờ bị chặn vì đối tác; thêm nhà thuốc = thêm cấu hình/adapter trong Gateway; mọi lần gửi có bản ghi để đối soát.
- **Mất:** nhất quán sau cùng: nhà thuốc thấy đơn chậm vài giây; phải vận hành broker, theo dõi DLQ; nhóm phải giải thích được at-least-once khi bảo vệ.

## 6. Rủi ro và giảm thiểu
- RSK-03 (mất kết nối): hàng đợi giữ sự kiện, thử lại có backoff; quá 5 phút thì cảnh báo vận hành và BN vẫn có mã đơn/QR để mua ở nhà thuốc khác (đổi nhà thuốc theo ASSUMP-10).
- RSK-04 (đồng bộ lặp): `dispenseId` duy nhất ở CSDL; gửi lặp trả lại kết quả cũ (HTTP 200), không tạo bản ghi mới.
- RSK-07 (hệ thống cũ khó tích hợp): Gateway có adapter riêng cho từng định dạng; nhà thuốc không tích hợp được thì dùng web.

## 7. Phần tử ArchiMate bị ảnh hưởng
AC-ePrescription, AC-PharmacyGateway, AI-PharmacyAPI, AI-PharmacyWebUI, AI-EventChannel, DO-OutboxEvent, DO-DispenseRecord, EXT-PharmacySystem, EXT-NationalRxSystem; tầng công nghệ: TS-Messaging (ND-MessageBroker, SW-RabbitMQ), TS-ApiGateway, NW-PartnerChannel.

## 8. Điều chỉnh theo biến thể
- **A (liên thông 2 cơ sở):** mở rộng cùng kiểu B thành mô hình hub-and-spoke: AC-IntegrationHub + một AC-FhirAdapter cho mỗi cơ sở, mô hình chuẩn FHIR. So với nối điểm–điểm, số kết nối tăng tuyến tính theo số cơ sở thay vì n(n−1)/2. Cần ADR riêng cho ghép định danh (MPI: tất định theo CCCD/BHYT so với xác suất).
- **B (nhà thuốc mất kết nối):** thêm AC-PharmacyAgent tại nhà thuốc giữ outbox cục bộ cho bản ghi cấp; khi có mạng gửi lô `POST /pharmacy/sync`; đối soát theo ADR-004.
- **C (sửa/thu hồi đơn):** sự kiện `PrescriptionAmended`/`PrescriptionRevoked` đi chung kênh; nhà thuốc phải xác nhận đã nhận (`POST /pharmacy/prescriptions/{rxCode}/ack`); quá hạn chưa xác nhận thì Gateway gọi lại và báo bác sĩ.

## 9. Điều kiện xem xét lại
- Số đối tác vượt khoảng 50 hoặc có yêu cầu đẩy dưới 1 giây: cân nhắc nền tảng sự kiện chuyên dụng.
- Bộ Y tế bắt buộc nhà thuốc nhận đơn **chỉ** qua Hệ thống đơn thuốc quốc gia: kênh tới nhà thuốc trở thành phụ, xem lại phạm vi AC-PharmacyGateway.
