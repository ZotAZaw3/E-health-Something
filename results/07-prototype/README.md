# Prototype minh họa — TV3, v0.1 (2026-11-03)

Đề yêu cầu "prototype mock UI/API/quy trình cho 01 kịch bản end-to-end và 01 ngoại lệ". Bộ này gồm:

| File | Nội dung |
|---|---|
| `openapi.yaml` | Hợp đồng API (OpenAPI 3.0.3, đã lint bằng Redocly: hợp lệ). Mỗi endpoint gắn AS-*, FR-*, POL-* |
| `mock-server/server.js` | Mock server chạy được, **không cần cài thư viện** (Node ≥ 18). Có trạng thái trong bộ nhớ, kiểm tra quyền RBAC+ABAC (ADR-002), ghi audit có chuỗi băm (ADR-003), idempotency (NFR-DAT-01) |
| `mock-server/public/index.html` | Giao diện bấm thử thay cho Figma (7 vai trò, 5 nhóm màn hình) gọi đúng API thật của mock |
| `demo.sh` | Kịch bản gọi API bằng curl: E2E + ngoại lệ lõi + A/B/C |
| `api-trace.txt` | Kết quả chạy `demo.sh all` (dán vào phụ lục báo cáo làm "API trace") |
| `scenario-outage.sh`, `scenario-outage-trace.txt` | Thử nghiệm tình huống bất thường: Hệ thống đơn thuốc quốc gia ngừng → outbox gửi bù, không trùng (xem `05-verification/change-scenario.md`) |
| `screenshots/*.png` | Ảnh chụp màn hình theo kịch bản (dùng cho báo cáo và slide) |
| `screens.md` | Mô tả từng màn hình, ánh xạ BPMN task → màn hình → API |

## Chạy demo (2 phút)

```bash
cd 04-prototype
node mock-server/server.js          # http://localhost:4010
# Mở trình duyệt http://localhost:4010 → chọn vai trò ở góc trên, đi theo thứ tự S1 → S5
bash demo.sh all                    # hoặc: bash demo.sh lõi | A | B | C
```

Muốn xem tài liệu API dạng Swagger: mở https://editor.swagger.io và dán nội dung `openapi.yaml`, hoặc `npx @redocly/cli preview-docs openapi.yaml`.

## Kịch bản trình bày khi bảo vệ (khớp BPMN-01 và nhánh ngoại lệ)

**End-to-end (BP-01 → BP-05):**
1. *Bệnh nhân P001* đặt lịch 08:00 BS Trần An → nhận mã QR (S1).
2. *Lễ tân CS1* quét QR + CCCD → mở lượt khám, BHYT hợp lệ, số thứ tự 1 (S2).
3. *BS Trần An* mở hồ sơ, thấy cảnh báo dị ứng penicillin; kê Amoxicillin → **hệ thống chặn** (AS-CheckDrugSafety); đổi Cefuroxim → lưu → ký số & phát hành, đơn tự liên thông Hệ thống đơn thuốc quốc gia (S3).
4. *Dược sĩ NT-01* nhập mã đơn + 4 số cuối SĐT → thấy đơn tối thiểu (không có chẩn đoán) → xác nhận cấp; bấm lại lần 2 → hệ thống nhận ra gửi trùng, không tạo bản ghi mới (S4).
5. *DPO* mở nhật ký P001 → thấy toàn bộ chuỗi truy cập (S5).

**Ngoại lệ (lõi, không phụ thuộc biến thể):**
6. *BS Lê Bình* (không phụ trách) mở hồ sơ P001 → **403, đã ghi nhật ký** → khai báo truy cập khẩn cấp có lý do → được xem với cờ BREAK-GLASS, nhưng **không kê đơn được** (S6).
7. *DPO* kiểm chứng chuỗi băm → hợp lệ; giả lập sửa 1 bản ghi → hệ thống chỉ ra đúng bản ghi bị sửa (S5).

**Ngoại lệ theo biến thể** (khi biết biến thể được giao, trình bày đúng 1 cái, nhánh tương ứng BP-06A/B/C):
- **A:** `GET /patients/match` → CCCD khớp: AUTO_LINK; chỉ khớp tên + năm sinh: MANUAL_REVIEW.
- **B:** đơn đã giao NT-01 (ASSUMP-10); NT-01 mất mạng, 2 quầy cùng cấp từ bộ nhớ đệm; khi đồng bộ lô: bản ghi đã gửi trước → DUPLICATE, bản ghi đầu → ACCEPTED, bản ghi cấp trùng → CONFLICT + mở hồ sơ đối soát.
- **C:** thu hồi đơn đã cấp → 409 (không xóa lịch sử); lập phiên bản điều chỉnh v2 → v1 SUPERSEDED, phần đã cấp được chuyển sang v2 để không cấp lại, cảnh báo BN đã nhận thừa Paracetamol; thu hồi đơn chưa cấp → REVOKED, nhà thuốc không cấp được.

## Giới hạn (nói rõ khi bảo vệ)

- Token cố định thay cho OIDC + MFA; chữ ký số, Hệ thống đơn thuốc quốc gia, cổng BHYT, SMS đều là mock.
- Audit ghi đồng bộ trong bộ nhớ (thật: outbox → hàng đợi → AC-Audit, checkpoint ký số, WORM — ADR-003).
- `POST /_demo/tamper`, `/_demo/national-rx` và `/_demo/reset` chỉ tồn tại trong mock để minh họa.
