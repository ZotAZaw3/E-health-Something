# -*- coding: utf-8 -*-
"""Gộp 2 file Exchange XML (TV1 Motivation/Business + TV3 Technology/Migration) thành MỘT mô hình
và bổ sung các phần còn thiếu: tầng Chiến lược (Ch.7), tầng Ứng dụng & Dữ liệu (TV2, app-catalog.md v0.2),
phần tử ngoại lệ biến thể A/B/C, view phân tầng xuyên suốt dùng cho truy vết.

Chạy:  python3 build_full_model.py      → ehealth-full-model.xml (cùng thư mục)
Nhập vào Archi: File > Import > Open Exchange XML Model.
Mã phần tử lấy đúng theo 3 catalog: 01-vision/catalog.md, 02-models/app-catalog.md, 02-models/tech-catalog.md.
"""
import os, re, sys
from lxml import etree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
TV1 = os.path.join(HERE, '..', 'ehealth-tv1-motivation-business.xml')
TV3 = os.path.join(HERE, 'ehealth-tv3-exchange.xml')
OUT = os.path.join(HERE, 'ehealth-full-model.xml')
NS = 'http://www.opengroup.org/xsd/archimate/3.0/'
XSI = 'http://www.w3.org/2001/XMLSchema-instance'
XML = 'http://www.w3.org/XML/1998/namespace'
q = lambda t: f'{{{NS}}}{t}'
T = f'{{{XSI}}}type'
LANG = f'{{{XML}}}lang'

# TV3 dùng mã tạm cho ứng dụng Baseline; mã chuẩn là của catalog TV1/TV2
ALIAS = {'id-APP-B-HisLite': 'id-AC-HisLite-CS1', 'id-APP-B-ClinicSoft': 'id-AC-ClinicSoft-CS2', 'id-APP-B-Sheet': 'id-AC-BookingSheet'}

elements, rels, views = {}, {}, []   # id -> (type, name, doc) ; id -> (type, src, tgt, extra) ; list of view nodes

def load(path, tag):
    root = ET.parse(path).getroot()
    for e in root.find(q('elements')):
        i = ALIAS.get(e.get('identifier'), e.get('identifier'))
        if i in elements and e.get('identifier') in ALIAS: continue
        n = e.find(q('name')).text
        d = e.find(q('documentation'))
        if i not in elements:
            elements[i] = [e.get(T), n, d.text if d is not None else '']
    for r in root.find(q('relationships')):
        s, t = ALIAS.get(r.get('source'), r.get('source')), ALIAS.get(r.get('target'), r.get('target'))
        extra = {k: v for k, v in r.attrib.items() if k in ('accessType', 'isDirected', 'modifier')}
        rels[r.get('identifier')] = (r.get(T), s, t, extra)
    for v in root.find(q('views')).find(q('diagrams')):
        for n in v.iter(q('node')):
            if n.get('elementRef') in ALIAS: n.set('elementRef', ALIAS[n.get('elementRef')])
        views.append(v)

load(TV1, 'tv1'); load(TV3, 'tv3')
VREN = {'id-v1': 'V-TECH-0', 'id-v2': 'V-TECH-1', 'id-v3': 'V-TECH-2', 'id-v4': 'V-TECH-3', 'id-v5': 'V-MIG-1', 'id-v6': 'V-MIG-2', 'id-v7': 'V-MIG-3'}
for v in views:
    if v.get('identifier') in VREN: v.set('identifier', VREN[v.get('identifier')])

# Tên chuẩn theo app-catalog (TV2) cho phần tử ứng dụng mà TV1/TV3 đặt hơi khác nhau
def el(code, typ, name, doc=''):
    i = 'id-' + code.replace('.', '_')
    if i in elements:
        elements[i][1] = f'{code} {name}'
        if doc: elements[i][2] = doc
    else:
        elements[i] = [typ, f'{code} {name}', doc]
    return i

_rc = [0]
_seen = {(t, s, d) for (t, s, d, _) in rels.values()}
def rel(typ, s, d, **extra):
    si, di = 'id-' + s.replace('.', '_'), 'id-' + d.replace('.', '_')
    for x in (si, di):
        if x not in elements: sys.exit(f'Thiếu phần tử {x} cho quan hệ {typ} {s}->{d}')
    if (typ, si, di) in _seen: return
    _seen.add((typ, si, di)); _rc[0] += 1
    rels[f'id-x{_rc[0]}'] = (typ, si, di, extra)

# ======================= 1. Bổ sung phần tử TV1 còn thiếu trong file Archi =======================
el('BA-CoQuanQuanLyDuoc', 'BusinessActor', 'Bộ/Sở Y tế (quản lý dược)')
el('BO-DongYChiaSe', 'BusinessObject', 'Đồng ý chia sẻ hồ sơ', 'Chỉ dùng với biến thể A')
for c, n in [('BP-06A', 'Xử lý định danh/hồ sơ liên cơ sở (ngoại lệ biến thể A)'),
             ('BP-06B', 'Cấp thuốc khi mất kết nối & đối soát (ngoại lệ biến thể B)'),
             ('BP-06C', 'Điều chỉnh/thu hồi đơn (ngoại lệ biến thể C)')]:
    el(c, 'BusinessProcess', n, 'Ngoại lệ theo biến thể — chỉ giữ biến thể được giao trong báo cáo; xem BPMN-02' + c[-1])
TASKS = {
 'BP-06A.1': 'Tìm & ghép định danh liên cơ sở (MPI)', 'BP-06A.2': 'Xác minh thủ công', 'BP-06A.3': 'Liên kết định danh',
 'BP-06A.5': 'Yêu cầu xem hồ sơ cơ sở kia', 'BP-06A.6': 'Xin đồng ý của BN', 'BP-06A.7': 'Truy vấn & chuyển đổi về FHIR',
 'BP-06B.1': 'Tra đơn trong bộ nhớ đệm', 'BP-06B.3': 'Cấp có giới hạn, ghi phiếu offline', 'BP-06B.5': 'Đồng bộ bản ghi cấp (idempotent)',
 'BP-06B.6': 'Đối chiếu với trạng thái đơn', 'BP-06B.8': 'Đối soát thủ công',
 'BP-06C.1': 'Chọn sửa/thu hồi, nhập lý do', 'BP-06C.2': 'Kiểm tra trạng thái cấp', 'BP-06C.3': 'Chuyển đơn sang REVOKED',
 'BP-06C.4': 'Lập phiên bản v+1, kiểm tra, ký số', 'BP-06C.6': 'Phát sự kiện thay đổi & ghi audit', 'BP-06C.7': 'Chặn đơn cũ / áp dụng bản mới'}
