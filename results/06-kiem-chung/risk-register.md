# Danh mục rủi ro (Risk Register) — TV3, bản nháp v0.1 (2026-11-03)

> Thang điểm: Xác suất (X) và Tác động (T) từ 1 (rất thấp) đến 5 (rất cao); **Mức = X × T** (≥ 15 Cao, 8–14 Trung bình, ≤ 7 Thấp).
> Chiến lược ứng phó: Tránh / Giảm thiểu / Chuyển giao / Chấp nhận. "Còn lại" là mức ước tính sau khi áp đối sách.
> Mỗi rủi ro gắn với phần tử kiến trúc, ADR và Work Package để truy vết (quy tắc nhất quán của nhóm).
> Chủ sở hữu: ghi cả vai trò trong tổ chức (người xử lý thật) và thành viên nhóm (người viết/bảo vệ).

| ID | Rủi ro (nguyên nhân → sự kiện → hậu quả) | X | T | Mức | Dấu hiệu sớm | Ứng phó | Đối sách | Liên kết | Còn lại | Chủ sở hữu |
|---|---|---|---|---|---|---|---|---|---|---|
| RSK-01 | Tài khoản bị chiếm hoặc nhân viên lạm quyền → hồ sơ sức khỏe bị xem/rò rỉ → vi phạm Luật BVDLCN, mất uy tín | 3 | 5 | **15** | Đăng nhập lạ, một người đọc nhiều hồ sơ, break-glass dày | Giảm thiểu | MFA, xóa tài khoản chung, RBAC+ABAC (POL-01/02), cảnh báo SIEM, mã hóa khi lưu/truyền, đào tạo, quy trình thông báo vi phạm | ADR-002, ADR-003; NFR-SEC-01..04; WP-02, WP-08 | 2×5 = 10 | DPO / TV3 |
| RSK-02 | Nhật ký bị sửa, xóa hoặc mất (quản trị viên, lỗi hàng đợi) → không chứng minh được ai đã truy cập → mất giá trị bằng chứng, không đạt OC-03 | 2 | 5 | 10 | Verify chuỗi băm báo lệch, outbox tồn đọng | Giảm thiểu | Chuỗi băm + checkpoint ký số + WORM + bản sao DR; outbox cùng giao dịch; verify tự động hằng ngày; tách quyền quản trị | ADR-003; NFR-SEC-03/05; WP-02 | 1×5 = 5 | Trưởng CNTT / TV3 |
| RSK-03 | Mất kết nối (Internet cơ sở, VPN, nhà thuốc đối tác) → không tra cứu/gửi đơn được → BN chờ, quay về giấy | 4 | 3 | 12 | Cảnh báo đường truyền, tỉ lệ lỗi gọi API đối tác tăng | Giảm thiểu | 2 nhà mạng + 4G, hàng đợi bền + thử lại, BN có mã đơn/QR tra trên hệ thống quốc gia, quy trình giấy dự phòng; biến thể B: agent offline | technology.md mục 6; NFR-AVL-01; WP-01, WP-05, WP-06B | 2×3 = 6 | Trưởng CNTT / TV3 (biến thể B: TV2 cùng xử lý) |
| RSK-04 | Đồng bộ lặp hoặc đơn đã đổi/thu hồi → cấp thuốc trùng hoặc cấp theo đơn cũ → nguy hại người bệnh | 2 | 5 | 10 | Đối soát phát hiện 2 bản ghi cấp cho 1 dòng thuốc | Giảm thiểu | Idempotency key, ràng buộc duy nhất, trạng thái đơn chặn cấp (POL-05), đẩy sự kiện đổi đơn có xác nhận, không cấp offline thuốc kiểm soát (CON-04) | NFR-DAT-01; ADR-001, ADR-004 (TV2); POL-05/06; WP-05, WP-06 | 1×5 = 5 | Trưởng dược / TV2 |
| RSK-05 | Ghép sai/trùng định danh BN khi gộp dữ liệu 2 cơ sở → bác sĩ xem nhầm hồ sơ → sai điều trị, lộ dữ liệu người khác | 3 | 4 | 12 | Tỉ lệ bản ghi nghi trùng cao khi chạy thử gộp | Giảm thiểu | Định danh chính bằng CCCD gắn chip (DV-IdCardReader), gộp có người xác nhận khi không chắc, không tự gộp dưới ngưỡng tin cậy; biến thể A: MPI | WP-07, WP-06A; FR-03, FR-A1 | 2×4 = 8 | Trưởng tiếp đón / TV2 |
| RSK-06 | Quá tải giờ cao điểm hoặc sự cố vùng DC → hệ thống chậm/ngừng → hàng chờ tăng, ngược mục tiêu G-01 | 2 | 4 | 8 | p95 > 1,5 s, CPU > 70% lúc 7h–10h | Giảm thiểu | Scale ngang, read replica, rate limit đối tác, kiểm thử tải trước PLT-2, DR vùng 2 + diễn tập quý | NFR-PRF-01, NFR-AVL-01; WP-01 | 1×4 = 4 | Trưởng CNTT / TV3 |
| RSK-07 | Hệ thống cũ (HIS-Lite, ClinicSoft) khó tích hợp, nhà cung cấp không hợp tác, chạy song song kéo dài → trễ lộ trình, nhập liệu 2 lần | 4 | 3 | 12 | Nhà cung cấp chậm trả lời đặc tả, tỉ lệ lệch dữ liệu khi đối soát song song | Giảm thiểu + Chuyển giao | Chỉ kết nối tối thiểu (thu ngân/BHYT giữ nguyên, ASSUMP-06), lấy dữ liệu qua xuất file/adapter ở phía DC (không sửa phần mềm cũ, CON-06), điều khoản hợp đồng hỗ trợ tích hợp, giới hạn song song ≤ 4 tuần/cơ sở | WP-03, WP-07; SH-11 | 3×2 = 6 | Giám đốc / TV2 |
| RSK-08 | Bác sĩ, dược sĩ không chấp nhận (MFA phiền, kê đơn lâu hơn, bị chặn nhầm) → làm đường vòng (dùng chung máy đang đăng nhập, quay lại giấy) | 3 | 4 | 12 | Thời gian kê đơn > 90 s, nhiều break-glass "cho nhanh", phản ánh | Giảm thiểu | Thiết kế cùng bác sĩ đại diện, SSO + đăng nhập bằng thẻ/khóa trên máy trạm, tự khóa màn hình khi rời, ABAC chế độ quan sát 2 tuần trước khi chặn, đào tạo theo vai trò, pilot từng cơ sở | NFR-USB-01; ADR-002 mục 6; WP-08 | 2×3 = 6 | Giám đốc chuyên môn / TV1 |

## Bản đồ nhiệt (trước đối sách)

| X \ T | 3 | 4 | 5 |
|---|---|---|---|
| **4** | RSK-03, RSK-07 | | |
| **3** | | RSK-05, RSK-08 | RSK-01 |
| **2** | | RSK-06 | RSK-02, RSK-04 |

## Ghi chú khi bảo vệ

- Rủi ro cao nhất là **RSK-01** (lộ dữ liệu) nên WP-02 nằm ngay PLT-1 và không có dữ liệu sức khỏe nào lên hệ thống mới trước khi IAM + audit chạy.
- Rủi ro theo biến thể: A → RSK-05 tăng (X=4); B → RSK-03, RSK-04 tăng (B là trọng tâm); C → RSK-04 tăng (cấp theo đơn đã thu hồi). Khi biết biến thể, nâng X tương ứng và chép đối sách chi tiết từ ADR của TV2.
- Ví dụ "thay đổi giả định": nhà thuốc mất kết nối 48 giờ → RSK-03 X=5, RSK-04 X=3 → xem lại hạn mức cấp offline và thời gian giữ hàng đợi (≥ 72 giờ đã đủ).
