# Kiểm chứng tình huống bất thường và thay đổi giả định — v1.0 (2026-11-04)

> Đề yêu cầu "thử nghiệm 01 tình huống bất thường/thay đổi". Nhóm làm **1 tình huống bất thường có chạy thử thật trên prototype** (mục 1) và **1 thay đổi giả định phân tích theo quy trình 4 bước** (mục 2). Cả hai không phụ thuộc biến thể, nên dùng được dù giảng viên giao A, B hay C.
> Mã phần tử theo 3 catalog (`01-vision/catalog.md`, `02-models/app-catalog.md`, `02-models/tech-catalog.md`).

## Quy trình 4 bước dùng chung (khớp `gap-roadmap.md` mục 4)

1. **Xác định yêu cầu/ràng buộc bị chạm:** Driver, Requirement, Constraint, Assumption nào đổi hoặc bị thử thách.
2. **Dò RTM xuôi và ngược** (`rtm.md`, view `V-LAY-1`, `V-LAY-2`) để ra các phần tử Business/Application/Technology liên quan.
3. **Xem lại ADR**: quyết định nào còn đúng, quyết định nào phải mở lại (dựa vào mục "Điều kiện xem xét lại" của từng ADR).
4. **Cập nhật lộ trình và rủi ro:** WP/Plateau nào thay đổi, RSK nào đổi điểm.

---

## 1. Tình huống bất thường: Hệ thống đơn thuốc quốc gia ngừng 2 giờ trong giờ cao điểm

### 1.1. Mô tả và vì sao chọn
Lúc 8h00–10h00 (cao điểm, ~45% lượt khám trong ngày, ASSUMP-02), `EXT-NationalRxSystem` trả lỗi 503. Khoảng 90 đơn được phát hành trong 2 giờ này. Tình huống chọn vì nó thử cùng lúc 3 thứ quan trọng nhất của kiến trúc: **PR-01** (an toàn người bệnh, không chặn khám chữa bệnh), **ADR-001** (outbox + hàng đợi bền + idempotency) và **NFR-DAT-01** (không mất, không trùng). Sự cố hệ thống bên ngoài là việc chắc chắn xảy ra, không phải giả thuyết xa.

### 1.2. Bước 1–2: yêu cầu bị chạm và phần tử liên quan

| Tầng | Phần tử |
|---|---|
| Motivation | G-04, OC-04 (≥ 95% đơn liên thông ≤ 5 phút), FR-06, NFR-AVL-01, NFR-DAT-01, CON-01, PR-01, PR-08 |
| Business | BP-04.4 Gửi đơn liên thông, BP-05.1 Tiếp nhận & tra cứu đơn, BR-BacSi, BR-DuocSi |
| Application | AS-SubmitNationalRx, AS-SendPrescription, AS-ReceivePrescription, AC-ePrescription, AC-PharmacyGateway, DO-OutboxEvent, AC-Audit |
| Technology | TS-Messaging (ND-MessageBroker), TS-Database, TS-Monitoring |
| ADR | ADR-001 (chính), ADR-003 (ghi vết lần gửi bù), ADR-004 (trạng thái đơn) |

### 1.3. Kỳ vọng theo kiến trúc và kết quả chạy thử

Chạy: `node mock-server/server.js` rồi `bash scenario-outage.sh` (kết quả đầy đủ ở `04-prototype/scenario-outage-trace.txt`). Mock có thêm `POST /_demo/national-rx {"up":false|true}` để bật/tắt hệ thống quốc gia giả lập.

