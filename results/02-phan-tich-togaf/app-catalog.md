# Danh mục mã Tầng Ứng dụng & Dữ liệu (TV2) — v0.2 (2026-11-03, đã khớp catalog TV1 v0.1)

> Nguồn sự thật cho tên/mã AC, AS, AI, DO. TV2 là người duy nhất thêm/đổi tên Data Object và Application Component.
> Mã BP/FR/NFR/G do TV1 sở hữu (01-vision/catalog.md); mã ND/TS do TV3 sở hữu (tech-catalog.md). BP-01..05 đã được TV1 xác nhận; ngoại lệ là BP-06A/B/C.
> Quy ước: mã tiếng Anh (PascalCase), tên hiển thị tiếng Việt; trong Archi đặt tên phần tử = "<mã> <tên VN>", ví dụ "AS-IssuePrescription Kê đơn điện tử".

## 1. Application Component (Target, lõi — không phụ thuộc biến thể)
| Mã | Tên hiển thị | Ghi chú |
|---|---|---|
| AC-PatientPortal | Cổng bệnh nhân (web/app) | Đặt lịch, xem đơn, nhận thông báo |
| AC-Booking | Quản lý lịch hẹn | |
| AC-Reception | Tiếp đón | Check-in, xác minh danh tính/BHYT, mở lượt khám |
| AC-EMR | Hồ sơ bệnh án điện tử | Lượt khám, chẩn đoán, tiền sử, dị ứng |
| AC-ePrescription | Kê đơn điện tử | Kê đơn, kiểm tra an toàn thuốc, ký số, trạng thái đơn |
| AC-PharmacyGateway | Cổng kết nối nhà thuốc | Gửi đơn, nhận kết quả cấp thuốc, chuyển đổi định dạng |
| AC-Notification | Thông báo | SMS/email/push nhắc lịch, báo đơn |
| AC-IAM | Định danh & phân quyền | RBAC+ABAC (ADR-002 của TV3) |
| AC-Audit | Lưu vết | Ghi/tra cứu AuditEvent (ADR-003 của TV3) |
| AC-MasterData | Danh mục dùng chung | Thuốc, ICD-10, chuyên khoa, bác sĩ, nhà thuốc |
| AC-Reporting | Báo cáo vận hành | Thời gian chờ, tỷ lệ đơn điện tử/đơn phải sửa (FR-11) |

Hệ thống ngoài (External Application Component, mock):
| Mã | Tên |
|---|---|
| EXT-PharmacySystem | Phần mềm nhà thuốc đối tác |
| EXT-InsurancePortal | Cổng giám định BHYT (mock) |
| EXT-SmsGateway | Nhà cung cấp SMS/OTP |
| EXT-NationalRxSystem | Hệ thống đơn thuốc quốc gia (mock) — BP-04.4, FR-06 |

Hệ thống hiện có được giữ lại (Retain, ASSUMP-06/CON-05) — thu ngân & BHYT:
| Mã | Tên |
|---|---|
| AC-HisLite-CS1 | HIS-Lite tại CS1 (Baseline: thu ngân, BHYT, in đơn; Target: chỉ thu ngân/BHYT) |
| AC-ClinicSoft-CS2 | ClinicSoft tại CS2 (Baseline: toàn bộ; Target: chỉ thu ngân/BHYT; biến thể A: giữ cả dữ liệu lâm sàng) |

Chỉ có ở Baseline (Eliminate):
| Mã | Tên |
|---|---|
| AC-BookingSheet | Google Sheet lịch hẹn (hotline/Zalo OA ghi vào) |

Bổ sung theo biến thể (chỉ đưa vào mô hình khi biết biến thể):
| Biến thể | Mã | Tên |
|---|---|---|
| A | AC-IntegrationHub | Trục tích hợp liên cơ sở |
| A | AC-FhirAdapter-CS1 / AC-FhirAdapter-CS2 | Bộ chuyển đổi FHIR từng cơ sở |
| A | AC-MPI | Chỉ mục bệnh nhân chủ (MPI) |
| A | AC-Consent | Quản lý đồng ý chia sẻ hồ sơ |
| B | AC-PharmacyAgent | Tác tử nhà thuốc (offline-first, cache đơn) |
| B | AC-Reconciliation | Đối soát cấp thuốc |
| C | (không thêm AC) | Bổ sung chức năng AF-PrescriptionVersioning trong AC-ePrescription |

