# Mô tả màn hình prototype — TV3, v0.1 (2026-11-03)

Mỗi màn hình gắn với BPMN task (mã BP của TV1), Application Service (TV2) và API (openapi.yaml). Ảnh chụp trong `screenshots/`.

| Màn hình | Vai trò (BR) | BPMN task | AS | API | Ảnh |
|---|---|---|---|---|---|
| S1 Đặt lịch | BR-BenhNhan, BR-LeTan | BP-01.1, BP-01.2 | AS-BookAppointment, AS-SendNotification | `GET /slots`, `POST /appointments` | S1-dat-lich.png |
| S2 Tiếp đón | BR-LeTan | BP-02.1, BP-02.2, BP-02.3 | AS-CheckIn, AS-VerifyInsurance | `POST /encounters`, `GET /encounters` | S2-check-in.png |
| S3 Khám & kê đơn | BR-BacSi | BP-03.2, BP-04.1–BP-04.4 | AS-ViewMedicalRecord, AS-CheckDrugSafety, AS-IssuePrescription, AS-SubmitNationalRx | `GET /patients/{id}/records`, `POST /prescriptions`, `POST /prescriptions/{id}/issue` | S3-canh-bao-di-ung.png, S3-phat-hanh-don.png |
| S4 Nhà thuốc | BR-DuocSi | BP-05.1, BP-05.3 | AS-ReceivePrescription, AS-RecordDispense | `GET /pharmacy/prescriptions/{rxCode}`, `POST /pharmacy/dispenses` | S4-nha-thuoc-cap.png, S4-gui-lai-idempotent.png |
| S5 Nhật ký | BR-QuanTriBaoMat, BR-BenhNhan | BF-01 | AS-QueryAudit | `GET /audit-events`, `GET /audit-events/verify` | S5-nhat-ky-hop-le.png, S5-phat-hien-sua.png, S5-benh-nhan-xem-vet.png |
| S6 Từ chối & break-glass (ngoại lệ) | BR-BacSi | BF-01 (nhánh ngoại lệ) | AS-Authorize | `GET /patients/{id}/records` (403), `POST /access/break-glass` | S6-tu-choi-truy-cap.png, S6-break-glass.png |

## S1 · Đặt lịch khám
- **Mục đích:** BN tự chọn khung giờ trống của bác sĩ/chuyên khoa, xác nhận tức thì (FR-01), nhận mã QR qua SMS (FR-10).
- **Thành phần:** lưới khung giờ (khung đã đặt bị mờ), ô lý do khám, nút "Xác nhận đặt lịch". Lễ tân dùng cùng màn hình, thêm ô mã BN để đặt hộ (kênh tổng đài BI-02).
- **Ngoại lệ trên màn:** khung giờ vừa bị người khác đặt → thông báo 409 + gợi ý 3 khung gần nhất.

## S2 · Tiếp đón (check-in)
- **Mục đích:** check-in ≤ 60 giây (NFR-USB-01): quét QR, đặt CCCD lên đầu đọc chip, hệ thống xác minh BHYT (mock EXT-InsurancePortal), mở lượt khám, cấp số thứ tự.
- **Thành phần:** ô mã QR, ô CCCD (tự điền từ đầu đọc), bảng hàng chờ hôm nay (số thứ tự, BN, bác sĩ, BHYT, trạng thái).
- **Ngoại lệ:** CCCD không khớp lịch hẹn → 422 "chuyển xác minh thủ công" (biến thể A mở rộng thành ghép định danh liên cơ sở).

## S3 · Khám & kê đơn điện tử
- **S3a Hàng chờ của tôi:** bác sĩ chỉ thấy BN được phân cho mình (POL-01).
- **S3b Hồ sơ:** băng cảnh báo dị ứng nổi bật màu đỏ ở đầu, tiền sử (ICD-10), danh sách đơn cũ với trạng thái. Nếu đang dùng quyền khẩn cấp, tiêu đề có nhãn **BREAK-GLASS**.
- **S3c Kê đơn:** chẩn đoán, bảng thuốc (chọn từ danh mục AC-MasterData), liều, số lượng; nút "Lưu & kiểm tra an toàn" rồi "Ký số & phát hành".
- **Ngoại lệ trên màn:** thuốc cùng nhóm với dị ứng → hộp đỏ "Cảnh báo an toàn thuốc", không cho lưu trừ khi sửa đơn hoặc ghi lý do bỏ qua (được ghi nhật ký).
- **Kết quả:** mã đơn, người ký, trạng thái liên thông đơn thuốc quốc gia, SMS mã đơn cho BN (FR-06).

