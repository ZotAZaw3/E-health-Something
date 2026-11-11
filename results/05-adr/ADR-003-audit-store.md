# ADR-003: Kho lưu vết (audit store) — dịch vụ audit append-only có chuỗi băm, niêm phong ký số và lưu WORM

- **Trạng thái:** Đề xuất (chờ nhóm duyệt) | **Ngày:** 2026-11-03 | **Tác giả:** TV3 | **Người duyệt:** TV1, TV2
- **Liên quan:** G-03, OC-03, FR-09, NFR-SEC-03, NFR-SEC-05, NFR-PRF-01, NFR-AVL-01, CON-02, CON-03, PR-04, PR-05; ADR-002 (nguồn sự kiện quyết định truy cập), ADR-001/ADR-004 của TV2 (outbox, phiên bản đơn)

## 1. Bối cảnh

- OC-03 đòi **100% truy cập hồ sơ/đơn có log bất biến**. "Truy cập" gồm cả **đọc** và **bị từ chối**, không chỉ thay đổi dữ liệu.
- Nhật ký phải dùng được làm **bằng chứng** khi có tranh chấp hoặc thanh tra (ai xem hồ sơ của tôi? ai sửa đơn?), nên phải chống được việc **chính quản trị viên** sửa/xóa vết.
- Lưu ≥ 10 năm (NFR-SEC-05); tải ước tính ~30.000 sự kiện/ngày, ~11 GB/năm (technology.md mục 3.5).
- Ghi vết **không được làm chậm** luồng khám giờ cao điểm (NFR-PRF-01), nhưng cũng **không được mất** sự kiện.
- Nhật ký chứa dữ liệu cá nhân (ai khám ai), nên chính nó cũng phải được bảo vệ và tối thiểu hóa (CON-02).

## 2. Phương án

| | Mô tả |
|---|---|
| **A. Bảng lịch sử trong CSDL nghiệp vụ** | Mỗi schema có bảng `*_history` ghi bằng trigger khi INSERT/UPDATE/DELETE. Rẻ, quen thuộc. |
| **B. Nền tảng log tập trung / SIEM làm kho audit** | Các dịch vụ đẩy log ứng dụng về ELK/Wazuh; tra cứu, cảnh báo bằng công cụ có sẵn. |
| **C. Dịch vụ audit riêng, append-only, chuỗi băm + niêm phong ký số + lưu WORM** | AC-Audit nhận sự kiện có cấu trúc (qua outbox → hàng đợi), ghi vào kho chỉ-thêm (PostgreSQL bị thu hồi quyền UPDATE/DELETE, phân vùng theo tháng); mỗi bản ghi chứa băm của bản trước; mỗi giờ tạo **checkpoint** ký bằng khóa trong KMS; phân vùng cũ được niêm phong và chuyển sang object storage khóa WORM. SIEM nhận **bản sao** để phát hiện bất thường. |
| **D. Blockchain có cấp phép giữa phòng khám và nhà thuốc** | Sổ cái phân tán (vd Hyperledger Fabric), mỗi bên giữ một node, đồng thuận trước khi ghi. |

## 3. Tiêu chí và chấm điểm (1–5, cao là tốt)

| Tiêu chí | Trọng số | A | B | C | D |
|---|---|---|---|---|---|
| Toàn vẹn, chống sửa/xóa kể cả bởi quản trị viên (NFR-SEC-03) | 30% | 1 | 2 | 5 | 5 |
| Đầy đủ: ghi cả đọc/từ chối, không mất sự kiện | 20% | 2 | 3 | 5 | 4 |
| Chi phí & độ phức tạp cho đội CNTT nhỏ (CON-07) | 20% | 5 | 4 | 3 | 1 |
| Không làm chậm luồng nghiệp vụ (NFR-PRF-01) | 15% | 3 | 5 | 4 | 2 |
| Truy vấn phục vụ điều tra/báo cáo (FR-09) | 15% | 4 | 5 | 4 | 2 |
| **Tổng có trọng số** | 100% | **2,75** | **3,50** | **4,30** | **3,10** |

