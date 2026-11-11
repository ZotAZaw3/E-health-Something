# Ma trận truy vết yêu cầu (RTM) — v0.1 (TV2, 2026-11-03)

> Mã theo 01-vision/catalog.md (TV1), 02-models/app-catalog.md (TV2), 02-models/tech-catalog.md (TV3). Cột "Hình" điền số hình khi ghép báo cáo.

## Chiều xuôi (Goal → Technology)
| Goal | Req | BPMN task | Business | Application (AS / AC / DO) | Technology | ADR | Kiểm chứng | Hình |
|---|---|---|---|---|---|---|---|---|
| G-01 | FR-01 Đặt lịch, xác nhận tức thì | BP-01.1, BP-01.2 | BP-01, BS-01, BR-BenhNhan, BO-LichHen | AS-BookAppointment / AC-Booking, AC-PatientPortal / DO-Appointment | TS-ApiGateway, ND-AppCluster, TS-Database | — | Mock `POST /appointments` 201 và 409 khung giờ hết | |
| G-02 | FR-05 Kê đơn có kiểm tra an toàn, ký số | BP-04.1, BP-04.2, BP-04.3 | BP-04, BS-04, BR-BacSi, BO-DonThuoc | AS-CheckDrugSafety, AS-IssuePrescription / AC-ePrescription (+ AC-EMR, AC-MasterData) / DO-Prescription, DO-PrescriptionItem, DO-Drug | ND-AppCluster, TS-Signing (ND-KeyVault), TS-Database | ADR-004 | Kịch bản E2E: kê đơn có thuốc BN dị ứng → cảnh báo chặn → sửa → phát hành | |
| G-04 | FR-07 + NFR-DAT-01 Cấp thuốc, không mất/không trùng | BP-04.4, BP-05.1, BP-05.3 | BP-05, BS-05, BR-DuocSi, BA-NhaThuocDoiTac, BO-PhieuCapThuoc | AS-SendPrescription, AS-ReceivePrescription, AS-RecordDispense / AC-PharmacyGateway / DO-DispenseRecord, DO-OutboxEvent | TS-Messaging (ND-MessageBroker), TS-ApiGateway, NW-PartnerChannel | ADR-001, ADR-004 | Gửi lại cùng `dispenseId` 2 lần → lần 2 trả 200 kết quả cũ, không tăng số đã cấp; cấp vượt → 409 | |
| G-03 | NFR-SEC-03 100% truy cập hồ sơ/đơn có log bất biến | BP-03.2, BP-04.x (xuyên suốt, BF-01) | BF-01, BS-07, BR-QuanTriBaoMat, BO-NhatKyTruyCap | AS-Authorize, AS-RecordAudit / AC-IAM, AC-Audit / DO-AuditEvent, DO-AccessPolicy | TS-PolicyDecision, TS-Audit (ND-AuditStore), TS-ObjectStorage WORM | ADR-002, ADR-003 | Bác sĩ không có lượt khám mở hồ sơ → 403 + AuditEvent result=DENIED | |

## Hàng theo biến thể (giữ 1 hàng khi biết biến thể)
| Goal | Req | BPMN task | Business | Application | Technology | ADR | Kiểm chứng |
|---|---|---|---|---|---|---|---|
| G-05 | FR-A1 Ghép định danh 2 cơ sở | BPMN-02A | BP-06A, BR-LeTan | AS-MatchPatient / AC-MPI, AC-IntegrationHub, AC-FhirAdapter-CS1/CS2 / DO-PatientLink | TS-Messaging, NW-SiteVPN | ADR-001 (mục A) | 2 hồ sơ cùng CCCD khác tên viết → hàng xác minh thủ công |
| G-04 | FR-B3 Phát hiện, chặn cấp trùng khi đồng bộ | BPMN-02B | BP-06B, BR-DuocSi, BR-QuanLy | AS-SyncDispense, AS-ReconcileDispense / AC-PharmacyAgent, AC-Reconciliation / DO-DispenseRecord | TS-Messaging, ND-PartnerPharmacy | ADR-001, ADR-004 (mục B) | Lô offline có 1 bản ghi vượt số còn lại → CONFLICT vào hàng đối soát |
| G-02 | FR-C2 Thu hồi đơn theo trạng thái cấp | BPMN-02C | BP-06C, BR-BacSi, BR-DuocSi | AS-RevokePrescription / AC-ePrescription (AF-PrescriptionVersioning) / DO-PrescriptionVersion, DO-AmendmentReason | TS-Signing, TS-Messaging | ADR-004 (mục C) | Thu hồi đơn PARTIALLY_DISPENSED → CLOSED_BY_REVOCATION, nhà thuốc nhận sự kiện và ack |

## Chiều ngược (Technology → Goal), dùng khi bị hỏi "thành phần này tồn tại vì sao?"
| Phần tử | Phục vụ | Vì yêu cầu | Vì Goal |
|---|---|---|---|
| ND-MessageBroker (TS-Messaging) | AC-PharmacyGateway | NFR-DAT-01, FR-06 (ADR-001) | G-04 |
| DO-OutboxEvent | AS-SendPrescription | NFR-DAT-01 (ADR-001) | G-04 |
| ràng buộc qty_dispensed ≤ qty_prescribed | AS-RecordDispense | NFR-DAT-01, FR-07 (ADR-004) | G-02, G-04 |
| AC-MasterData | AS-CheckDrugSafety | FR-05 | G-02 |
