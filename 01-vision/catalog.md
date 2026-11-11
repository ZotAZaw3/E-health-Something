# Danh mục tên/mã chung – Motivation & Business (TV1) – v0.1 (2026-11-03)

> Nguồn sự thật cho: giả định tổ chức, SH, DRV, ASM, G, OC, PR, FR, NFR, CON, tầng Business (BA/BR/BS/BI/BP/BE/BO/CT).
> TV2 sở hữu AC/AS/AI/DO (xem `02-models/app-catalog.md`), TV3 sở hữu ND/TS/WP/PLT/RSK.
> Trong Archi đặt tên phần tử = "<mã> <tên VN>", ví dụ "BP-04 Kê đơn điện tử". Mã có hậu tố A/B/C chỉ dùng khi biết biến thể.

## 1. Giả định tổ chức (ASSUMP)
| Mã | Giả định |
|---|---|
| ASSUMP-01 | Tổ chức: **Phòng khám Đa khoa An Tâm** (hư cấu), tư nhân, có ký hợp đồng KCB BHYT. |
| ASSUMP-02 | **2 cơ sở**: CS1 (Cầu Giấy, ~300 lượt khám/ngày), CS2 (Long Biên, ~200 lượt/ngày). Tổng ~500 lượt/ngày, cao điểm 7h–10h chiếm ~45%. |
| ASSUMP-03 | ~40 bác sĩ, 30 điều dưỡng, 12 lễ tân/thu ngân, 10 chuyên khoa ngoại trú; không có nội trú. |
| ASSUMP-04 | Mỗi cơ sở có 1 nhà thuốc nội bộ; thêm **6 nhà thuốc đối tác** bên ngoài, mỗi nhà thuốc dùng phần mềm bán thuốc riêng (không bắt buộc đổi). |
| ASSUMP-05 | Hiện trạng phần mềm: CS1 dùng **HIS-Lite** (thu ngân, BHYT, in đơn); CS2 dùng **ClinicSoft** (nhà cung cấp khác, cấu trúc dữ liệu và mã bệnh nhân khác); đặt lịch qua hotline/Zalo OA ghi vào Google Sheet; bệnh án ngoại trú chủ yếu giấy; tài khoản phần mềm dùng chung theo quầy. |
| ASSUMP-06 | Thanh toán viện phí và giám định BHYT **giữ hệ thống hiện có** (Retain), chỉ kết nối; không thuộc phạm vi thiết kế lại. |
| ASSUMP-07 | Hệ thống ngoài (Cổng giám định BHYT, Hệ thống đơn thuốc quốc gia, SMS, phần mềm nhà thuốc, CA ký số) được **mock**. |
| ASSUMP-08 | Ngân sách & thời gian chuyển đổi: 12 tháng, 3 giai đoạn (Plateau do TV3 đặt mã). |
| ASSUMP-09 | Số liệu hiện trạng (thời gian chờ, tỷ lệ sai sót) là **giả định có chủ đích** để đặt mục tiêu đo được, ghi rõ trong báo cáo. |
| ASSUMP-10 | Mỗi đơn thuốc tại một thời điểm chỉ được giao cho **một** nhà thuốc (nhà thuốc nội bộ hoặc 1 đối tác do BN chọn); muốn đổi nhà thuốc phải "trả đơn" về trạng thái chưa giao. Đề xuất bởi TV2 (ADR-004), nhóm thống nhất 2026-11-04. |