for c, n in TASKS.items():
    el(c, 'BusinessProcess', n); rel('Composition', c[:6], c)
for a, b in [('BP-06A', 'BP-02'), ('BP-06A', 'BP-03'), ('BP-06B', 'BP-05'), ('BP-06C', 'BP-04')]:
    rel('Association', a, b)
for c, n, g, bp in [('FR-A1', 'Ghép định danh BN giữa CS1/CS2', 'G-05', 'BP-06A'), ('FR-A2', 'Xem hồ sơ liên cơ sở qua mô hình chuẩn', 'G-05', 'BP-06A'),
                    ('FR-A3', 'Đồng ý (consent) khi xem hồ sơ cơ sở kia', 'G-03', 'BP-06A'),
                    ('FR-B1', 'Cấp thuốc khi mất kết nối theo đơn đã cache, có giới hạn', 'G-04', 'BP-06B'),
                    ('FR-B2', 'Đồng bộ lại và đối chiếu bản ghi cấp', 'G-04', 'BP-06B'), ('FR-B3', 'Phát hiện, chặn, xử lý cấp trùng', 'G-02', 'BP-06B'),
                    ('FR-C1', 'Sửa đơn tạo phiên bản mới, không ghi đè', 'G-02', 'BP-06C'), ('FR-C2', 'Thu hồi đơn theo trạng thái cấp', 'G-02', 'BP-06C'),
                    ('FR-C3', 'Thông báo thay đổi đơn tới nhà thuốc và BN', 'G-04', 'BP-06C')]:
    el(c, 'Requirement', n, 'Yêu cầu theo biến thể ' + c[3]); rel('Realization', c, g); rel('Realization', bp, c)

# ======================= 2. Tầng Chiến lược (Ch.7) =======================
CAPS = [('CAP-00', 'Khám chữa bệnh ngoại trú (năng lực tổng)', ''),
        ('CAP-01', 'Quản lý lịch hẹn & điều phối công suất', 'Khoảng trống: MỚI (hiện chỉ có hotline + Google Sheet)'),
        ('CAP-02', 'Tiếp nhận & định danh người bệnh', 'Khoảng trống: NÂNG CẤP (nhập tay → QR/CCCD)'),
        ('CAP-03', 'Khám & quản lý hồ sơ lâm sàng', 'Khoảng trống: NÂNG CẤP (giấy → điện tử)'),
        ('CAP-04', 'Kê đơn an toàn', 'Khoảng trống: MỚI (chưa có kiểm tra an toàn; CS2 chưa kê đơn điện tử)'),
        ('CAP-05', 'Liên thông đơn thuốc & cấp thuốc', 'Khoảng trống: MỚI'),
        ('CAP-06', 'Kiểm soát truy cập & lưu vết', 'Khoảng trống: MỚI (tài khoản chung, không có log)'),
        ('CAP-07', 'Quản trị dữ liệu người bệnh liên cơ sở', 'Khoảng trống: MỚI — trọng tâm biến thể A'),
        ('CAP-08', 'Đo lường & cải tiến vận hành', 'Khoảng trống: NÂNG CẤP'),
        ('CAP-09', 'Thanh toán & giám định BHYT', 'Khoảng trống: GIỮ (Retain, ASSUMP-06)')]
for c, n, d in CAPS: el(c, 'Capability', n, d)
for c, _, _ in CAPS[1:]: rel('Composition', 'CAP-00', c)
for bp, cap in [('BP-01', 'CAP-01'), ('BP-02', 'CAP-02'), ('BP-03', 'CAP-03'), ('BP-04', 'CAP-04'), ('BP-05', 'CAP-05'),
                ('BF-01', 'CAP-06'), ('BP-06A', 'CAP-07'), ('BF-02', 'CAP-08'), ('BP0-05', 'CAP-09')]:
    rel('Realization', bp, cap)
RES = [('RS-01', 'Đội ngũ y tế (bác sĩ, điều dưỡng, dược sĩ)', ['BR-BacSi', 'BR-DieuDuong', 'BR-DuocSi'], ['CAP-03', 'CAP-04', 'CAP-05']),
       ('RS-02', 'Dữ liệu người bệnh & đơn thuốc', [], ['CAP-03', 'CAP-04', 'CAP-07']),
       ('RS-03', 'Nền tảng số dùng chung (ứng dụng + hạ tầng)', ['ND-AppCluster', 'ND-DataCluster'], ['CAP-01', 'CAP-02', 'CAP-05', 'CAP-06', 'CAP-08']),
       ('RS-04', 'Mạng lưới nhà thuốc liên kết (2 nội bộ + 6 đối tác)', ['BA-NhaThuocDoiTac', 'BA-NhaThuocNoiBo'], ['CAP-05'])]
for c, n, by, caps in RES:
    el(c, 'Resource', n)
    for b in by: rel('Realization', b, c)
    for cap in caps: rel('Assignment', c, cap)
COA = [('COA-01', 'Tuân thủ trước, tối ưu sau: bảo mật + kê đơn điện tử ở PLT-1', ['G-02', 'G-03'], ['CAP-04', 'CAP-06']),
       ('COA-02', 'Số hóa đầu vào để giảm chờ: đặt lịch, check-in QR/CCCD', ['G-01'], ['CAP-01', 'CAP-02']),
       ('COA-03', 'Liên thông qua cổng chuẩn, không buộc đối tác đổi phần mềm', ['G-04'], ['CAP-05']),
       ('COA-04', 'Một hồ sơ người bệnh dùng chung cho 2 cơ sở', ['G-05'], ['CAP-03', 'CAP-07'])]
for c, n, goals, caps in COA:
    el(c, 'CourseOfAction', n)
    for g in goals: rel('Realization', c, g)
    for cap in caps: rel('Association', c, cap)
el('VAL-01', 'Value', 'Được khám đúng hẹn, nhận thuốc đúng và an toàn')
el('VS-01', 'ValueStream', 'Khám ngoại trú đến khi nhận thuốc')
STAGES = [('VS-01.1', 'Hẹn khám', 'BP-01', 'CAP-01'), ('VS-01.2', 'Tiếp đón', 'BP-02', 'CAP-02'), ('VS-01.3', 'Khám & chẩn đoán', 'BP-03', 'CAP-03'),
          ('VS-01.4', 'Kê đơn an toàn', 'BP-04', 'CAP-04'), ('VS-01.5', 'Nhận thuốc', 'BP-05', 'CAP-05')]
