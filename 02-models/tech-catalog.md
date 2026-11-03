# Danh mục mã Tầng Công nghệ & Dịch chuyển (TV3) — bản nháp v0.1 (2026-11-03)

> Nguồn sự thật cho mã ND, DV, SW, NW, TS, ART, WP, DLV, PLT, GAP, RSK. TV3 là người duy nhất thêm/đổi tên các mã này.
> Mã AC/AS/DO theo `app-catalog.md` (TV2); FR/NFR/G/BP theo catalog của TV1.
> Quy ước tên trong Archi: "<mã> <tên VN>", ví dụ "ND-AppCluster Cụm máy chủ ứng dụng".
> Lưu ý tránh trùng tiền tố: Gap dùng **GAP-xx** (không dùng G-xx vì G-xx là Goal); Artifact dùng **ART-** (vì AF- đã dùng cho Application Function của TV2).

## 1. Node / Device / System Software (Target)
| Mã | Loại ArchiMate | Tên hiển thị | Vùng mạng | Host cho |
|---|---|---|---|---|
| ND-EdgeGateway | Node | Cụm biên (WAF + cân bằng tải + API Gateway) | DMZ | TS-ApiGateway, TS-SecureChannel |
| ND-AppCluster | Node | Cụm máy chủ ứng dụng (3 VM chạy container) | App | ART của AC-Booking, AC-Reception, AC-EMR, AC-ePrescription, AC-PharmacyGateway, AC-Notification, AC-MasterData, AC-Reporting, AC-PatientPortal (backend), AI-PharmacyWebUI |
| ND-DataCluster | Node | Cụm CSDL (PostgreSQL chính + bản sao dự phòng) | Data | TS-Database |
| ND-MessageBroker | Node | Máy chủ hàng đợi thông điệp | Data | TS-Messaging |
| ND-ObjectStore | Node | Kho lưu trữ đối tượng (có khóa WORM) | Data | TS-ObjectStorage, lưu phân đoạn audit đã niêm phong |
| ND-SecurityPlatform | Node | Nền tảng định danh & chính sách (IdP + PDP) | Security | TS-Identity, TS-PolicyDecision |
| ND-AuditStore | Node | Kho lưu vết append-only | Security | TS-Audit (ADR-003) |
| ND-KeyVault | Node | Quản lý khóa & ký số (KMS/HSM) | Security | TS-KeyManagement, TS-Signing |
| ND-SecOps | Node | Giám sát & SIEM | Mgmt | TS-Monitoring, TS-SIEM |
| ND-BackupDR | Node | Sao lưu & dự phòng thảm họa (vùng thứ 2) | DR | TS-Backup |
| ND-SiteCS1 / ND-SiteCS2 | Node (Location) | Hạ tầng tại cơ sở 1 / cơ sở 2 (LAN phân VLAN, tường lửa, VPN) | Site | DV-* |
| ND-SiteServerCS1 / ND-SiteServerCS2 | Node | Máy chủ tại cơ sở (OS còn hỗ trợ, ảo hóa) cho hệ thống Retain | Site | AC-HisLite-CS1 / AC-ClinicSoft-CS2 |
| ND-PartnerPharmacy | Node (ngoài) | Hạ tầng nhà thuốc đối tác | Partner | EXT-PharmacySystem (B: AC-PharmacyAgent) |
| DV-Workstation | Device | Máy trạm nhân viên | Site | AI-StaffUI (trình duyệt) |
| DV-Kiosk | Device | Kiosk check-in tự phục vụ | Site | AI-StaffUI (chế độ kiosk) |
| DV-IdCardReader | Device | Đầu đọc CCCD gắn chip | Site | dùng bởi AS-CheckIn |
| DV-PatientMobile | Device | Điện thoại bệnh nhân | Internet | AI-PortalUI |
| SW-K8sRuntime | System Software | Nền tảng container (Kubernetes gọn nhẹ, vd k3s) | App | trên ND-AppCluster |
| SW-PostgreSQL | System Software | PostgreSQL 16 | Data | trên ND-DataCluster, ND-AuditStore |
| SW-RabbitMQ | System Software | RabbitMQ (hàng đợi bền) | Data | trên ND-MessageBroker (tùy ADR-001 của TV2) |
| SW-Keycloak | System Software | Keycloak (OIDC/SAML, MFA) | Security | trên ND-SecurityPlatform |
| SW-OPA | System Software | Open Policy Agent (đánh giá chính sách ABAC) | Security | trên ND-SecurityPlatform |
| SW-Wazuh | System Software | Wazuh/ELK (SIEM) | Mgmt | trên ND-SecOps |