## 2. Stakeholder (SH)
| Mã | Stakeholder | Mối quan tâm chính | Power / Interest |
|---|---|---|---|
| SH-01 | Bệnh nhân | Chờ ít, đặt lịch dễ, nhận thuốc đúng, dữ liệu được bảo vệ | Thấp / Cao → Keep informed |
| SH-02 | Ban Giám đốc phòng khám | Công suất, chi phí, uy tín, tuân thủ | Cao / Cao → Manage closely |
| SH-03 | Bác sĩ | Kê đơn nhanh, an toàn, xem đủ tiền sử | Cao / Cao → Manage closely |
| SH-04 | Điều dưỡng | Điều phối hàng chờ, đo sinh hiệu | Thấp / Trung bình → Keep informed |
| SH-05 | Lễ tân / Thu ngân | Tiếp đón nhanh, ít nhập liệu trùng | Thấp / Cao → Keep informed |
| SH-06 | Dược sĩ (nhà thuốc nội bộ & đối tác) | Nhận đơn hợp lệ, không cấp trùng, ít đổi phần mềm | Trung bình / Cao → Keep satisfied+informed |
| SH-07 | Phòng CNTT | Vận hành, tích hợp, bảo mật | Trung bình / Cao → Manage closely |
| SH-08 | Pháp chế / Phụ trách bảo vệ dữ liệu (DPO) | Tuân thủ dữ liệu cá nhân, lưu vết | Cao / Trung bình → Keep satisfied |
| SH-09 | Sở Y tế / Bộ Y tế (cơ quan quản lý) | Kê đơn điện tử, liên thông đơn thuốc, báo cáo | Cao / Thấp → Keep satisfied |
| SH-10 | BHXH (cơ quan giám định BHYT) | Dữ liệu KCB BHYT đúng chuẩn | Cao / Thấp → Keep satisfied |
| SH-11 | Nhà cung cấp phần mềm hiện tại (HIS-Lite, ClinicSoft) | Giữ hợp đồng, phạm vi tích hợp | Thấp / Trung bình → Monitor |

## 3. Driver (DRV) & Assessment (ASM)
| Mã | Driver | Assessment liên quan |
|---|---|---|
| DRV-01 | Quá tải giờ cao điểm, thời gian chờ dài | ASM-01: chờ TB 70 phút từ lúc đến tới lúc gặp bác sĩ (7h–10h); 60% BN đến không hẹn |
| DRV-02 | Sai sót đơn thuốc giấy/không kiểm tra an toàn | ASM-02: ~3% đơn phải sửa (chữ khó đọc, trùng hoạt chất, quên dị ứng); không có cảnh báo tương tác |
| DRV-03 | Quy định kê đơn điện tử và liên thông đơn thuốc | ASM-03: CS2 chưa kê đơn điện tử/liên thông (trái TT 26/2025 từ 01/01/2026); CS1 liên thông thủ công, chậm |
| DRV-04 | Bảo vệ dữ liệu cá nhân/sức khỏe, yêu cầu lưu vết | ASM-04: tài khoản dùng chung theo quầy, không có log truy cập hồ sơ |
| DRV-05 | Nhu cầu kết nối nhà thuốc đối tác (BN mua thuốc ngoài) | ASM-05: nhà thuốc nhận đơn giấy/ảnh chụp, không xác thực, không phản hồi trạng thái cấp |
| DRV-06 | Hồ sơ phân tán giữa 2 cơ sở và giấy | ASM-06: BN khám ở 2 cơ sở có 2 mã khác nhau, bác sĩ không xem được tiền sử bên kia |

## 4. Goal (G) & Outcome (OC)
| Mã | Goal | Outcome đo được (realizes Goal) |
|---|---|---|
| G-01 | Giảm thời gian chờ khám | OC-01: thời gian chờ TB ≤ 45 phút (giảm ≥ 35%) sau 6 tháng vận hành; ≥ 60% lượt khám có hẹn trước |
| G-02 | Nâng cao an toàn kê đơn | OC-02: 100% đơn ngoại trú (trừ thuốc kiểm soát đặc biệt) là đơn điện tử có kiểm tra an toàn; tỷ lệ đơn phải sửa ≤ 0,5% |
| G-03 | Bảo đảm bảo mật, tuân thủ và truy vết | OC-03: 100% truy cập hồ sơ/đơn có log bất biến; 0 tài khoản dùng chung; báo cáo tuân thủ xuất được trong ≤ 1 ngày |
| G-04 | Liên thông đơn thuốc với nhà thuốc và hệ thống quốc gia | OC-04: ≥ 95% đơn được đẩy liên thông trong ≤ 5 phút; ≥ 90% đơn tại nhà thuốc đối tác nhận qua kênh điện tử |
| G-05 | Hồ sơ bệnh nhân thống nhất, dùng lại được | OC-05: mỗi BN có 1 hồ sơ điện tử dùng chung; không nhập lại thông tin hành chính khi tái khám |