| # | Bước | Kỳ vọng (theo ADR-001, PR-01) | Kết quả trên mock | Đạt |
|---|---|---|---|---|
| 1 | Hệ thống quốc gia ngừng | Không ảnh hưởng ngay tới phòng khám | `nationalRxUp: false` | ✓ |
| 2 | Bác sĩ ký và phát hành đơn | Vẫn phát hành được, không bắt bác sĩ chờ; đơn và sự kiện outbox ghi cùng giao dịch | `200`, `status: ISSUED`, `nationalRx.status: QUEUED`, `lastError: 503`, BN vẫn nhận SMS mã đơn | ✓ |
| 3 | Nhà thuốc đối tác tra đơn và cấp | Tra qua cổng phòng khám (AC-PharmacyGateway), không phụ thuộc hệ thống quốc gia | `200` tra đơn; `201` ghi cấp, đơn `DISPENSED` | ✓ |
| 4 | Giám sát | Thấy số đơn tồn chưa liên thông để cảnh báo | `outboxPending: 1` | ✓ |
| 5 | Hệ thống quốc gia hoạt động lại | Gửi bù tự động, có ghi vết | `flushed: [...]`, đơn `SUBMITTED`, `attempts: 2`, audit `SUBMIT_NATIONAL_RX` lý do `OUTBOX_RETRY` | ✓ |
| 6 | Job gửi bù chạy lặp | Không gửi trùng | Lần 2: `flushed: []`, `outboxPending: 0` | ✓ |
| 7 | Kiểm tra chuỗi audit | Chuỗi băm còn nguyên | `valid: true` | ✓ |

### 1.4. Bước 3: ADR còn đúng không?
- **ADR-001 được xác nhận.** Nếu chọn phương án A (gọi đồng bộ), bước 2 sẽ thất bại: bác sĩ không phát hành được đơn suốt 2 giờ, khoảng 90 BN phải chờ hoặc quay về đơn giấy (vi phạm CON-01 theo hướng khác). Phương án C (lô cuối ngày) không bị ảnh hưởng bởi sự cố này nhưng vốn đã không đạt OC-04 trong ngày bình thường.
- **Đánh đổi lộ ra:** trong 2 giờ sự cố, OC-04 tạm không đạt (đơn liên thông muộn tới 2 giờ). Đây là đánh đổi có chủ đích theo PR-01: ưu tiên khám chữa bệnh liên tục hơn đúng hạn liên thông.
- **ADR-003:** lần gửi bù có bản ghi audit riêng, nên chứng minh được đơn nào liên thông muộn và vì sao.

### 1.5. Bước 4: điều chỉnh sau thử nghiệm
| Phát hiện | Điều chỉnh | Phần tử / WP |
|---|---|---|
| Cách đo OC-04 chưa nói gì về sự cố bên ngoài | Đo OC-04 riêng phần do phòng khám kiểm soát; ghi nhận sự cố bên ngoài có thời gian bắt đầu, kết thúc, số đơn tồn | AC-Reporting, FR-11, WP-04 |
| Cần ngưỡng cảnh báo | `outboxPending` > 20 hoặc đơn tồn > 15 phút → cảnh báo trực CNTT; > 4 giờ → báo cáo Sở Y tế theo quy trình sự cố | TS-Monitoring, WP-08 (SOP) |
| Đơn thuốc kiểm soát (CON-04) | Vẫn phát hành được nhưng chỉ cấp tại nhà thuốc nội bộ (POL-06 đã có), không đổi | — |
| Rủi ro | Bổ sung tình huống này vào RSK-03 (mất kết nối) như một dạng "đối tác ngoài ngừng"; điểm X×T giữ nguyên vì đối sách đã có | RSK-03 |

---

## 2. Thay đổi giả định: mở thêm cơ sở 3 và thêm 10 nhà thuốc đối tác trong 6 tháng

*(Dạng câu giảng viên hay hỏi: "nếu quy mô tăng / thêm đối tác thì kiến trúc có chịu được không?")*

**Giả định đổi:** ASSUMP-02 (2 cơ sở, ~500 lượt/ngày) → 3 cơ sở, ~800 lượt/ngày; ASSUMP-04 (6 nhà thuốc đối tác) → 16. Cơ sở 3 dùng phần mềm thu ngân thứ ba (khác HIS-Lite và ClinicSoft).