for i, (c, n, bp, cap) in enumerate(STAGES):
    el(c, 'ValueStream', n); rel('Composition', 'VS-01', c); rel('Realization', bp, c); rel('Serving', cap, c)
    if i: rel('Flow', STAGES[i - 1][0], c)
rel('Serving', 'CAP-06', 'VS-01'); rel('Association', 'VS-01', 'VAL-01'); rel('Association', 'VAL-01', 'SH-01')

# ======================= 3. Tầng Ứng dụng (TV2, app-catalog v0.2) =======================
AC = [('AC-PatientPortal', 'Cổng bệnh nhân (web/app)'), ('AC-Booking', 'Quản lý lịch hẹn'), ('AC-Reception', 'Tiếp đón'),
      ('AC-EMR', 'Hồ sơ bệnh án điện tử'), ('AC-ePrescription', 'Kê đơn điện tử'), ('AC-PharmacyGateway', 'Cổng kết nối nhà thuốc'),
      ('AC-Notification', 'Thông báo'), ('AC-IAM', 'Định danh & phân quyền'), ('AC-Audit', 'Lưu vết'),
      ('AC-MasterData', 'Danh mục dùng chung'), ('AC-Reporting', 'Báo cáo vận hành'),
      ('AC-HisLite-CS1', 'HIS-Lite tại CS1 (Retain: thu ngân/BHYT)'), ('AC-ClinicSoft-CS2', 'ClinicSoft tại CS2 (Retain: thu ngân/BHYT)'),
      ('AC-BookingSheet', 'Google Sheet lịch hẹn (Baseline, Eliminate)'),
      ('EXT-PharmacySystem', 'Phần mềm nhà thuốc đối tác (ngoài)'), ('EXT-InsurancePortal', 'Cổng giám định BHYT (mock)'),
      ('EXT-SmsGateway', 'Nhà cung cấp SMS/OTP (ngoài)'), ('EXT-NationalRxSystem', 'Hệ thống đơn thuốc quốc gia (mock)')]
for c, n in AC: el(c, 'ApplicationComponent', n)
el('GRP-CoreApps', 'Grouping', 'Ứng dụng nghiệp vụ lõi (Target)')
CORE = ['AC-PatientPortal', 'AC-Booking', 'AC-Reception', 'AC-EMR', 'AC-ePrescription', 'AC-PharmacyGateway', 'AC-Notification', 'AC-Reporting']
for c in CORE: rel('Aggregation', 'GRP-CoreApps', c)
for c in ['AC-IAM', 'AC-Audit', 'AC-MasterData']: rel('Serving', c, 'GRP-CoreApps')

AS = [('AS-BookAppointment', 'Đặt lịch khám', 'AC-Booking', ['BP-01.1', 'BP-01.2']),
      ('AS-CancelAppointment', 'Hủy/đổi lịch khám', 'AC-Booking', ['BP-01']),
      ('AS-CheckIn', 'Tiếp nhận check-in, mở lượt khám', 'AC-Reception', ['BP-02.1', 'BP-02.3']),
      ('AS-VerifyInsurance', 'Xác minh danh tính & thẻ BHYT', 'AC-Reception', ['BP-02.2']),
      ('AS-ViewMedicalRecord', 'Tra cứu hồ sơ bệnh án', 'AC-EMR', ['BP-03.2']),
      ('AS-RecordEncounter', 'Ghi nhận khám (sinh hiệu, chẩn đoán ICD-10)', 'AC-EMR', ['BP-03.1', 'BP-03.3']),
      ('AS-IssuePrescription', 'Lập, ký số & phát hành đơn', 'AC-ePrescription', ['BP-04.1', 'BP-04.3']),
      ('AS-CheckDrugSafety', 'Kiểm tra dị ứng/tương tác/trùng hoạt chất/liều', 'AC-ePrescription', ['BP-04.2']),
      ('AS-SendPrescription', 'Gửi đơn tới nhà thuốc', 'AC-PharmacyGateway', ['BP-04.4']),
      ('AS-SubmitNationalRx', 'Gửi đơn lên Hệ thống đơn thuốc quốc gia', 'AC-PharmacyGateway', ['BP-04.4']),
      ('AS-ReceivePrescription', 'Nhận/tra cứu đơn theo mã tại nhà thuốc', 'AC-PharmacyGateway', ['BP-05.1']),
      ('AS-RecordDispense', 'Ghi nhận cấp thuốc toàn phần/một phần', 'AC-PharmacyGateway', ['BP-05.3']),
      ('AS-SendNotification', 'Gửi thông báo', 'AC-Notification', ['BP-01.3', 'BP-04.4', 'BP-05.3']),
      ('AS-ReportOperations', 'Báo cáo vận hành (đo Outcome)', 'AC-Reporting', ['BF-02']),
      ('AS-Authenticate', 'Xác thực', 'AC-IAM', ['BF-01']), ('AS-Authorize', 'Phân quyền RBAC+ABAC', 'AC-IAM', ['BF-01']),
      ('AS-RecordAudit', 'Ghi vết', 'AC-Audit', ['BF-01']), ('AS-QueryAudit', 'Tra cứu vết', 'AC-Audit', ['BF-01'])]
for c, n, ac, bps in AS:
    el(c, 'ApplicationService', n); rel('Realization', ac, c)
    for b in bps: rel('Serving', c, b)
AI = [('AI-PortalUI', 'Giao diện web/app bệnh nhân', ['AC-PatientPortal'], ['BR-BenhNhan']),
      ('AI-StaffUI', 'Giao diện web nhân viên', ['AC-Reception', 'AC-EMR', 'AC-ePrescription'], ['BR-LeTan', 'BR-DieuDuong', 'BR-BacSi']),
      ('AI-PrescriptionAPI', 'API đơn thuốc (REST/FHIR MedicationRequest)', ['AC-ePrescription'], []),
      ('AI-PharmacyAPI', 'API nhà thuốc (REST/FHIR + webhook)', ['AC-PharmacyGateway'], []),
      ('AI-PharmacyWebUI', 'Cổng web nhà thuốc', ['AC-PharmacyGateway'], ['BR-DuocSi']),
      ('AI-EventChannel', 'Kênh sự kiện (publish/subscribe)', ['AC-PharmacyGateway'], [])]
for c, n, acs, roles in AI:
    el(c, 'ApplicationInterface', n)
    for a in acs: rel('Composition' if len(acs) == 1 else 'Aggregation', a, c)
    for r in roles: rel('Serving', c, r)