## 5. Architecture Principles (PR)
| Mã | Tên | Phát biểu ngắn |
|---|---|---|
| PR-01 | An toàn người bệnh trên hết | Khi phải đánh đổi, chọn phương án an toàn người bệnh (fail-safe) trước tiện lợi/sẵn sàng |
| PR-02 | Dữ liệu là tài sản, có chủ sở hữu | Dữ liệu lâm sàng do cơ sở khám quản lý; mỗi Data Object có chủ sở hữu và nguồn chuẩn duy nhất |
| PR-03 | Tối thiểu quyền, đúng ngữ cảnh | Chỉ truy cập dữ liệu cần cho công việc, với BN đang phục vụ (RBAC + ABAC) |
| PR-04 | Mọi truy cập đều để lại vết | Ai–làm gì–trên đối tượng nào–khi nào–từ đâu–kết quả, ghi bất biến |
| PR-05 | Không ghi đè dữ liệu lâm sàng | Thay đổi tạo phiên bản/bản ghi mới, giữ lịch sử |
| PR-06 | Ưu tiên chuẩn mở | HL7 FHIR R4, ICD-10, mã thuốc theo danh mục quốc gia cho trao đổi dữ liệu |
| PR-07 | Nhập một lần, dùng nhiều nơi | Dữ liệu hành chính/lâm sàng nhập tại nguồn, các bước sau dùng lại |
| PR-08 | Kết nối lỏng qua giao diện | Hệ thống nội bộ và đối tác giao tiếp qua API/sự kiện, không truy cập DB của nhau |

## 6. Requirements – FR
| Mã | Yêu cầu chức năng | Goal | BP |
|---|---|---|---|
| FR-01 | Đặt lịch khám trực tuyến/qua tổng đài: chọn chuyên khoa, bác sĩ, khung giờ; xác nhận tức thì | G-01 | BP-01 |
| FR-02 | Nhắc lịch, hủy/đổi lịch; giải phóng khung giờ | G-01 | BP-01 |
| FR-03 | Check-in (QR lịch hẹn hoặc CCCD), xác minh danh tính và thẻ BHYT, mở lượt khám, xếp hàng chờ | G-01, G-05 | BP-02 |
| FR-04 | Xem tiền sử, dị ứng, đơn cũ; ghi nhận khám và chẩn đoán ICD-10 vào hồ sơ điện tử | G-02, G-05 | BP-03 |
| FR-05 | Kê đơn điện tử có kiểm tra dị ứng, tương tác, trùng hoạt chất, liều; ký số và phát hành mã đơn | G-02 | BP-04 |
| FR-06 | Gửi đơn liên thông lên Hệ thống đơn thuốc quốc gia và tới nhà thuốc; BN nhận mã đơn (SMS/app/bản in có QR) | G-04 | BP-04 |
| FR-07 | Nhà thuốc tra cứu đơn theo mã, ghi nhận cấp thuốc toàn phần/một phần, cập nhật trạng thái đơn | G-04 | BP-05 |
| FR-08 | Phân quyền theo vai trò và ngữ cảnh (BN đang khám, cơ sở, ca trực); truy cập khẩn cấp (break-glass) có cờ | G-03 | BF-01 |
| FR-09 | Ghi và tra cứu nhật ký truy cập; báo cáo truy cập bất thường | G-03 | BF-01 |
| FR-10 | Thông báo cho BN: xác nhận/nhắc lịch, đơn đã phát hành, trạng thái cấp thuốc | G-01, G-04 | BP-01, BP-04, BP-05 |
| FR-11 | Báo cáo vận hành: thời gian chờ, số lượt, tỷ lệ đơn điện tử/đơn phải sửa (đo Outcome) | G-01, G-02 | BF-02 |

Theo biến thể (chỉ giữ nhánh được giao; nhánh khác dùng cho phần "thay đổi giả định"):
| Mã | Yêu cầu | Goal | BP |
|---|---|---|---|
| FR-A1 | Ghép định danh BN giữa CS1/CS2 (CCCD/BHYT + đối chiếu), xác minh thủ công khi không chắc | G-05 | BP-06A |
| FR-A2 | Xem hồ sơ liên cơ sở qua mô hình dữ liệu chuẩn mà không buộc 2 cơ sở đổi hệ thống | G-05 | BP-03, BP-06A |
| FR-A3 | Ghi nhận/kiểm tra đồng ý (consent) của BN khi xem hồ sơ cơ sở kia | G-03 | BP-06A |
| FR-B1 | Nhà thuốc cấp thuốc khi mất kết nối theo đơn đã nhận trước (cache), có giới hạn | G-04 | BP-06B |
| FR-B2 | Đồng bộ lại và đối chiếu bản ghi cấp thuốc với đơn gốc khi có kết nối | G-04 | BP-06B |
| FR-B3 | Phát hiện, chặn và xử lý cấp trùng; lưu vết đối soát | G-02, G-03 | BP-06B |
| FR-C1 | Sửa đơn sau phát hành tạo phiên bản mới, kèm lý do, chữ ký; không ghi đè | G-02, G-03 | BP-06C |
| FR-C2 | Thu hồi đơn theo trạng thái cấp (chưa cấp / cấp một phần / đã cấp) | G-02 | BP-06C |
| FR-C3 | Thông báo thay đổi đơn tới nhà thuốc và BN; nhà thuốc xác nhận đã nhận | G-04 | BP-06C |

