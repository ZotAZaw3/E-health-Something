# Rà soát file hướng dẫn (phần TV3) — những chỗ đã sửa khi làm bài

> File hướng dẫn chỉ để tham khảo. Dưới đây là các điểm TV3 thấy chưa đúng, chưa đủ hoặc lệch với bài giảng, và cách bài nhóm đã xử lý. Ngày rà: 2026-11-03.

| # | Hướng dẫn viết | Vấn đề | Cách bài làm xử lý |
|---|---|---|---|
| 1 | Ràng buộc pháp lý chỉ nêu chung "quy định bảo mật dữ liệu sức khỏe" | Thiếu căn cứ cụ thể; hội đồng có thể hỏi | Nêu văn bản cụ thể ở `technology.md` mục 7: Luật BVDLCN 91/2025/QH15 + NĐ 356/2025, TT 26/2025/TT-BYT (kê đơn điện tử), TT 13/2025/TT-BYT (bệnh án điện tử), Luật KBCB 2023. Nhóm cần tự kiểm tra lại trên cổng văn bản trước khi nộp |
| 2 | Baseline giả định "đơn giấy", lộ trình đặt Booking là WP1 | Theo TT 26/2025, kê đơn điện tử đã bắt buộc với mọi cơ sở KCB từ 01/01/2026, nên ở thời điểm 11/2026 "chưa có đơn điện tử" là **vi phạm**, không phải chỉ là điểm yếu | Roadmap đặt **bảo mật + kê đơn điện tử liên thông lên PLT-1**, đặt lịch/tiếp đón sang PLT-2 (`gap-roadmap.md` mục 3.1) |
| 3 | Tên góc nhìn "Technology/Deployment View" | Bài giảng Ch.5 và Ch.8 dùng tên khác | Dùng đúng tên bài giảng: Hạ tầng, Sử dụng hạ tầng, Thực hiện và triển khai; Dự án, Dịch chuyển, Thực hiện và dịch chuyển (file Archi có 7 view TV3-01…07) |
| 4 | Gap phân loại New/Replace/Retain/Eliminate trong 1 bảng | Chưa thể hiện ma trận Baseline × Target của TOGAF; chưa nói Gap trong ArchiMate là phần tử nối **2 bình cảnh** | Bảng theo từng tầng + 3 phần tử GAP-01..03 nối PLT-0→1→2→3, mỗi Gap có WP lấp |
| 5 | Quy ước mã: Goal `G-xx`, chưa có mã cho Gap, Artifact; ví dụ trộn `TS-API Gateway`, `ADR-A1`, `ADR-00x` | Trùng/thiếu nhất quán | Gap dùng `GAP-xx`, Artifact dùng `ART-` (vì `AF-` là Application Function của TV2), ADR đánh số liên tục ADR-001…004 |
| 6 | ABAC ví dụ "ngoài giờ trực → chặn" | Trái nguyên tắc PR-01 (an toàn người bệnh trên hết): chặn cứng có thể cản cấp cứu | Ngoài ca: chỉ đọc, không ký đơn (POL-03); khẩn cấp: break-glass có lý do, 4 giờ, DPO rà soát 24 giờ (POL-07) |
| 7 | Audit "append-only, có băm chuỗi" | Chưa nói: phải ghi cả **đọc** và **bị từ chối**; không ghi nội dung y tế vào log; xử lý khi audit hỏng; SIEM không phải kho bằng chứng | ADR-003 mục 4: outbox cùng giao dịch, fail-closed với đọc thường nhưng vẫn cho break-glass, checkpoint ký số + WORM, SIEM chỉ nhận bản sao |
| 8 | Mock API trả "200/409/503" | Thiếu mã đúng ngữ nghĩa | 403 cho từ chối quyền (kèm `policyId`), 422 cho cảnh báo an toàn/dữ liệu sai, 409 cho xung đột trạng thái, 200 cho gửi lặp idempotent, 201 khi tạo mới |
| 9 | Biến thể B: "quy tắc xung đột: ai cấp trước theo timestamp + chữ ký" | Đồng hồ thiết bị offline không tin được, lấy timestamp nhà thuốc để phân xử là sai | Theo ADR-004 (TV2): xử lý theo thứ tự server nhận, vượt số lượng → CONFLICT → đối soát thủ công; mock `/pharmacy/sync` minh họa |
| 10 | Biến thể C: "đã cấp → chỉ lập đơn bổ sung" | Đúng hướng nhưng thiếu: phiên bản mới phải **trừ phần đã cấp** để không cấp lại, và cảnh báo khi BN đã nhận thừa | Mock `/prescriptions/{id}/amend` chuyển số đã cấp sang v2 và trả cảnh báo |
| 11 | Risk register chỉ có Xác suất/Tác động/Đối sách/Chủ sở hữu (tên thành viên) | Thiếu điểm mức rủi ro, dấu hiệu sớm, rủi ro còn lại, liên kết ADR/WP; chủ sở hữu thật phải là vai trò trong tổ chức | `risk-register.md`: X×T, dấu hiệu, chiến lược, còn lại, liên kết, chủ sở hữu = vai trò tổ chức / thành viên nhóm |
| 12 | Prototype UI bằng Figma | Figma chỉ là ảnh, dễ lệch với API | Giao diện HTML bấm thử gọi thẳng mock API (`04-prototype/`); Figma không bắt buộc |
| 13 | RTM mẫu dùng `NFR-03` | Mã đã đổi | Dùng `NFR-SEC-03` theo catalog TV1 |
| 14 | Câu hỏi "tăng ×5" gợi ý "ADR monolith vs services" | Bài không có ADR này | Trả lời bằng scale ngang cụm ứng dụng, read replica, phân vùng audit theo tháng (`technology.md` mục 3.5, RSK-06) |
| 15 | Catalog TV1 (CON-02) ghi "NĐ 13/2023" | NĐ 13/2023 đã được thay bởi khung Luật BVDLCN 2025 + NĐ 356/2025 (cần kiểm tra lại) | Đã báo TV1 cập nhật |