rel('Serving', 'AI-PharmacyAPI', 'EXT-PharmacySystem')
# Hợp tác ứng dụng (flow = dữ liệu chảy, serving = dùng dịch vụ)
for typ, a, b in [('Flow', 'AC-Booking', 'AC-Reception'), ('Flow', 'AC-Reception', 'AC-EMR'), ('Serving', 'AC-EMR', 'AC-ePrescription'),
                  ('Flow', 'AC-ePrescription', 'AC-PharmacyGateway'), ('Flow', 'AC-PharmacyGateway', 'EXT-NationalRxSystem'),
                  ('Flow', 'AC-PharmacyGateway', 'EXT-PharmacySystem'), ('Flow', 'EXT-PharmacySystem', 'AC-PharmacyGateway'),
                  ('Serving', 'AC-Booking', 'AC-PatientPortal'), ('Serving', 'AC-Notification', 'AC-PatientPortal'),
                  ('Serving', 'EXT-SmsGateway', 'AC-Notification'), ('Serving', 'EXT-InsurancePortal', 'AC-Reception'),
                  ('Flow', 'AC-ePrescription', 'AC-Notification'), ('Flow', 'AC-PharmacyGateway', 'AC-Notification'),
                  ('Flow', 'AC-Reception', 'AC-HisLite-CS1'), ('Flow', 'AC-Reception', 'AC-ClinicSoft-CS2'),
                  ('Flow', 'AC-ePrescription', 'AC-HisLite-CS1'), ('Flow', 'AC-ePrescription', 'AC-ClinicSoft-CS2'),
                  ('Serving', 'AC-MasterData', 'AC-ePrescription'), ('Flow', 'AC-PharmacyGateway', 'AC-ePrescription'),
                  ('Flow', 'AC-Booking', 'AC-Reporting'), ('Flow', 'AC-Reception', 'AC-Reporting'), ('Flow', 'AC-ePrescription', 'AC-Reporting')]:
    rel(typ, a, b)
# Baseline: tích hợp thủ công
for a, b in [('AC-BookingSheet', 'AC-HisLite-CS1'), ('AC-BookingSheet', 'AC-ClinicSoft-CS2'), ('AC-HisLite-CS1', 'EXT-NationalRxSystem')]:
    rel('Association', a, b)
rel('Serving', 'EXT-InsurancePortal', 'AC-HisLite-CS1'); rel('Serving', 'EXT-InsurancePortal', 'AC-ClinicSoft-CS2')

# ======================= 4. Dữ liệu (Data Object) =======================
DO = [('DO-Patient', 'Bệnh nhân', 'BO-HoSoBenhNhan'), ('DO-Practitioner', 'Nhân viên y tế', None), ('DO-Appointment', 'Lịch hẹn', 'BO-LichHen'),
      ('DO-Encounter', 'Lượt khám', 'BO-LuotKham'), ('DO-ClinicalRecord', 'Ghi nhận lâm sàng (chẩn đoán, dị ứng)', 'BO-BenhAnNgoaiTru'),
      ('DO-Insurance', 'Thẻ BHYT', 'BO-TheBHYT'), ('DO-Prescription', 'Đơn thuốc', 'BO-DonThuoc'), ('DO-PrescriptionItem', 'Dòng thuốc trong đơn', 'BO-DonThuoc'),
      ('DO-Drug', 'Danh mục thuốc', None), ('DO-DispenseRecord', 'Bản ghi cấp thuốc', 'BO-PhieuCapThuoc'), ('DO-Notification', 'Thông báo', None),
      ('DO-AccessPolicy', 'Chính sách truy cập', 'BO-ChinhSachTruyCap'), ('DO-AuditEvent', 'Sự kiện lưu vết', 'BO-NhatKyTruyCap'),
      ('DO-Pharmacy', 'Nhà thuốc (nội bộ/đối tác)', None), ('DO-OutboxEvent', 'Sự kiện chờ phát (outbox, ADR-001)', None)]
for c, n, bo in DO:
    el(c, 'DataObject', n)
    if bo: rel('Realization', c, bo)
rel('Composition', 'DO-Prescription', 'DO-PrescriptionItem')
for a, b in [('DO-PrescriptionItem', 'DO-Drug'), ('DO-Prescription', 'DO-Encounter'), ('DO-Encounter', 'DO-Patient'), ('DO-Insurance', 'DO-Patient'),
             ('DO-Appointment', 'DO-Patient'), ('DO-ClinicalRecord', 'DO-Encounter'), ('DO-DispenseRecord', 'DO-Prescription'),
             ('DO-DispenseRecord', 'DO-Pharmacy'), ('DO-AuditEvent', 'DO-Practitioner'), ('DO-OutboxEvent', 'DO-Prescription'),
             ('DO-Notification', 'DO-Patient'), ('DO-Encounter', 'DO-Practitioner'), ('DO-Prescription', 'DO-Practitioner')]:
    rel('Association', a, b)
ACCESS = {'AC-Booking': [('DO-Appointment', 'ReadWrite')], 'AC-PatientPortal': [('DO-Appointment', 'Read'), ('DO-Prescription', 'Read')],
          'AC-Reception': [('DO-Patient', 'ReadWrite'), ('DO-Encounter', 'Write'), ('DO-Insurance', 'ReadWrite'), ('DO-Appointment', 'Read')],
          'AC-EMR': [('DO-Patient', 'Read'), ('DO-Encounter', 'ReadWrite'), ('DO-ClinicalRecord', 'ReadWrite')],
          'AC-ePrescription': [('DO-Prescription', 'ReadWrite'), ('DO-PrescriptionItem', 'ReadWrite'), ('DO-ClinicalRecord', 'Read'), ('DO-OutboxEvent', 'Write')],
          'AC-PharmacyGateway': [('DO-Prescription', 'Read'), ('DO-DispenseRecord', 'ReadWrite'), ('DO-OutboxEvent', 'ReadWrite'), ('DO-Pharmacy', 'Read')],
          'AC-Notification': [('DO-Notification', 'ReadWrite')], 'AC-IAM': [('DO-AccessPolicy', 'Read'), ('DO-Practitioner', 'Read')],
          'AC-Audit': [('DO-AuditEvent', 'ReadWrite')], 'AC-MasterData': [('DO-Drug', 'ReadWrite'), ('DO-Practitioner', 'ReadWrite'), ('DO-Pharmacy', 'ReadWrite')],
          'AC-Reporting': [('DO-Appointment', 'Read'), ('DO-Encounter', 'Read'), ('DO-Prescription', 'Read')]}
for ac, lst in ACCESS.items():
    for d, a in lst: rel('Access', ac, d, accessType=a)