## 7. Requirements – NFR (theo đề xuất mã của TV3)
| Mã | Yêu cầu phi chức năng | Goal |
|---|---|---|
| NFR-PRF-01 | p95 thời gian phản hồi API ≤ 2 s giờ cao điểm (300 người dùng đồng thời); tra cứu đơn tại nhà thuốc ≤ 3 s | G-01 |
| NFR-AVL-01 | Sẵn sàng 99,5% trong 6h–21h; RPO ≤ 15 phút, RTO ≤ 4 giờ | G-01, G-04 |
| NFR-SEC-01 | Xác thực mạnh: MFA cho nhân viên; OTP cho BN | G-03 |
| NFR-SEC-02 | Phân quyền RBAC + ABAC (đúng người, đúng BN đang khám, break-glass) | G-03 |
| NFR-SEC-03 | 100% truy cập hồ sơ/đơn được ghi audit bất biến (append-only, chống sửa) | G-03 |
| NFR-SEC-04 | Mã hóa khi truyền (TLS 1.2+, mTLS với đối tác) và khi lưu (AES-256) | G-03 |
| NFR-SEC-05 | Lưu audit ≥ 10 năm (không ngắn hơn thời hạn lưu hồ sơ bệnh án) | G-03 |
| NFR-INT-01 | Trao đổi dữ liệu lâm sàng/đơn theo HL7 FHIR R4 (Patient, Encounter, MedicationRequest, MedicationDispense) | G-04, G-05 |
| NFR-INT-02 | Thêm 1 nhà thuốc/cơ sở mới không phải sửa hệ thống lõi (chỉ cấu hình/adapter) | G-04 |
| NFR-DAT-01 | Không mất, không trùng đơn/bản ghi cấp thuốc (idempotent, có mã duy nhất) | G-02, G-04 |
| NFR-USB-01 | Bác sĩ kê 1 đơn 5 thuốc ≤ 90 s; lễ tân check-in 1 BN có hẹn ≤ 60 s | G-01 |

## 8. Constraint (CON)
| Mã | Ràng buộc | Ghi chú |
|---|---|---|
| CON-01 | Tuân thủ Luật Khám bệnh, chữa bệnh 2023 và quy định của Bộ Y tế về kê đơn điện tử, liên thông đơn thuốc, hồ sơ bệnh án điện tử | TT 26/2025/TT-BYT: kê đơn điện tử bắt buộc chậm nhất 01/01/2026 → ASM-03 là vi phạm hiện hành, ưu tiên PLT-1 |
| CON-02 | Tuân thủ quy định bảo vệ dữ liệu cá nhân (dữ liệu sức khỏe là dữ liệu nhạy cảm): cần căn cứ xử lý/consent, thông báo, lưu vết | Luật BVDLCN 91/2025/QH15 (hiệu lực 01/01/2026), NĐ 356/2025/NĐ-CP |
| CON-03 | Đơn thuốc và hồ sơ điện tử phải ký số hợp lệ | Luật Giao dịch điện tử 2023 |
| CON-04 | Thuốc gây nghiện/hướng thần/tiền chất kê và cấp theo quy định riêng: không cấp offline, không qua nhà thuốc đối tác thông thường | Liên quan PR-01 |
| CON-05 | Giữ hệ thống thu ngân/BHYT hiện có; kết nối Cổng giám định BHYT theo chuẩn BHXH | ASSUMP-06 |
| CON-06 | Không bắt buộc nhà thuốc đối tác (và CS2 với biến thể A) thay phần mềm nội bộ | ASSUMP-04/05 |
| CON-07 | 12 tháng, ngân sách hạn chế; ưu tiên dịch vụ đám mây trong nước/on-prem đạt yêu cầu lưu trữ dữ liệu | ASSUMP-08 |

