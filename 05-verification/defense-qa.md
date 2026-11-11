# Chuẩn bị bảo vệ — câu hỏi dự kiến theo thành viên (v1.0, 2026-11-04)

> Đề: "từng thành viên trả lời câu hỏi, bao gồm một thay đổi giả định do giảng viên đưa ra" (15 điểm cá nhân). Mỗi câu trả lời nên đi theo khung **Yêu cầu/ràng buộc nào → phần tử nào trong mô hình → ADR nào → đánh đổi**. Chỗ tra cứu ghi ở cột cuối.

## Câu chung (ai cũng phải trả lời được)

| Câu hỏi | Ý trả lời (≤ 30 giây) | Tra |
|---|---|---|
| Kiến trúc này giải quyết vấn đề gì lớn nhất? | Chuỗi giấy + phần mềm rời rạc → một hồ sơ, đơn điện tử có kiểm tra an toàn, một cổng tới nhà thuốc, phân quyền ngữ cảnh + audit bất biến | Báo cáo ch.12 |
| Vì sao kê đơn điện tử lên trước đặt lịch? | TT 26/2025 bắt buộc từ 01/01/2026, CS2 đang vi phạm; và bảo mật/audit phải có trước khi đưa dữ liệu sức khỏe lên hệ thống mới (PR-04, RSK-01) | `gap-roadmap.md` 3.1, COA-01 |
| Chọn 1 yêu cầu, truy vết từ Goal tới hạ tầng | G-02 → FR-05 → CAP-04 → BP-04.2 → AS-CheckDrugSafety → AC-ePrescription → ART-erx-svc → ND-AppCluster; ký số TS-Signing → CON-03 | View V-LAY-1, `rtm.md` |
| Đã kiểm chứng tình huống bất thường nào? | Hệ thống đơn thuốc quốc gia ngừng 2 giờ: vẫn phát hành đơn, outbox gửi bù, không trùng, audit hợp lệ — 7/7 bước đạt | `change-scenario.md` mục 1 |

## TV1 — Bối cảnh, Motivation, Chiến lược, Nghiệp vụ, BPMN

| Câu hỏi | Ý trả lời | Tra |
|---|---|---|
| Goal và Outcome khác nhau thế nào? | Goal là phát biểu định hướng (G-01 giảm chờ); Outcome là kết quả đo được (OC-01 ≤ 45 phút sau 6 tháng). Con số đặt vào Goal là lỗi ký pháp | catalog §4 |
| Capability khác Business Function? | Capability là "làm được gì" phục vụ hoạch định (CAP-04 Kê đơn an toàn); Function là công việc thực tế theo tổ chức. BP-04 *realizes* CAP-04 | V-STR-1, V-STR-2 |
| Vì sao 2 cơ sở chứ không 3 như hướng dẫn? | Giữ đúng ràng buộc biến thể A (hai nguồn dữ liệu khác cấu trúc); đề cấm giả định làm mất ràng buộc chính | TV1 mục 0 |
| BPMN-01 có mấy pool, vì sao BHXH là pool đóng? | Tổ chức khác → pool riêng, nối bằng message flow; không mô hình hóa bên trong | BPMN-01 |
| *Thay đổi giả định:* thêm dịch vụ khám từ xa | Thêm BS mới + kênh BI video, BP-02 có nhánh check-in online; CAP-01/02 mở rộng; ADR-002 cần POL cho phiên từ xa | — |

## TV2 — Ứng dụng, Dữ liệu, ADR-001, ADR-004

| Câu hỏi | Ý trả lời | Tra |
|---|---|---|
| Flow và Serving khác nhau? | Flow: dữ liệu chảy theo sự kiện (AC-ePrescription ⇢ AC-PharmacyGateway); Serving: gọi dịch vụ (AC-EMR → AC-ePrescription) | V-APP-1 |
| Outbox giải quyết gì? | "Ghi đơn thành công thì sự kiện chắc chắn được phát": đơn + DO-OutboxEvent cùng giao dịch; at-least-once + idempotency = hiệu quả đúng một lần | ADR-001 §4 |
| Vì sao không cho nhà thuốc đọc CSDL chung? | Trái PR-08, khó phân quyền theo nhà thuốc, lô 15 phút vi phạm OC-04 (phương án C 2,90 điểm) | ADR-001 §3 |
| Đơn đã cấp một phần rồi sửa thì sao? | Không UPDATE; tạo v+1 `supersedes`, số đã cấp chuyển sang v2, cảnh báo nếu BN nhận thừa | ADR-004, mock `/amend` |
| *Thay đổi giả định:* bỏ ASSUMP-10 (mọi nhà thuốc cùng nhận 1 đơn) | Sổ cái vẫn đúng; thêm khóa theo dòng thuốc, đối soát chéo nhà thuốc; RSK-04 tăng | `change-scenario.md` §3 |

## TV3 — Công nghệ, ADR-002, ADR-003, lộ trình, rủi ro, prototype

| Câu hỏi | Ý trả lời | Tra |
|---|---|---|
| Vì sao RBAC + ABAC mà không RBAC thuần? | RBAC không biểu diễn "BN đang khám của tôi" (POL-01); ABAC thuần thì quyền đơn giản cũng thành quy tắc. B đạt 4,50 | ADR-002 |
| Ngoài giờ trực có chặn không? | Không chặn cứng (PR-01, cấp cứu): chỉ đọc, không ký đơn (POL-03); khẩn cấp dùng break-glass 4 giờ, DPO rà soát 24 giờ | ADR-002 POL-03/07 |
| Làm sao chứng minh log không bị sửa? | Chuỗi băm từng bản ghi, checkpoint ký bằng KMS mỗi giờ, phân đoạn cũ WORM; demo sửa 1 bản ghi → verify chỉ đúng chỗ | ADR-003, prototype S5 |
| SIEM có thay audit store được không? | Không: SIEM chỉ nhận bản sao để phát hiện bất thường, không phải nguồn bằng chứng | ADR-003 §4 |
| Gap trong ArchiMate nối với gì? | Association với 2 Plateau; Work Package lấp Gap | V-MIG-1, V-MIG-3 |
| *Thay đổi giả định:* tải tăng ×5 / thêm cơ sở 3 | Scale ngang 3→4+ VM, read replica, phân vùng audit theo tháng; không mở lại ADR; thêm WP-09 | `change-scenario.md` §2 |

## Câu theo biến thể ⟦giữ đúng biến thể được giao⟧

| Biến thể | Câu dễ bị hỏi | Ý trả lời |
|---|---|---|
| A | Ghép định danh sai thì sao? | Tất định theo CCCD/BHYT; dưới ngưỡng tin cậy → xác minh thủ công, không tự gộp (RSK-05) |
| B | Hai quầy offline cùng cấp một đơn? | Không tin đồng hồ máy offline; xử lý theo thứ tự server nhận, vượt số → CONFLICT → đối soát thủ công; thuốc kiểm soát không cấp offline (CON-04) |
| C | Thu hồi đơn đã cấp? | 409, không xóa lịch sử; lập đơn điều chỉnh, nhà thuốc phải ack, quá 30 phút liên hệ trực tiếp |