## 2. Application Service (khớp BPMN task)
| Mã | Tên hiển thị | Hiện thực bởi | Phục vụ BP (đề xuất, chờ TV1) |
|---|---|---|---|
| AS-BookAppointment | Đặt lịch khám | AC-Booking | BP-01.1, BP-01.2 |
| AS-CancelAppointment | Hủy/đổi lịch khám | AC-Booking | BP-01 (FR-02) |
| AS-CheckIn | Tiếp nhận check-in, mở lượt khám | AC-Reception | BP-02.1, BP-02.3 |
| AS-VerifyInsurance | Xác minh danh tính & thẻ BHYT | AC-Reception (gọi EXT-InsurancePortal) | BP-02.2 |
| AS-ViewMedicalRecord | Tra cứu hồ sơ bệnh án | AC-EMR | BP-03.2 |
| AS-RecordEncounter | Ghi nhận khám (sinh hiệu, chẩn đoán ICD-10) | AC-EMR | BP-03.1, BP-03.3 |
| AS-IssuePrescription | Lập, ký số & phát hành đơn | AC-ePrescription | BP-04.1, BP-04.3 |
| AS-CheckDrugSafety | Kiểm tra dị ứng/tương tác/trùng hoạt chất/liều | AC-ePrescription | BP-04.2 |
| AS-SendPrescription | Gửi đơn tới nhà thuốc | AC-PharmacyGateway | BP-04.4 |
| AS-SubmitNationalRx | Gửi đơn lên Hệ thống đơn thuốc quốc gia | AC-PharmacyGateway (gọi EXT-NationalRxSystem) | BP-04.4 |
| AS-ReceivePrescription | Nhận/tra cứu đơn theo mã tại nhà thuốc | AC-PharmacyGateway | BP-05.1 |
| AS-RecordDispense | Ghi nhận cấp thuốc toàn phần/một phần | AC-PharmacyGateway | BP-05.3 |
| AS-SendNotification | Gửi thông báo | AC-Notification | BP-01.3, BP-04.4, BP-05.3 (FR-10) |
| AS-ReportOperations | Báo cáo vận hành (đo Outcome) | AC-Reporting | BF-02 (FR-11) |
| AS-Authenticate / AS-Authorize | Xác thực / Phân quyền | AC-IAM | BF-01 (FR-08) |
| AS-RecordAudit / AS-QueryAudit | Ghi / tra cứu vết | AC-Audit | BF-01 (FR-09) |
| A: AS-MatchPatient, AS-ExchangeRecord, AS-RecordConsent | Ghép định danh / Trao đổi hồ sơ liên cơ sở / Ghi nhận đồng ý | AC-MPI / AC-IntegrationHub / AC-Consent | BP-06A |
| B: AS-SyncDispense, AS-ReconcileDispense | Đồng bộ cấp thuốc / Đối soát | AC-PharmacyAgent / AC-Reconciliation | BP-06B |
| C: AS-AmendPrescription, AS-RevokePrescription | Điều chỉnh / Thu hồi đơn | AC-ePrescription | BP-06C |

## 3. Application Interface
| Mã | Tên |
|---|---|
| AI-PortalUI | Giao diện web/app bệnh nhân |
| AI-StaffUI | Giao diện web nhân viên (lễ tân, bác sĩ) |
| AI-PrescriptionAPI | API đơn thuốc (REST/FHIR MedicationRequest) |
| AI-PharmacyAPI | API cho nhà thuốc có tích hợp (REST/FHIR + webhook) |
| AI-PharmacyWebUI | Cổng web nhà thuốc (cho nhà thuốc nội bộ và đối tác chưa tích hợp, CON-06) |
| AI-EventChannel | Kênh sự kiện (publish/subscribe) |

## 4. Data Object
| Mã | Tên | Business Object tương ứng (TV1) |
|---|---|---|
| DO-Patient | Bệnh nhân | BO-HoSoBenhNhan |
| DO-Practitioner | Nhân viên y tế | |
| DO-Appointment | Lịch hẹn | BO-LichHen |
| DO-Encounter | Lượt khám | BO-LuotKham |
| DO-ClinicalRecord | Ghi nhận lâm sàng (chẩn đoán, dị ứng, chỉ định) | BO-BenhAnNgoaiTru |
| DO-Insurance | Thẻ BHYT | BO-TheBHYT |
| DO-Prescription | Đơn thuốc | BO-DonThuoc |
| DO-PrescriptionItem | Dòng thuốc trong đơn | |
| DO-Drug | Danh mục thuốc | |
| DO-DispenseRecord | Bản ghi cấp thuốc | BO-PhieuCapThuoc |
| DO-Notification | Thông báo | |
| DO-AccessPolicy | Chính sách truy cập | BO-ChinhSachTruyCap |
| DO-AuditEvent | Sự kiện lưu vết | BO-NhatKyTruyCap |
| DO-Pharmacy | Nhà thuốc (nội bộ/đối tác) | |
| DO-OutboxEvent | Sự kiện chờ phát (outbox, ADR-001) | |
| A: DO-PatientLink, DO-CodeMapping, DO-Consent | Liên kết định danh / Bảng ánh xạ mã / Đồng ý chia sẻ | |
| B: DO-DispenseLedger, DO-SyncBatch | Sổ cái cấp thuốc / Lô đồng bộ | |
| C: DO-PrescriptionVersion, DO-AmendmentReason | Phiên bản đơn / Lý do điều chỉnh | |