## 9. Business layer (Target)
### 9.1 Actor (BA) & Role (BR)
| Mã | Tên | Loại |
|---|---|---|
| BA-BenhNhan | Bệnh nhân | Business Actor (ngoài) |
| BA-PhongKham | Phòng khám Đa khoa An Tâm | Business Actor (tổ chức), gồm BA-CS1, BA-CS2 |
| BA-NhaThuocDoiTac | Nhà thuốc đối tác | Business Actor (ngoài) |
| BA-NhaThuocNoiBo | Nhà thuốc nội bộ | Business Actor (trong) |
| BA-BHXH | Cơ quan BHXH | Business Actor (ngoài) |
| BA-CoQuanQuanLyDuoc | Bộ/Sở Y tế (quản lý dược) | Business Actor (ngoài) |
| BR-BenhNhan | Người bệnh | Business Role |
| BR-LeTan | Lễ tân | Business Role |
| BR-DieuDuong | Điều dưỡng | Business Role |
| BR-BacSi | Bác sĩ khám | Business Role |
| BR-DuocSi | Dược sĩ cấp thuốc | Business Role (gán cho cả nhà thuốc nội bộ và đối tác) |
| BR-QuanLy | Quản lý vận hành | Business Role |
| BR-QuanTriBaoMat | Quản trị bảo mật / DPO | Business Role |
| BC-KhamKeDon | Cộng tác Khám–Kê đơn (Bác sĩ + Điều dưỡng) | Business Collaboration |

### 9.2 Business Service (BS) & Interface (BI)
| Mã | Tên | Hiện thực bởi |
|---|---|---|
| BS-01 | Dịch vụ đặt lịch khám | BP-01 |
| BS-02 | Dịch vụ tiếp đón | BP-02 |
| BS-03 | Dịch vụ khám ngoại trú | BP-03 |
| BS-04 | Dịch vụ kê đơn điện tử | BP-04 |
| BS-05 | Dịch vụ cấp thuốc theo đơn | BP-05 |
| BS-06 | Dịch vụ thông tin cho người bệnh (lịch, đơn, trạng thái) | BP-01, BP-04, BP-05 |
| BS-07 | Dịch vụ kiểm soát truy cập & lưu vết (nội bộ) | BF-01 |
| BI-01 | Web/App bệnh nhân | kênh của BS-01, BS-06 |
| BI-02 | Tổng đài | kênh của BS-01 |
| BI-03 | Quầy/Kiosk tiếp đón | kênh của BS-02 |
| BI-04 | Kênh nhận đơn của nhà thuốc | kênh của BS-05 |
| PRD-01 | Gói khám ngoại trú (Product) = BS-01..BS-06 + CT-01 | Product |
| CT-01 | Thỏa thuận khám (điều khoản dịch vụ + đồng ý xử lý dữ liệu) | Contract |
| CT-02 | Hợp đồng liên kết nhà thuốc đối tác | Contract |

### 9.3 Business Process (BP) / Function (BF) – mã dùng chung với BPMN
| Mã | Tên | Bước con (task BPMN) | Role |
|---|---|---|---|
| BP-01 | Đặt lịch khám | BP-01.1 Chọn chuyên khoa/bác sĩ/khung giờ · BP-01.2 Xác nhận lịch hẹn · BP-01.3 Nhắc lịch | BR-BenhNhan, BR-LeTan |
| BP-02 | Tiếp đón | BP-02.1 Check-in · BP-02.2 Xác minh danh tính & BHYT · BP-02.3 Mở lượt khám & xếp hàng | BR-LeTan |
| BP-03 | Khám bệnh | BP-03.1 Đo sinh hiệu · BP-03.2 Xem hồ sơ & tiền sử · BP-03.3 Ghi nhận khám & chẩn đoán | BR-DieuDuong, BR-BacSi |
| BP-04 | Kê đơn điện tử | BP-04.1 Lập đơn · BP-04.2 Kiểm tra an toàn đơn · BP-04.3 Ký số & phát hành đơn · BP-04.4 Gửi đơn liên thông | BR-BacSi |
| BP-05 | Cấp thuốc | BP-05.1 Tiếp nhận & tra cứu đơn · BP-05.2 Cấp thuốc & tư vấn · BP-05.3 Xác nhận cấp thuốc | BR-DuocSi |
| BP-06A | Xử lý định danh/hồ sơ liên cơ sở (ngoại lệ biến thể A) | xem BPMN-02A | BR-LeTan, BR-BacSi |
| BP-06B | Cấp thuốc khi mất kết nối & đối soát (ngoại lệ biến thể B) | xem BPMN-02B | BR-DuocSi, BR-QuanLy |
| BP-06C | Điều chỉnh/thu hồi đơn (ngoại lệ biến thể C) | xem BPMN-02C | BR-BacSi, BR-DuocSi |
| BF-01 | Kiểm soát truy cập & lưu vết (Business Function, xuyên suốt) | | BR-QuanTriBaoMat |
| BF-02 | Quản lý vận hành & báo cáo (Business Function) | | BR-QuanLy |