# ======================= 5. Biến thể A/B/C (chỉ giữ biến thể được giao khi viết báo cáo) =======================
VAR = {
 'A': dict(ac=[('AC-IntegrationHub', 'Trục tích hợp liên cơ sở'), ('AC-FhirAdapter-CS1', 'Bộ chuyển đổi FHIR CS1'), ('AC-FhirAdapter-CS2', 'Bộ chuyển đổi FHIR CS2'),
               ('AC-MPI', 'Chỉ mục bệnh nhân chủ (MPI)'), ('AC-Consent', 'Quản lý đồng ý chia sẻ hồ sơ')],
           as_=[('AS-MatchPatient', 'Ghép định danh', 'AC-MPI', ['BP-06A.1', 'BP-06A.3']), ('AS-ExchangeRecord', 'Trao đổi hồ sơ liên cơ sở', 'AC-IntegrationHub', ['BP-06A.5', 'BP-06A.7']),
                ('AS-RecordConsent', 'Ghi nhận đồng ý', 'AC-Consent', ['BP-06A.6'])],
           do=[('DO-PatientLink', 'Liên kết định danh', None), ('DO-CodeMapping', 'Bảng ánh xạ mã', None), ('DO-Consent', 'Đồng ý chia sẻ', 'BO-DongYChiaSe')]),
 'B': dict(ac=[('AC-PharmacyAgent', 'Tác tử nhà thuốc (offline-first, cache đơn)'), ('AC-Reconciliation', 'Đối soát cấp thuốc')],
           as_=[('AS-SyncDispense', 'Đồng bộ cấp thuốc', 'AC-PharmacyAgent', ['BP-06B.5']), ('AS-ReconcileDispense', 'Đối soát', 'AC-Reconciliation', ['BP-06B.6', 'BP-06B.8'])],
           do=[('DO-DispenseLedger', 'Sổ cái cấp thuốc', None), ('DO-SyncBatch', 'Lô đồng bộ', None)]),
 'C': dict(ac=[], as_=[('AS-AmendPrescription', 'Điều chỉnh đơn (phiên bản v+1)', 'AF-PrescriptionVersioning', ['BP-06C.1', 'BP-06C.4']),
                       ('AS-RevokePrescription', 'Thu hồi đơn', 'AF-PrescriptionVersioning', ['BP-06C.2', 'BP-06C.3'])],
           do=[('DO-PrescriptionVersion', 'Phiên bản đơn', None), ('DO-AmendmentReason', 'Lý do điều chỉnh', None)])}
el('AF-PrescriptionVersioning', 'ApplicationFunction', 'Quản lý phiên bản đơn', 'Biến thể C — chức năng trong AC-ePrescription')
rel('Assignment', 'AC-ePrescription', 'AF-PrescriptionVersioning')
for v, d in VAR.items():
    for c, n in d['ac']: el(c, 'ApplicationComponent', n, f'Chỉ dùng với biến thể {v}')
    for c, n, ac, bps in d['as_']:
        el(c, 'ApplicationService', n, f'Biến thể {v}'); rel('Realization', ac, c)
        for b in bps: rel('Serving', c, b)
    for c, n, bo in d['do']:
        el(c, 'DataObject', n, f'Biến thể {v}')
        if bo: rel('Realization', c, bo)
# A
for a in ['AC-FhirAdapter-CS1', 'AC-FhirAdapter-CS2', 'AC-MPI', 'AC-Consent']: rel('Serving', a, 'AC-IntegrationHub')
rel('Serving', 'AC-HisLite-CS1', 'AC-FhirAdapter-CS1'); rel('Serving', 'AC-ClinicSoft-CS2', 'AC-FhirAdapter-CS2')
rel('Serving', 'AC-IntegrationHub', 'AC-EMR'); rel('Serving', 'AC-MPI', 'AC-Reception')
rel('Access', 'AC-MPI', 'DO-PatientLink', accessType='ReadWrite'); rel('Access', 'AC-IntegrationHub', 'DO-CodeMapping', accessType='Read')
rel('Access', 'AC-Consent', 'DO-Consent', accessType='ReadWrite'); rel('Aggregation', 'DO-PatientLink', 'DO-Patient'); rel('Association', 'DO-Consent', 'DO-Patient')
rel('Realization', 'AS-MatchPatient', 'FR-A1'); rel('Realization', 'AS-ExchangeRecord', 'FR-A2'); rel('Realization', 'AS-RecordConsent', 'FR-A3')
# B
rel('Flow', 'AC-PharmacyAgent', 'AC-PharmacyGateway'); rel('Serving', 'AC-PharmacyAgent', 'EXT-PharmacySystem'); rel('Serving', 'AC-Reconciliation', 'AC-PharmacyGateway')
rel('Access', 'AC-PharmacyAgent', 'DO-SyncBatch', accessType='ReadWrite'); rel('Access', 'AC-PharmacyAgent', 'DO-Prescription', accessType='Read')
rel('Access', 'AC-Reconciliation', 'DO-DispenseLedger', accessType='ReadWrite')
rel('Aggregation', 'DO-DispenseLedger', 'DO-DispenseRecord'); rel('Aggregation', 'DO-SyncBatch', 'DO-DispenseRecord')
rel('Realization', 'AS-ReconcileDispense', 'FR-B3'); rel('Realization', 'AS-SyncDispense', 'FR-B2')
# C
rel('Composition', 'DO-Prescription', 'DO-PrescriptionVersion'); rel('Association', 'DO-AmendmentReason', 'DO-PrescriptionVersion')
rel('Access', 'AF-PrescriptionVersioning', 'DO-PrescriptionVersion', accessType='ReadWrite'); rel('Access', 'AF-PrescriptionVersioning', 'DO-AmendmentReason', accessType='Write')
rel('Realization', 'AS-AmendPrescription', 'FR-C1'); rel('Realization', 'AS-RevokePrescription', 'FR-C2'); rel('Flow', 'AF-PrescriptionVersioning', 'AC-PharmacyGateway')

# ======================= 6. Liên kết xuyên tầng để truy vết (RTM) =======================
for a, b in [('AS-IssuePrescription', 'FR-05'), ('AS-CheckDrugSafety', 'FR-05'), ('AS-SubmitNationalRx', 'FR-06'), ('AS-SendPrescription', 'FR-06'),
             ('AS-RecordDispense', 'FR-07'), ('AS-BookAppointment', 'FR-01'), ('AS-Authorize', 'FR-08'), ('AS-RecordAudit', 'FR-09'),
             ('AC-Audit', 'NFR-SEC-03'), ('AC-IAM', 'NFR-SEC-02'), ('TS-Audit', 'NFR-SEC-03'), ('TS-PolicyDecision', 'NFR-SEC-02'),
             ('TS-Signing', 'CON-03'), ('TS-Messaging', 'NFR-DAT-01'), ('AS-RecordDispense', 'NFR-DAT-01')]:
    rel('Realization', a, b)