> Tên sản phẩm (Keycloak, OPA, PostgreSQL…) chỉ là ví dụ minh họa để lập luận chi phí/độ phức tạp; mô hình ArchiMate chỉ cần System Software ở mức loại.

## 2. Communication Network / Path
| Mã | Loại | Tên | Ghi chú |
|---|---|---|---|
| NW-Internet | Communication Network | Internet (2 nhà mạng tại mỗi cơ sở) | |
| NW-SiteVPN | Path | VPN IPsec cơ sở ↔ trung tâm dữ liệu | CS1, CS2 |
| NW-PartnerChannel | Path | Kênh đối tác mTLS (TLS 1.3, chứng thư 2 chiều) | Nhà thuốc ↔ ND-EdgeGateway |
| NW-LAN-CS1 / NW-LAN-CS2 | Communication Network | LAN phân vùng: VLAN nhân viên, VLAN thiết bị, Wi-Fi khách tách biệt | |
| NW-DCInternal | Communication Network | Mạng nội bộ trung tâm dữ liệu, phân vùng DMZ / App / Data / Security | Tường lửa giữa các vùng |

## 3. Technology Service
| Mã | Tên | Hiện thực bởi | Phục vụ (AC) | NFR chính |
|---|---|---|---|---|
| TS-ApiGateway | Cổng API (định tuyến, rate limit, kiểm tra token, PEP) | ND-EdgeGateway | mọi AC có API | NFR-SEC-02, NFR-PRF-01 |
| TS-SecureChannel | Kênh truyền an toàn (TLS/mTLS/VPN) | ND-EdgeGateway, NW-* | AC-PharmacyGateway, AC-PatientPortal | NFR-SEC-04 |
| TS-Identity | Xác thực & SSO (OIDC, MFA) | ND-SecurityPlatform | AC-IAM | NFR-SEC-01 |
| TS-PolicyDecision | Quyết định quyền truy cập (RBAC+ABAC) | ND-SecurityPlatform | AC-IAM | NFR-SEC-02 |
| TS-Audit | Ghi/tra cứu vết bất biến (hash chain) | ND-AuditStore + ND-ObjectStore | AC-Audit | NFR-SEC-03, NFR-SEC-05 |
| TS-Database | CSDL quan hệ có sao chép | ND-DataCluster | AC nghiệp vụ | NFR-AVL-01, NFR-SEC-04 |
| TS-Messaging | Hàng đợi/sự kiện bền | ND-MessageBroker | AC-PharmacyGateway, AC-Notification, AC-Audit | NFR-AVL-01 |
| TS-ObjectStorage | Lưu trữ đối tượng (WORM) | ND-ObjectStore | AC-Audit, AC-EMR | NFR-SEC-05 |
| TS-KeyManagement | Quản lý khóa mã hóa | ND-KeyVault | TS-Database, TS-Audit | NFR-SEC-04 |
| TS-Signing | Ký số đơn thuốc / niêm phong audit | ND-KeyVault | AC-ePrescription, AC-Audit | CON-03 |
| TS-Monitoring | Giám sát, cảnh báo | ND-SecOps | mọi node | NFR-AVL-01 |
| TS-SIEM | Phát hiện bất thường an ninh | ND-SecOps | AC-Audit (luồng sao) | NFR-SEC-03 |
| TS-Backup | Sao lưu, khôi phục, DR | ND-BackupDR | ND-DataCluster, ND-AuditStore | NFR-AVL-01 (RPO/RTO), NFR-SEC-05 |

