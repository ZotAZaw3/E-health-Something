# ADR-004: Mô hình lưu dữ liệu đơn thuốc — đơn bất biến theo phiên bản + sổ cái cấp thuốc append-only

- **Trạng thái:** Đề xuất (chờ nhóm duyệt) | **Ngày:** 2026-11-03 | **Tác giả:** TV2 | **Người duyệt:** TV1, TV3
- **Liên quan:** G-02, G-03, FR-05, FR-07, FR-11, NFR-DAT-01, NFR-SEC-03, PR-05, CON-03; biến thể: FR-B2, FR-B3, FR-C1, FR-C2; ADR-001, ADR-003; RSK-04

## 1. Bối cảnh
- Đơn đã ký số là chứng từ pháp lý (CON-03): nội dung đã ký không được thay đổi; mọi thay đổi phải để lại lịch sử (PR-05).
- Một đơn có thể được cấp nhiều lần (cấp một phần). Tổng số đã cấp không bao giờ vượt số kê, kể cả khi bản ghi cấp đến muộn hoặc đến hai lần (NFR-DAT-01, RSK-04).
- Báo cáo vận hành cần đếm nhanh tỷ lệ đơn phải sửa, thời gian liên thông (FR-11).
- Nhóm 3 người, 5 tuần; mô hình phải giải thích được trong 1 slide.

## 2. Phương án
| | Mô tả |
|---|---|
| **A. CRUD ghi đè + bảng lịch sử bằng trigger** | Một dòng `prescription` được UPDATE tại chỗ (trạng thái, số lượng đã cấp); trigger CSDL chép bản cũ sang `prescription_history`. |
| **B. Đơn bất biến theo phiên bản + sổ cái cấp thuốc** | Nội dung đơn đã ISSUED không bao giờ UPDATE; sửa đơn (nếu có) = dòng mới `version + 1` trỏ `supersedes`. Mỗi lần cấp = một dòng `dispense_record` + `dispense_line` chỉ INSERT, khóa duy nhất `dispenseId`. `status` và `qtyDispensed` là giá trị **suy ra** từ sổ cái, cập nhật trong cùng giao dịch, có `version` cho optimistic locking và ràng buộc `qtyDispensed ≤ qtyPrescribed`. |
| **C. Event sourcing toàn phần** | Không lưu trạng thái; đơn là chuỗi sự kiện (Created, Issued, Dispensed…), trạng thái hiện tại dựng lại bằng cách phát lại sự kiện; báo cáo đọc từ các projection. |

## 3. Tiêu chí và chấm điểm (1–5, cao là tốt)
| Tiêu chí | Trọng số | A | B | C |
|---|---|---|---|---|
| Giữ nguyên lịch sử, không ghi đè nội dung đã ký (PR-05, CON-03) | 25% | 2 | 5 | 5 |
| Chống cấp trùng, đối soát được (NFR-DAT-01, RSK-04) | 25% | 2 | 5 | 5 |
| Độ phức tạp với nhóm nhỏ, thời gian ngắn (CON-07) | 20% | 5 | 3 | 1 |
| Truy vấn và báo cáo dễ (FR-11) | 15% | 5 | 4 | 2 |
| Truy vết: trả lời "ai đổi gì, khi nào" (NFR-SEC-03) | 15% | 3 | 4 | 5 |
| **Tổng có trọng số** | 100% | **3,20** | **4,30** | **3,75** |

Giải thích:
- A dễ nhất nhưng UPDATE tại chỗ làm hai bản ghi cấp đến cùng lúc có thể ghi đè nhau (lost update); trigger lịch sử có thể bị tắt bởi quản trị CSDL nên không đủ làm bằng chứng.
- C mạnh nhất về truy vết nhưng đòi hỏi projection, phát lại, xử lý thay đổi cấu trúc sự kiện: quá sức nhóm trong 5 tuần và khó giải thích khi bảo vệ.
- B lấy phần cốt lõi của C (chỉ thêm, không sửa) cho đúng hai chỗ cần (nội dung đơn, sổ cái cấp) và giữ bảng trạng thái quen thuộc cho truy vấn.

## 4. Quyết định
Chọn **B**. Quy tắc cứng:
1. Nội dung đơn ISSUED không UPDATE; chỉ cột trạng thái/số lượng suy ra được đổi, trong cùng giao dịch với INSERT sổ cái.
2. `dispense_record.dispenseId` UNIQUE; nhận lại cùng `dispenseId` → trả kết quả cũ.
3. Ràng buộc CSDL `qty_dispensed ≤ qty_prescribed` theo từng dòng thuốc; vi phạm → 409, ghi sự kiện đối soát.
4. Mọi thay đổi phát `DO-OutboxEvent` (ADR-001) và `DO-AuditEvent` (ADR-003).

## 5. Đánh đổi
- **Được:** không thể cấp vượt số kê dù đồng bộ lặp; lịch sử đơn đầy đủ để chứng minh; báo cáo vẫn dùng SQL thường.
- **Mất:** bảng tăng nhanh hơn CRUD; lập trình viên phải tuân thủ quy tắc "chỉ thêm" (cần review); trạng thái suy ra có thể lệch nếu ai đó sửa tay CSDL → chạy job đối chiếu hằng đêm.

## 6. Rủi ro và giảm thiểu
- RSK-04: ràng buộc CSDL là lớp chặn cuối cùng, không phụ thuộc code ứng dụng.
- Lệch trạng thái suy ra: job đối chiếu tổng `dispense_line` với `qty_dispensed`, lệch thì báo AC-Audit.

## 7. Phần tử ArchiMate bị ảnh hưởng
DO-Prescription, DO-PrescriptionItem, DO-DispenseRecord, DO-OutboxEvent; AF-ManagePrescriptionState (AC-ePrescription); AS-RecordDispense; ART-erx-db (TV3).

## 8. Điều chỉnh theo biến thể
- **B:** bản ghi cấp offline mang `source = OFFLINE_SYNC` và giờ cấp tại nhà thuốc; khi đồng bộ, mỗi bản ghi được: ACCEPTED (hợp lệ), DUPLICATE (trùng `dispenseId`, bỏ qua), CONFLICT (vượt số lượng còn lại → đưa vào hàng đối soát cho BR-QuanLy và dược sĩ). Thứ tự xử lý theo thời điểm server nhận, **không** theo đồng hồ nhà thuốc (đồng hồ offline không tin được). Nhờ ASSUMP-10 (một đơn chỉ giao một nhà thuốc), xung đột chỉ xảy ra trong nội bộ một nhà thuốc nên hiếm.
- **C:** thêm `DO-PrescriptionVersion` (thực chất là dòng prescription có `version`, `supersedes`) và `DO-AmendmentReason` (lý do, người duyệt, chữ ký). Đơn đã cấp một phần không bị thu hồi ngược: phần đã cấp giữ nguyên, phần còn lại đóng (`CLOSED_BY_REVOCATION`) và nếu cần kê đơn mới.
- **A:** không đổi mô hình đơn; thêm DO-PatientLink và DO-CodeMapping ở AC-MPI.

## 9. Điều kiện xem xét lại
- Pháp luật yêu cầu dựng lại toàn bộ lịch sử thao tác ở mức sự kiện cho mọi đối tượng: chuyển dần sang C.
- Bỏ ASSUMP-10 (mọi nhà thuốc nhận cùng một đơn): xung đột giữa các nhà thuốc trở nên thường xuyên, cần cơ chế "giữ chỗ" (claim) đơn trước khi cấp.