Giải thích:
- A: trigger chỉ bắt **thay đổi**, không bắt **đọc**; DBA sửa được cả bảng lịch sử; nhật ký nằm chung CSDL nghiệp vụ, mất cùng lúc khi CSDL hỏng.
- B: rất tốt cho tra cứu và cảnh báo, nhưng log ứng dụng là "best effort" (có thể rơi khi quá tải), và quản trị viên SIEM xóa được chỉ mục, nên không đủ làm bằng chứng.
- D: toàn vẹn cao, nhưng nhà thuốc đối tác nhỏ không vận hành nổi node, độ trễ đồng thuận cao, chi phí lớn. Lợi ích "nhiều bên không tin nhau" không cần thiết vì phòng khám là bên chịu trách nhiệm giữ hồ sơ; C đạt cùng mức chống sửa nhờ checkpoint ký số + WORM.

## 4. Quyết định

**Chọn C**, đồng thời **giữ B làm luồng phụ** (SIEM nhận bản sao để phát hiện bất thường, không phải nguồn bằng chứng).

### 4.1. Cấu trúc một AuditEvent (DO-AuditEvent)

| Trường | Ý nghĩa | Ghi chú tối thiểu hóa |
|---|---|---|
| `eventId` | UUID, sinh tại nguồn | Dùng làm khóa idempotency khi ghi |
| `ts` | Thời điểm (UTC, đồng bộ NTP) | |
| `actor` | `userId`, `role`, `facility`, `pharmacyId?` | Không ghi tên |
| `action` | READ / CREATE / UPDATE / SIGN / REVOKE / DISPENSE / LOGIN / BREAK_GLASS / EXPORT | |
| `resource` | `type` + `id` (vd `Prescription/RX-...`) + `patientRef` (mã giả danh) | **Không ghi nội dung y tế** |
| `decision` | PERMIT / DENY + `policyId` + `policyVersion` | Từ ADR-002 |
| `breakGlass` | true/false + lý do | |
| `source` | IP, thiết bị, kênh (StaffUI/Portal/PartnerAPI) | |
| `outcome` | SUCCESS / FAILURE + mã lỗi | |
| `correlationId` | Nối các bước một giao dịch (đặt lịch → cấp thuốc) | |
| `prevHash`, `hash` | `hash = SHA-256(prevHash ‖ nội dung chuẩn hóa)` | Phát hiện sửa/xóa/chèn |

### 4.2. Đường ghi (không chặn luồng khám, không mất sự kiện)

1. Dịch vụ nghiệp vụ ghi AuditEvent vào bảng **outbox trong cùng giao dịch** với thay đổi nghiệp vụ (với thao tác đọc: ghi outbox trước khi trả dữ liệu). Dùng chung cơ chế outbox với ADR-001 của TV2 (DO-OutboxEvent).
2. Bộ chuyển tiếp đẩy outbox sang TS-Messaging (hàng đợi bền, at-least-once).
3. AC-Audit nhận, bỏ trùng theo `eventId`, nối chuỗi băm, ghi vào ND-AuditStore. Quyền CSDL: tài khoản ứng dụng chỉ có `INSERT`, `SELECT`; không ai có `UPDATE/DELETE` trên bảng audit (thu hồi cả với chủ sở hữu schema, thay đổi cấu trúc phải qua quy trình 2 người duyệt).
4. Mỗi giờ: tạo checkpoint `{phân vùng, eventId cuối, hash cuối, số lượng}` ký bằng khóa trong ND-KeyVault (TS-Signing), lưu vào ND-ObjectStore chế độ WORM và sao sang ND-BackupDR.
5. Sau 90 ngày: phân vùng tháng được niêm phong (xuất file + chữ ký) sang WORM, giữ 10 năm; CSDL nóng giữ 13 tháng để tra cứu nhanh.
6. Song song: bản sao sự kiện đi sang TS-SIEM (cảnh báo: break-glass bất thường, một người đọc > 50 hồ sơ/giờ, truy cập ngoài giờ).