## 4. Artifact (ví dụ, dùng ở Implementation & Deployment view)
| Mã | Tên | Hiện thực | Gán cho |
|---|---|---|---|
| ART-booking-svc | Image container booking-svc | AC-Booking | ND-AppCluster |
| ART-erx-svc | Image container erx-svc | AC-ePrescription | ND-AppCluster |
| ART-pharmacy-gw | Image container pharmacy-gw | AC-PharmacyGateway | ND-AppCluster |
| ART-emr-db | Schema emr (CSDL) | DO-Patient, DO-Encounter, DO-ClinicalRecord | SW-PostgreSQL |
| ART-erx-db | Schema erx (CSDL) | DO-Prescription, DO-PrescriptionItem, DO-DispenseRecord | SW-PostgreSQL |
| ART-audit-log | Bảng audit_event phân vùng theo tháng + phân đoạn niêm phong | DO-AuditEvent | ND-AuditStore, ND-ObjectStore |
| ART-abac-policy | Gói chính sách (policy bundle) | DO-AccessPolicy | SW-OPA |

## 5. Dịch chuyển
| Mã | Tên |
|---|---|
| PLT-0 | Hiện trạng (Baseline) |
| PLT-1 | Nền tảng an toàn + Đặt lịch/Tiếp đón số |
| PLT-2 | Bệnh án & Kê đơn điện tử tích hợp |
| PLT-3 | Liên thông nhà thuốc + năng lực biến thể (Target) |
| WP-01 … WP-08 | xem `05-verification/gap-roadmap.md` |
| GAP-01 … | xem `05-verification/gap-roadmap.md` |
| RSK-01 … RSK-08 | xem `05-verification/risk-register.md` |

## 6. NFR/CON mà tầng công nghệ hiện thực (mã theo catalog TV1)
| Mã | Nội dung (tóm tắt) | Hiện thực chính ở tầng công nghệ |
|---|---|---|
| NFR-SEC-01 | MFA nhân viên, OTP bệnh nhân | TS-Identity |
| NFR-SEC-02 | RBAC + ABAC, break-glass | TS-PolicyDecision, TS-ApiGateway (PEP) — ADR-002 |
| NFR-SEC-03 | 100% truy cập có audit bất biến | TS-Audit, TS-ObjectStorage (WORM), TS-SIEM — ADR-003 |
| NFR-SEC-04 | Mã hóa khi truyền/khi lưu | TS-SecureChannel, TS-KeyManagement |
| NFR-SEC-05 | Lưu audit ≥ 10 năm | TS-ObjectStorage, TS-Backup |
| NFR-AVL-01 | 99,5% (6h–21h), RPO ≤ 15', RTO ≤ 4h | ND-AppCluster (3 VM), ND-DataCluster (bản sao), TS-Backup, ND-BackupDR |
| NFR-PRF-01 | p95 ≤ 2 s, 300 người dùng đồng thời | TS-ApiGateway (rate limit), ND-AppCluster (scale ngang), TS-Database (read replica) |
| NFR-INT-01/02 | FHIR R4; thêm đối tác chỉ cấu hình | TS-ApiGateway, NW-PartnerChannel, TS-Messaging |
| NFR-DAT-01 | Không mất/không trùng đơn & bản ghi cấp | TS-Messaging (hàng đợi bền), TS-Database (ràng buộc duy nhất idempotency key) |
| CON-03 | Ký số đơn thuốc | TS-Signing (ND-KeyVault, kết nối CA — mock) |
| CON-07 | Đám mây trong nước / on-prem, ngân sách hạn chế | Chọn đám mây riêng thuê tại VN (mục 3.3 technology.md) |