## S4 · Nhà thuốc nhận đơn & cấp thuốc
- **Mục đích:** dược sĩ (nội bộ hoặc đối tác qua AI-PharmacyWebUI) tra đơn bằng mã + 4 số cuối SĐT BN (POL-04), thấy **dữ liệu tối thiểu** (tên, năm sinh, thuốc, liều; không có chẩn đoán/tiền sử), chữ ký hợp lệ, phiên bản đơn.
- **Thành phần:** ô mã đơn, ô xác minh, bảng thuốc (kê / đã cấp / cấp lần này), nhãn "Kiểm soát" cho thuốc thuộc CON-04, khóa Idempotency hiển thị mờ.
- **Ngoại lệ:** đơn REVOKED/SUPERSEDED/đã cấp đủ → khung đỏ, nút cấp bị khóa; bấm xác nhận 2 lần (hoặc mạng gửi lại) → "Đã ghi nhận trước đó", không tạo bản ghi thứ 2; nhà thuốc đối tác cấp thuốc kiểm soát → 403 (POL-06).

## S5 · Nhật ký truy cập
- **DPO:** lọc theo BN và quyết định (PERMIT/DENY); mỗi dòng: thời điểm, người + vai trò, hành động (nhãn BREAK-GLASS và lý do), đối tượng, quyết định + mã chính sách, đoạn đầu mã băm. Nút "Kiểm chứng chuỗi băm" → hộp xanh "Chuỗi hợp lệ" hoặc hộp đỏ "Phát hiện sửa đổi tại bản ghi #n".
- **Bệnh nhân:** cùng bảng nhưng chỉ hồ sơ của mình ("Ai đã xem hồ sơ của tôi") — thể hiện quyền của chủ thể dữ liệu (CON-02).

## S6 · Truy cập bị từ chối & truy cập khẩn cấp (ngoại lệ chính của prototype)
- **Khi nào:** bác sĩ không có quan hệ điều trị mở hồ sơ.
- **Thành phần:** hộp đỏ nêu chính sách bị vi phạm (POL-01) và "lần truy cập này đã được ghi nhật ký"; hộp tím break-glass: ô lý do bắt buộc ≥ 10 ký tự, nút đỏ "Xác nhận truy cập khẩn cấp", ghi chú "4 giờ, không kê đơn, DPO rà soát 24 giờ".
- **Sau xác nhận:** hồ sơ hiện với nhãn BREAK-GLASS; nếu thử kê đơn → 403.

## Màn hình theo biến thể (vẽ thêm khi biết biến thể; API đã có trong mock)
| Biến thể | Màn hình | Nội dung |
|---|---|---|
| A | S2-A Ghép định danh | Bảng ứng viên trùng giữa CS1/CS2 với điểm khớp; AUTO_LINK khi CCCD khớp, MANUAL_REVIEW khi chỉ khớp tên/năm sinh; nút "Liên kết"/"Tạo mới"; hỏi consent trước khi xem hồ sơ cơ sở kia |
| B | S4-B Nhà thuốc offline | Băng vàng "Đang mất kết nối — cấp theo đơn đã lưu, giới hạn" ; thuốc kiểm soát bị khóa; sau khi có mạng: bảng kết quả đồng bộ ACCEPTED / DUPLICATE / CONFLICT + nút mở hồ sơ đối soát |
| C | S3-C Điều chỉnh/thu hồi đơn | Hộp thoại chọn "Thu hồi" hoặc "Điều chỉnh", lý do bắt buộc; nếu đơn đã cấp: chỉ cho điều chỉnh, hiển thị số đã cấp và cảnh báo BN nhận thừa; S4 hiển thị "Đơn đã được thay bằng phiên bản mới" |