| Bước | Phân tích |
|---|---|
| 1. Yêu cầu bị chạm | NFR-INT-02 (thêm cơ sở/nhà thuốc không sửa lõi), NFR-PRF-01 (300 → ~500 người dùng đồng thời giờ cao điểm), CON-06 (không buộc đổi phần mềm), CON-07 (ngân sách), G-05 |
| 2. Dò RTM | Application: AC-PharmacyGateway (adapter đối tác), AC-Reception, AC-EMR, DO-Patient, DO-Pharmacy, AC-MasterData. Technology: ND-AppCluster, ND-DataCluster, NW-SiteVPN (thêm 1 đường VPN), NW-PartnerChannel (thêm 10 chứng thư mTLS). Business: BA-PhongKham thêm BA-CS3; CT-02 thêm 10 hợp đồng |
| 3. ADR | **ADR-001 giữ nguyên**: thêm nhà thuốc = thêm cấu hình + chứng thư + (nếu cần) adapter trong Gateway, đúng mục đích NFR-INT-02; ngưỡng xem lại của ADR-001 là ~50 đối tác, còn xa. **ADR-002 giữ nguyên**: POL-02 (cơ sở) dùng thuộc tính `facility`, chỉ cần thêm giá trị CS3. **ADR-003 giữ nguyên**: audit tăng ~60% (~18 GB/năm), vẫn trong khả năng phân vùng theo tháng. **ADR-004 giữ nguyên**. Nếu nhóm nhận **biến thể A**: hub-and-spoke cho thêm 1 AC-FhirAdapter-CS3, số kết nối tăng tuyến tính (3 thay vì 3 cặp điểm–điểm), MPI không đổi thiết kế |
| 4. Lộ trình & rủi ro | Thêm **WP-09 Mở rộng CS3 & đối tác đợt 2** sau PLT-3 (không chen vào lộ trình 12 tháng): mạng/VPN CS3, kết nối thu ngân CS3 qua adapter, nạp dữ liệu BN CS3 (lặp lại cách WP-07a/b), onboard 10 nhà thuốc theo lô 3–4 nhà/tháng. Scale ngang ND-AppCluster 3 → 4 VM, bật read replica cho báo cáo. RSK-06 (quá tải) X 2 → 3; RSK-07 (hệ thống cũ khó tích hợp) X giữ 4 vì thêm 1 nhà cung cấp; RSK-05 (ghép sai định danh) X 3 → 4 do thêm nguồn dữ liệu |

**Kết luận:** kiến trúc chịu được thay đổi mà **không phải mở lại ADR nào**, chỉ thêm cấu hình, adapter và một WP. Đây là bằng chứng cho lựa chọn PR-08 (kết nối lỏng qua giao diện) và ADR-001: nếu đã chọn tích hợp điểm–điểm hoặc CSDL dùng chung, thay đổi này sẽ phải sửa lõi.

---

## 3. Bảng tra nhanh: các thay đổi giả định khác và chỗ trả lời

| Thay đổi giảng viên có thể đưa ra | ADR/phần tử bị chạm | Trả lời ngắn | Xem |
|---|---|---|---|
| Quy định mới: BN phải đồng ý (consent) cho mỗi lần chia sẻ hồ sơ | ADR-002 (POL-08), AC-Consent, DO-Consent | Bật POL-08 cho mọi luồng chia sẻ, không sửa ứng dụng vì quyết định nằm ở PDP | ADR-002 mục 8 |
| Nhà thuốc mất mạng 48 giờ | ADR-001, RSK-03/04 | Hàng đợi giữ ≥ 72 giờ đủ; BN đổi nhà thuốc theo ASSUMP-10 | `risk-register.md` ghi chú |
| Tải tăng ×5 | NFR-PRF-01, ND-AppCluster, RSK-06 | Scale ngang, read replica, phân vùng audit | `technology.md` 3.5 |
| Bỏ ASSUMP-10 (1 đơn chia cho nhiều nhà thuốc) | ADR-004, DO-DispenseRecord | Sổ cái cấp thuốc vẫn đúng; phải thêm khóa lạc quan theo dòng thuốc và đối soát chéo nhà thuốc | ADR-004 |
| Chuyển hạ tầng về on-prem | `technology.md` 3.1, CON-07 | Phương án điểm 3,20; kiến trúc ứng dụng không đổi, đổi WP-01 và RSK-06 | `technology.md` 3.1 |
| Kiểm toán yêu cầu chứng minh ai đã xem hồ sơ BN X tháng trước | ADR-003, AS-QueryAudit | Tra theo `patientRef`, verify chuỗi băm + checkpoint ký số | Prototype S5 |