### 9.4 Business Event (BE) & Object (BO)
| Mã | Tên | DO tương ứng (TV2) |
|---|---|---|
| BE-01 | BN có nhu cầu khám | |
| BE-02 | BN đến cơ sở | |
| BE-03 | Đơn thuốc đã phát hành | |
| BE-04 | BN nhận đủ thuốc | |
| BO-HoSoBenhNhan | Hồ sơ bệnh nhân | DO-Patient |
| BO-LichHen | Lịch hẹn | DO-Appointment |
| BO-TheBHYT | Thẻ BHYT | DO-Insurance |
| BO-LuotKham | Lượt khám | DO-Encounter |
| BO-BenhAnNgoaiTru | Bệnh án ngoại trú | DO-ClinicalRecord |
| BO-DonThuoc | Đơn thuốc | DO-Prescription, DO-PrescriptionItem |
| BO-PhieuCapThuoc | Phiếu cấp thuốc | DO-DispenseRecord |
| BO-NhatKyTruyCap | Nhật ký truy cập | DO-AuditEvent |
| BO-ChinhSachTruyCap | Chính sách truy cập | DO-AccessPolicy |
| BO-DongYChiaSe (A) | Đồng ý chia sẻ hồ sơ | DO-Consent |
| RP-01 | Mã đơn/QR trên SMS hoặc bản in (Representation của BO-DonThuoc) | |

## 10. Ghi chú cho TV2/TV3
- Xác nhận BP-01..BP-05 như TV2 đề xuất; ngoại lệ dùng **BP-06A/B/C** (không dùng BP-06 trống).
- Đề nghị TV2 thêm `EXT-NationalRxSystem` (Hệ thống đơn thuốc quốc gia, mock) phục vụ BP-04.4 / FR-06, và `AS-SubmitNationalRx`.
- AS cho bước BP-03.1 Đo sinh hiệu: dùng chung AS-RecordEncounter.