## 5. ADR
| Mã | Chủ đề | Người viết |
|---|---|---|
| ADR-001 | Kiểu tích hợp với nhà thuốc / liên cơ sở (theo biến thể) | TV2 |
| ADR-002 | IAM: RBAC + ABAC | TV3 |
| ADR-003 | Audit store | TV3 |
| ADR-004 | Mô hình lưu dữ liệu đơn thuốc (trạng thái, phiên bản, đối soát) | TV2 |

## 6. Gán AS cho task BPMN ngoại lệ (khớp catalog TV1 v0.2 mục 11; chỉ giữ nhóm của biến thể được giao)
| Task | Application Service | Component | Data Object |
|---|---|---|---|
| BP-06A.1 Tìm & ghép định danh (MPI) | AS-MatchPatient | AC-MPI | DO-Patient, DO-PatientLink |
| BP-06A.2 Xác minh thủ công | (thủ công, dùng AI-StaffUI xem ứng viên khớp) | AC-MPI | DO-PatientLink |
| BP-06A.3 Liên kết định danh | AS-MatchPatient | AC-MPI | DO-PatientLink |
| BP-06A.4 Tạo hồ sơ mới tại cơ sở | AS-CheckIn | AC-Reception | DO-Patient |
| BP-06A.5 Yêu cầu xem hồ sơ cơ sở kia | AS-ExchangeRecord | AC-IntegrationHub | DO-Encounter, DO-ClinicalRecord |
| BP-06A.6 Xin đồng ý của BN | AS-RecordConsent | AC-Consent | DO-Consent |
| BP-06A.7 Truy vấn & chuyển đổi về FHIR | AS-ExchangeRecord | AC-IntegrationHub, AC-FhirAdapter-CS1/CS2 | DO-CodeMapping |
| BP-06A.8 Gắn cờ dữ liệu thiếu | AS-ExchangeRecord | AC-IntegrationHub | DO-CodeMapping |
| BP-06B.1 Tra đơn trong bộ nhớ đệm | AS-ReceivePrescription (chế độ offline) | AC-PharmacyAgent | DO-Prescription (bản cache) |
| BP-06B.2 Từ chối cấp, hướng dẫn BN | (thủ công) | — | — |
| BP-06B.3 Cấp có giới hạn, ghi phiếu offline | AS-RecordDispense (offline) | AC-PharmacyAgent | DO-DispenseRecord (source=OFFLINE_SYNC) |
| BP-06B.4 Ghi hàng đợi đồng bộ cục bộ | AS-SyncDispense | AC-PharmacyAgent | DO-SyncBatch |
| BP-06B.5 Đồng bộ bản ghi cấp | AS-SyncDispense | AC-PharmacyAgent → AC-PharmacyGateway | DO-SyncBatch, DO-DispenseRecord |
| BP-06B.6 Đối chiếu với trạng thái đơn | AS-ReconcileDispense | AC-Reconciliation | DO-DispenseLedger, DO-Prescription |
| BP-06B.7 Cập nhật trạng thái đơn & audit | AS-RecordDispense, AS-RecordAudit | AC-ePrescription, AC-Audit | DO-Prescription, DO-AuditEvent |
| BP-06B.8 Đối soát thủ công | AS-ReconcileDispense (hàng CONFLICT) | AC-Reconciliation | DO-DispenseLedger |
| BP-06B.9 Ghi kết quả đối soát | AS-ReconcileDispense, AS-RecordAudit | AC-Reconciliation, AC-Audit | DO-AuditEvent |
| BP-06C.1 Chọn sửa/thu hồi, nhập lý do | AS-AmendPrescription / AS-RevokePrescription | AC-ePrescription | DO-AmendmentReason |
| BP-06C.2 Kiểm tra trạng thái cấp | AS-RevokePrescription | AC-ePrescription | DO-Prescription, DO-DispenseRecord |
| BP-06C.3 Chuyển đơn sang REVOKED | AS-RevokePrescription | AC-ePrescription | DO-Prescription |
| BP-06C.4 Lập phiên bản v+1, kiểm tra, ký | AS-AmendPrescription, AS-CheckDrugSafety | AC-ePrescription | DO-PrescriptionVersion |
| BP-06C.5 Lập đơn điều chỉnh/bổ sung | AS-IssuePrescription | AC-ePrescription | DO-Prescription (mới) |
| BP-06C.6 Phát sự kiện thay đổi & audit | AS-SendPrescription, AS-RecordAudit | AC-PharmacyGateway, AC-Audit | DO-OutboxEvent, DO-AuditEvent |
| BP-06C.7 Chặn đơn cũ / áp dụng bản mới | AS-ReceivePrescription (nhận sự kiện + ack) | AC-PharmacyGateway | DO-Prescription |
| BP-06C.8 Liên hệ nhà thuốc (quá 30 phút) | AS-SendNotification (cảnh báo cho bác sĩ) | AC-Notification | DO-Notification |

AS mới: AS-RecordConsent (AC-Consent, biến thể A).