**Khi đường ghi gặp sự cố:** outbox giữ sự kiện (không mất). Nếu outbox của một dịch vụ vượt ngưỡng (hàng đợi không chạy) thì dịch vụ chuyển sang **fail-closed với thao tác đọc hồ sơ thường**, vẫn cho **break-glass** (PR-01 an toàn người bệnh được ưu tiên hơn PR-04, nhưng vết break-glass vẫn được giữ trong outbox).

### 4.3. Kiểm chứng

- `GET /audit-events/verify?from&to`: tính lại chuỗi băm và đối chiếu checkpoint đã ký → báo vị trí đầu tiên bị sai lệch (có trong prototype).
- Truy cập vào chính nhật ký (BR-QuanTriBaoMat, BR-BenhNhan xem "ai đã xem hồ sơ của tôi") cũng sinh AuditEvent `action=READ, resource=AuditEvent`.

## 5. Đánh đổi

- **Được:** bằng chứng chống chối bỏ, kể cả với quản trị viên; ghi được đọc/từ chối; không chặn luồng khám; tách khỏi CSDL nghiệp vụ nên sống sót khi CSDL nghiệp vụ hỏng; tra cứu đủ tốt bằng SQL + SIEM.
- **Mất:** thêm 1 dịch vụ + KMS + object storage WORM phải vận hành; độ trễ từ lúc truy cập tới lúc vết xuất hiện để tra cứu là vài giây (bất đồng bộ); dữ liệu 10 năm không xóa được trước hạn, kể cả khi BN yêu cầu xóa dữ liệu (nghĩa vụ lưu trữ theo luật là căn cứ để từ chối, cần ghi trong thông báo xử lý dữ liệu, CT-01).

## 6. Rủi ro và giảm thiểu

| Rủi ro | Giảm thiểu |
|---|---|
| RSK-02 vết bị sửa/xóa hoặc mất | Chuỗi băm + checkpoint ký số + WORM + bản sao DR; kiểm tra verify tự động hằng ngày |
| Lộ dữ liệu qua chính nhật ký | Không ghi nội dung y tế, `patientRef` giả danh, mã hóa khi lưu, chỉ BR-QuanTriBaoMat được đọc |
| Mất khóa ký checkpoint | Khóa trong HSM/KMS có sao lưu; xoay khóa hằng năm, checkpoint ghi `keyId` |
| Đồng hồ lệch giữa nguồn | NTP bắt buộc; thứ tự chuỗi theo thời điểm nhận, `ts` nguồn chỉ là thông tin |

## 7. Phần tử ArchiMate bị ảnh hưởng

AC-Audit, AS-RecordAudit, AS-QueryAudit, DO-AuditEvent, DO-OutboxEvent, BO-NhatKyTruyCap, BF-01, TS-Audit, TS-ObjectStorage, TS-Signing, TS-SIEM, TS-Messaging, ND-AuditStore, ND-ObjectStore, ND-KeyVault, ND-SecOps, ND-BackupDR, ART-audit-log; WP-02; PLT-1.

## 8. Điều kiện xem xét lại

- Cơ quan quản lý yêu cầu nộp nhật ký về một hệ thống tập trung quốc gia → thêm bộ xuất, giữ kho hiện tại làm nguồn.
- Số bên tham gia ngang hàng tăng mạnh và **không có bên nào được tin là người giữ sổ** (vd liên minh nhiều phòng khám độc lập) → xem lại phương án D.
- Lượng sự kiện > 1 triệu/ngày → xem lại kho (chuyển sang kho cột/time-series), giữ nguyên mô hình chuỗi băm + checkpoint.