## 11. Bổ sung v0.2 (2026-11-03): mã task BPMN ngoại lệ và Baseline
| Mã | Tên |
|---|---|
| BP-06A.1 | Tìm & ghép định danh liên cơ sở (MPI) |
| BP-06A.2 | Xác minh thủ công (CCCD, BHYT, hỏi BN) |
| BP-06A.3 | Liên kết định danh |
| BP-06A.4 | Tạo hồ sơ mới tại cơ sở |
| BP-06A.5 | Yêu cầu xem hồ sơ cơ sở kia |
| BP-06A.6 | Xin đồng ý của BN |
| BP-06A.7 | Truy vấn & chuyển đổi hồ sơ về mô hình chuẩn (FHIR) |
| BP-06A.8 | Gắn cờ dữ liệu thiếu, cảnh báo |
| BP-06B.1 | Tra đơn trong bộ nhớ đệm |
| BP-06B.2 | Từ chối cấp, hướng dẫn BN |
| BP-06B.3 | Cấp có giới hạn, ghi phiếu cấp offline (dispenseId) |
| BP-06B.4 | Ghi hàng đợi đồng bộ cục bộ |
| BP-06B.5 | Đồng bộ bản ghi cấp (idempotent) |
| BP-06B.6 | Đối chiếu với trạng thái đơn |
| BP-06B.7 | Cập nhật trạng thái đơn & ghi audit |
| BP-06B.8 | Đối soát thủ công, liên hệ BN & nhà thuốc |
| BP-06B.9 | Ghi kết quả đối soát (audit) |
| BP-06C.1 | Chọn sửa/thu hồi, nhập lý do |
| BP-06C.2 | Kiểm tra trạng thái cấp của đơn |
| BP-06C.3 | Chuyển đơn sang REVOKED (giữ lịch sử) |
| BP-06C.4 | Lập phiên bản mới v+1, kiểm tra an toàn, ký số |
| BP-06C.5 | Lập đơn điều chỉnh/bổ sung (không xóa phần đã cấp) |
| BP-06C.6 | Phát sự kiện thay đổi đơn & ghi audit |
| BP-06C.7 | Chặn đơn cũ / áp dụng phiên bản mới (tại nhà thuốc) |
| BP-06C.8 | Liên hệ trực tiếp nhà thuốc (quá 30 phút chưa xác nhận) |
| BP0-01..06 | Quy trình Baseline: đặt lịch hotline/Zalo; lấy số & tiếp đón; khám bệnh án giấy; kê đơn in/viết tay; thanh toán & BHYT (Retain); mua thuốc bằng đơn giấy |
| BO0-01..04 | Object Baseline: sổ lịch hẹn Google Sheet; phiếu số thứ tự; bệnh án giấy; đơn thuốc giấy |
| BR-ThuNgan | Thu ngân (Role, Baseline + Retain) |

File nguồn: `02-models/ehealth-tv1-motivation-business.xml` (Archi: File > Import > Open Exchange XML Model), `02-models/bpmn/*.bpmn` (Camunda Modeler), ảnh ở `02-models/exports/`.

## 12. Bổ sung v0.3 (2026-11-04): tầng Chiến lược (Ch.7) — dùng trong `02-models/archimate/ehealth-full-model.xml`
| Mã | Loại | Tên | Ghi chú |
|---|---|---|---|
| CAP-00 | Capability | Khám chữa bệnh ngoại trú (năng lực tổng) | gồm CAP-01..09 |
| CAP-01 | Capability | Quản lý lịch hẹn & điều phối công suất | MỚI · hiện thực bởi BP-01 |
| CAP-02 | Capability | Tiếp nhận & định danh người bệnh | NÂNG CẤP · BP-02 |
| CAP-03 | Capability | Khám & quản lý hồ sơ lâm sàng | NÂNG CẤP · BP-03 |
| CAP-04 | Capability | Kê đơn an toàn | MỚI · BP-04 |
| CAP-05 | Capability | Liên thông đơn thuốc & cấp thuốc | MỚI · BP-05 |
| CAP-06 | Capability | Kiểm soát truy cập & lưu vết | MỚI · BF-01 |
| CAP-07 | Capability | Quản trị dữ liệu người bệnh liên cơ sở | MỚI · BP-06A (trọng tâm biến thể A) |
| CAP-08 | Capability | Đo lường & cải tiến vận hành | NÂNG CẤP · BF-02 |
| CAP-09 | Capability | Thanh toán & giám định BHYT | GIỮ · BP0-05 |
| RS-01..04 | Resource | Đội ngũ y tế · Dữ liệu BN & đơn · Nền tảng số dùng chung · Mạng lưới nhà thuốc | |
| COA-01 | Course of Action | Tuân thủ trước, tối ưu sau (bảo mật + kê đơn điện tử ở PLT-1) | realizes G-02, G-03 |
| COA-02 | Course of Action | Số hóa đầu vào để giảm chờ | G-01 |
| COA-03 | Course of Action | Liên thông qua cổng chuẩn, không buộc đối tác đổi phần mềm | G-04 |
| COA-04 | Course of Action | Một hồ sơ BN dùng chung cho 2 cơ sở | G-05 |
| VS-01 (.1–.5) | Value Stream | Khám ngoại trú đến khi nhận thuốc: Hẹn khám → Tiếp đón → Khám & chẩn đoán → Kê đơn an toàn → Nhận thuốc | |
| VAL-01 | Value | Được khám đúng hẹn, nhận thuốc đúng và an toàn | cho SH-01 |
| GRP-CoreApps | Grouping | Ứng dụng nghiệp vụ lõi (Target) | dùng ở view V-APP-1 |