for a, b in [('AS-RecordAudit', 'BP-04.3'), ('AS-Authorize', 'BP-03.2'), ('AS-Authorize', 'BP-04.1')]:
    rel('Serving', a, b)
rel('Access', 'BP-04', 'BO-DonThuoc', accessType='Write')
rel('Serving', 'BS-04', 'BR-BenhNhan')

# ======================= 7. Views mới =======================
W, H = 175, 62
def band_view(vid, name, bands, doc='', vw=None):
    """bands: list of (label, [codes], cols). Trả về element <view> với Container theo dải (layer)."""
    v = ET.Element(q('view'), {'identifier': vid, T: 'Diagram'})
    ET.SubElement(v, q('name'), {LANG: 'vi'}).text = name
    if doc: ET.SubElement(v, q('documentation'), {LANG: 'vi'}).text = doc
    y, placed, k = 10, {}, 0
    maxcols = max(c for _, _, c in bands)
    width = vw or (maxcols * (W + 20) + 30)
    for bi, (label, codes, cols) in enumerate(bands):
        rows = (len(codes) + cols - 1) // cols
        h = rows * (H + 20) + 35
        if codes and elements.get('id-' + codes[0], [''])[0] == 'Grouping':   # dải chính là phần tử Grouping → lồng các phần tử con vào
            gid = 'id-' + codes[0]; codes = codes[1:]
            rows = (len(codes) + cols - 1) // cols; h = rows * (H + 20) + 35
            g = ET.SubElement(v, q('node'), {'identifier': f'{vid}-b{bi}', 'elementRef': gid, T: 'Element', 'x': '10', 'y': str(y), 'w': str(width), 'h': str(h)})
            placed[gid] = f'{vid}-b{bi}'
        else:
            g = ET.SubElement(v, q('node'), {'identifier': f'{vid}-b{bi}', T: 'Container', 'x': '10', 'y': str(y), 'w': str(width), 'h': str(h)})
            ET.SubElement(g, q('label'), {LANG: 'vi'}).text = label
        off = (width - cols * (W + 20) + 20) // 2 if len(codes) >= cols else (width - len(codes) * (W + 20) + 20) // 2
        for i, c in enumerate(codes):
            eid = 'id-' + c.replace('.', '_')
            if eid not in elements: sys.exit(f'View {vid}: thiếu {c}')
            k += 1; nid = f'{vid}-n{k}'; placed[eid] = nid
            ET.SubElement(g, q('node'), {'identifier': nid, 'elementRef': eid, T: 'Element',
                                         'x': str(10 + off + (i % cols) * (W + 20)), 'y': str(y + 28 + (i // cols) * (H + 20)), 'w': str(W), 'h': str(H)})
        y += h + 15
    for rid, (t, s, d, _) in rels.items():
        if s in placed and d in placed:
            ET.SubElement(v, q('connection'), {'identifier': f'{vid}-{rid}', 'relationshipRef': rid, T: 'Relationship', 'source': placed[s], 'target': placed[d]})
    return v

NEWVIEWS = [
 ('V-STR-1', 'Chiến lược 1 – Bản đồ năng lực (Capability Map, có mức khoảng trống)', [
     ('Năng lực tổng', ['CAP-00'], 1),
     ('Năng lực lõi khám chữa bệnh', ['CAP-01', 'CAP-02', 'CAP-03', 'CAP-04', 'CAP-05'], 5),
     ('Năng lực hỗ trợ / quản trị', ['CAP-06', 'CAP-07', 'CAP-08', 'CAP-09'], 4)],
  'Mức khoảng trống ghi ở documentation của từng Capability: MỚI / NÂNG CẤP / GIỮ.'),
 ('V-STR-2', 'Chiến lược 2 – Hoạch định năng lực (Goal ← Course of Action → Capability ← Resource, Business)', [
     ('Motivation', ['G-01', 'G-02', 'G-03', 'G-04', 'G-05'], 5),
     ('Lộ trình hành động (Course of Action)', ['COA-01', 'COA-02', 'COA-03', 'COA-04'], 4),
     ('Năng lực', ['CAP-01', 'CAP-02', 'CAP-03', 'CAP-04', 'CAP-05', 'CAP-06', 'CAP-07'], 7),
     ('Tài nguyên', ['RS-01', 'RS-02', 'RS-03', 'RS-04'], 4),
     ('Hiện thực hóa bởi Business', ['BP-01', 'BP-02', 'BP-03', 'BP-04', 'BP-05', 'BF-01', 'BP-06A'], 7)], ''),
 ('V-STR-3', 'Chiến lược 3 – Luồng giá trị “Khám ngoại trú đến khi nhận thuốc”', [
     ('Giá trị cho bên liên quan', ['SH-01', 'VAL-01', 'VS-01'], 3),
     ('Công đoạn luồng giá trị', [s[0] for s in STAGES], 5),
     ('Năng lực phục vụ', ['CAP-01', 'CAP-02', 'CAP-03', 'CAP-04', 'CAP-05'], 5),
     ('Quy trình hiện thực', ['BP-01', 'BP-02', 'BP-03', 'BP-04', 'BP-05'], 5)], ''),
 ('V-APP-0', 'Ứng dụng Baseline (As-Is, PLT-0)', [
     ('Người dùng', ['BR-LeTan', 'BR-BacSi', 'BR-ThuNgan'], 3),
     ('Ứng dụng hiện có', ['AC-BookingSheet', 'AC-HisLite-CS1', 'AC-ClinicSoft-CS2'], 3),
     ('Hệ thống ngoài', ['EXT-InsurancePortal', 'EXT-NationalRxSystem'], 2)],
  'HIS-Lite và ClinicSoft khác cấu trúc dữ liệu, khác mã BN; liên thông đơn quốc gia nhập tay; Google Sheet giữ lịch hẹn.'),
 ('V-APP-1', 'Ứng dụng Target – Hợp tác ứng dụng (Application Cooperation)', [
     ('Kênh / giao diện', ['AI-PortalUI', 'AI-StaffUI', 'AI-PharmacyWebUI', 'AI-PharmacyAPI'], 4),
     ('Ứng dụng nghiệp vụ lõi', ['GRP-CoreApps', 'AC-PatientPortal', 'AC-Booking', 'AC-Reception', 'AC-EMR', 'AC-ePrescription', 'AC-PharmacyGateway', 'AC-Notification', 'AC-Reporting'], 5),
     ('Ứng dụng nền dùng chung', ['AC-IAM', 'AC-Audit', 'AC-MasterData'], 3),
     ('Giữ lại (Retain) và hệ thống ngoài (mock)', ['AC-HisLite-CS1', 'AC-ClinicSoft-CS2', 'EXT-InsurancePortal', 'EXT-NationalRxSystem', 'EXT-PharmacySystem', 'EXT-SmsGateway'], 6)], ''),
 ('V-APP-2', 'Ứng dụng Target – Sử dụng ứng dụng (Application Usage, khớp task BPMN-01)', [
     ('Quy trình (task BPMN)', ['BP-01.1', 'BP-01.2', 'BP-02.1', 'BP-02.2', 'BP-02.3', 'BP-03.2', 'BP-03.3', 'BP-04.1', 'BP-04.2', 'BP-04.3', 'BP-04.4', 'BP-05.1', 'BP-05.3'], 7),
     ('Dịch vụ ứng dụng', ['AS-BookAppointment', 'AS-CheckIn', 'AS-VerifyInsurance', 'AS-ViewMedicalRecord', 'AS-RecordEncounter', 'AS-IssuePrescription', 'AS-CheckDrugSafety',
                           'AS-SendPrescription', 'AS-SubmitNationalRx', 'AS-ReceivePrescription', 'AS-RecordDispense', 'AS-SendNotification'], 6),
     ('Thành phần ứng dụng', ['AC-Booking', 'AC-Reception', 'AC-EMR', 'AC-ePrescription', 'AC-PharmacyGateway', 'AC-Notification'], 6)], ''),
 ('V-DATA-1', 'Dữ liệu – Cấu trúc thông tin và hiện thực Business Object', [
     ('Business Object (TV1)', ['BO-HoSoBenhNhan', 'BO-LichHen', 'BO-TheBHYT', 'BO-LuotKham', 'BO-BenhAnNgoaiTru', 'BO-DonThuoc', 'BO-PhieuCapThuoc', 'BO-NhatKyTruyCap', 'BO-ChinhSachTruyCap'], 5),
     ('Data Object (TV2)', ['DO-Patient', 'DO-Appointment', 'DO-Insurance', 'DO-Encounter', 'DO-ClinicalRecord', 'DO-Prescription', 'DO-PrescriptionItem', 'DO-Drug',
                            'DO-DispenseRecord', 'DO-Pharmacy', 'DO-Practitioner', 'DO-Notification', 'DO-AccessPolicy', 'DO-AuditEvent', 'DO-OutboxEvent'], 5)], ''),
 ('V-DATA-2', 'Dữ liệu – Ứng dụng truy cập dữ liệu (nguồn chuẩn, PR-02)', [
     ('Thành phần ứng dụng', ['AC-Booking', 'AC-Reception', 'AC-EMR', 'AC-ePrescription', 'AC-PharmacyGateway', 'AC-IAM', 'AC-Audit', 'AC-MasterData'], 8),
     ('Data Object', ['DO-Appointment', 'DO-Patient', 'DO-Insurance', 'DO-Encounter', 'DO-ClinicalRecord', 'DO-Prescription', 'DO-PrescriptionItem', 'DO-OutboxEvent',
                      'DO-DispenseRecord', 'DO-Pharmacy', 'DO-AccessPolicy', 'DO-AuditEvent', 'DO-Drug', 'DO-Practitioner'], 7)],
  'Mỗi Data Object có đúng 1 thành phần ghi (ReadWrite/Write) = nguồn chuẩn; các thành phần khác chỉ đọc.'),
 ('V-VAR-A', 'Biến thể A – Liên thông hồ sơ hai cơ sở (Application + Business)', [
     ('Quy trình ngoại lệ', ['BP-06A', 'BP-06A.1', 'BP-06A.3', 'BP-06A.5', 'BP-06A.6', 'BP-06A.7'], 6),
     ('Dịch vụ & yêu cầu', ['AS-MatchPatient', 'AS-ExchangeRecord', 'AS-RecordConsent', 'FR-A1', 'FR-A2', 'FR-A3'], 6),
     ('Thành phần', ['AC-Reception', 'AC-EMR', 'AC-MPI', 'AC-IntegrationHub', 'AC-Consent', 'AC-FhirAdapter-CS1', 'AC-FhirAdapter-CS2', 'AC-HisLite-CS1', 'AC-ClinicSoft-CS2'], 5),
     ('Dữ liệu', ['DO-Patient', 'DO-PatientLink', 'DO-CodeMapping', 'DO-Consent'], 4)], ''),
 ('V-VAR-B', 'Biến thể B – Nhà thuốc mất kết nối (Application + Business)', [
     ('Quy trình ngoại lệ', ['BP-06B', 'BP-06B.1', 'BP-06B.3', 'BP-06B.5', 'BP-06B.6', 'BP-06B.8'], 6),
     ('Dịch vụ & yêu cầu', ['AS-ReceivePrescription', 'AS-RecordDispense', 'AS-SyncDispense', 'AS-ReconcileDispense', 'FR-B2', 'FR-B3'], 6),
     ('Thành phần', ['EXT-PharmacySystem', 'AC-PharmacyAgent', 'AC-PharmacyGateway', 'AC-Reconciliation'], 4),
     ('Dữ liệu', ['DO-Prescription', 'DO-SyncBatch', 'DO-DispenseRecord', 'DO-DispenseLedger'], 4)], ''),
 ('V-VAR-C', 'Biến thể C – Điều chỉnh/thu hồi đơn (Application + Business)', [
     ('Quy trình ngoại lệ', ['BP-06C', 'BP-06C.1', 'BP-06C.2', 'BP-06C.3', 'BP-06C.4', 'BP-06C.6', 'BP-06C.7'], 7),
     ('Dịch vụ & yêu cầu', ['AS-AmendPrescription', 'AS-RevokePrescription', 'AS-CheckDrugSafety', 'FR-C1', 'FR-C2'], 5),
     ('Thành phần / chức năng', ['AC-ePrescription', 'AF-PrescriptionVersioning', 'AC-PharmacyGateway'], 3),
     ('Dữ liệu', ['DO-Prescription', 'DO-PrescriptionVersion', 'DO-AmendmentReason'], 3)], ''),
 ('V-LAY-1', 'Phân tầng xuyên suốt – Kê đơn điện tử (truy vết G-02/FR-05, CON-03)', [
     ('Motivation', ['G-02', 'OC-02', 'FR-05', 'FR-06', 'CON-03'], 5),
     ('Chiến lược', ['CAP-04', 'COA-01'], 2),
     ('Business', ['BR-BacSi', 'BP-04', 'BP-04.1', 'BP-04.2', 'BP-04.3', 'BP-04.4', 'BO-DonThuoc'], 7),
     ('Application', ['AS-CheckDrugSafety', 'AS-IssuePrescription', 'AS-SubmitNationalRx', 'AS-SendPrescription', 'AC-ePrescription', 'AC-PharmacyGateway', 'AC-EMR', 'DO-Prescription'], 4),
     ('Technology', ['TS-Signing', 'TS-Database', 'TS-Messaging', 'ART-erx-svc', 'ART-pharmacy-gw', 'ND-AppCluster', 'ND-KeyVault'], 7)], ''),
 ('V-LAY-2', 'Phân tầng xuyên suốt – Phân quyền & lưu vết (truy vết G-03/NFR-SEC-02/03)', [
     ('Motivation', ['G-03', 'OC-03', 'NFR-SEC-02', 'NFR-SEC-03', 'FR-08', 'FR-09'], 6),
     ('Chiến lược', ['CAP-06', 'COA-01'], 2),
     ('Business', ['BR-QuanTriBaoMat', 'BF-01', 'BS-07', 'BO-NhatKyTruyCap', 'BO-ChinhSachTruyCap', 'BP-03.2'], 6),
     ('Application', ['AS-Authorize', 'AS-RecordAudit', 'AC-IAM', 'AC-Audit', 'DO-AccessPolicy', 'DO-AuditEvent'], 6),
     ('Technology', ['TS-PolicyDecision', 'TS-Audit', 'TS-ObjectStorage', 'ND-SecurityPlatform', 'ND-AuditStore', 'ND-ObjectStore'], 6)], ''),
]
for vid, name, bands, doc in NEWVIEWS:
    views.append(band_view(vid, name, bands, doc))

# ======================= 8. Ghi file + kiểm tra cấu trúc =======================
root = ET.Element(q('model'), {'identifier': 'id-ehealth-full', f'{{{XSI}}}schemaLocation':
    'http://www.opengroup.org/xsd/archimate/3.0/ http://www.opengroup.org/xsd/archimate/3.1/archimate3_Diagram.xsd'}, nsmap={None: NS, 'xsi': XSI})
ET.SubElement(root, q('name'), {LANG: 'vi'}).text = 'E-Health ngoại trú – Mô hình kiến trúc tổng hợp (Phòng khám ĐK An Tâm)'
ET.SubElement(root, q('documentation'), {LANG: 'vi'}).text = ('Gộp TV1 (Motivation, Business) + TV2 (Application, Data) + TV3 (Technology, Migration) + Chiến lược. '
    'Sinh bởi build_full_model.py. Mã theo 01-vision/catalog.md, 02-models/app-catalog.md, 02-models/tech-catalog.md.')
E = ET.SubElement(root, q('elements'))
for i, (t, n, d) in elements.items():
    e = ET.SubElement(E, q('element'), {'identifier': i, T: t})
    ET.SubElement(e, q('name'), {LANG: 'vi'}).text = n
    if d: ET.SubElement(e, q('documentation'), {LANG: 'vi'}).text = d
Rr = ET.SubElement(root, q('relationships'))
for i, (t, s, d, extra) in rels.items():
    ET.SubElement(Rr, q('relationship'), {'identifier': i, 'source': s, 'target': d, T: t, **extra})
V = ET.SubElement(ET.SubElement(root, q('views')), q('diagrams'))
for v in views: V.append(v)

# ---- Dọn bố cục cho Archi: tách nhóm chồng nhau, giãn khoảng cách để đường nối không đè lên hộp ----
SX, SY, GROW_W, GROW_H = 1.3, 1.45, 14, 10
def _box(n): return [int(n.get(k)) for k in 'xywh']
def _shift(n, dy):
    for m in n.iter(q('node')): m.set('y', str(int(m.get('y')) + dy))
def _fix_overlap(parent):
    """Hộp anh em chồng lên nhau theo chiều dọc → đẩy hộp dưới (và con của nó) xuống; nới hộp cha nếu cần."""
    kids = sorted(parent.findall(q('node')), key=lambda n: (int(n.get('y')), int(n.get('x'))))
    for k in kids: _fix_overlap(k)
    for i, b in enumerate(kids):
        for a in kids[:i]:
            ax, ay, aw, ah = _box(a); bx, by, bw, bh = _box(b)
            if ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah:
                _shift(b, ay + ah + 15 - by)
    if parent.tag == q('node') and kids:
        px, py, pw, ph = _box(parent)
        parent.set('h', str(max(ph, max(int(k.get('y')) + int(k.get('h')) for k in kids) + 10 - py)))
def _spread(v):
    for n in v.iter(q('node')):
        x, y, w, h = _box(n); leaf = not n.findall(q('node'))
        n.set('x', str(round(x * SX))); n.set('y', str(round(y * SY)))
        if leaf and w >= 100: w, h = w + GROW_W, h + GROW_H      # hộp phần tử: rộng/cao thêm cho chữ 3 dòng
        elif not leaf: w, h = round(w * SX), round(h * SY)        # nhóm/container: co giãn cùng tỉ lệ để chứa con
        n.set('w', str(w)); n.set('h', str(h))
    for bp in v.iter(q('bendpoint')):
        bp.set('x', str(round(int(bp.get('x')) * SX))); bp.set('y', str(round(int(bp.get('y')) * SY)))
for v in V:
    _fix_overlap(v); _spread(v)

# kiểm tra: id duy nhất, tham chiếu hợp lệ, quan hệ trong view khớp quan hệ mô hình
ids = [x.get('identifier') for x in root.iter() if x.get('identifier')]
dup = {x for x in ids if ids.count(x) > 1}
assert not dup, f'id trùng: {list(dup)[:5]}'
S = set(ids)
for r in Rr: assert r.get('source') in S and r.get('target') in S, r.get('identifier')
nodes = {}
for v in V:
    for n in v.iter(q('node')):
        if n.get('elementRef'): assert n.get('elementRef') in elements, n.get('elementRef'); nodes[n.get('identifier')] = n.get('elementRef')
    for c in v.iter(q('connection')):
        rr = rels[c.get('relationshipRef')]
        assert (nodes[c.get('source')], nodes[c.get('target')]) == (rr[1], rr[2]), c.get('identifier')
ET.ElementTree(root).write(OUT, xml_declaration=True, encoding='UTF-8', pretty_print=True)
from collections import Counter
print(f'{len(elements)} phần tử, {len(rels)} quan hệ, {len(views)} view →', os.path.basename(OUT))
print(Counter(t for t, _, _ in elements.values()).most_common())
