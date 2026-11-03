import xml.sax.saxutils as X, itertools
E = {}  # code -> (type, name, doc)
R = []  # (id, type, src, tgt, name)
def el(code, t, name, doc=''): E[code] = (t, f'{code} {name}', doc); return code
def rel(t, s, d, name=''):
    rid = f'r{len(R)+1}'; R.append((rid, t, s, d, name)); return rid
# ---------- Baseline ----------
for c,t,n,d in [
 ('ND-B-ServerCS1','Node','Máy chủ CS1 (Win 2012 R2 + SQL Express)','Hết hỗ trợ bảo mật; điểm lỗi đơn (T1)'),
 ('ND-B-ServerCS2','Node','Máy chủ CS2 (PC Win10)','T1'),
 ('ND-B-SaaS','Node','SaaS bên ngoài (Google Sheets, Zalo OA)','Tài khoản chung, dữ liệu sức khỏe (T6)'),
 ('DV-B-Workstation','Device','Máy trạm dùng chung tài khoản','T2'),
 ('NW-B-LAN','CommunicationNetwork','LAN phẳng + Wi-Fi khách chung','T4'),
 ('NW-B-Internet','CommunicationNetwork','Internet 1 đường',''),
 ('TS-B-Backup','TechnologyService','Sao lưu thủ công hàng tuần','T7'),
 ('APP-B-HisLite','ApplicationComponent','HIS-Lite (CS1)','Thu ngân, BHYT, in đơn'),
 ('APP-B-ClinicSoft','ApplicationComponent','ClinicSoft (CS2)',''),
 ('APP-B-Sheet','ApplicationComponent','Google Sheet lịch hẹn',''),
]: el(c,t,n,d)
for a,nd,ap,n in [('ART-B-hislite','ND-B-ServerCS1','APP-B-HisLite','bộ cài HIS-Lite'),('ART-B-clinicsoft','ND-B-ServerCS2','APP-B-ClinicSoft','bộ cài ClinicSoft'),('ART-B-sheet','ND-B-SaaS','APP-B-Sheet','file Google Sheet')]:
    el(a,'Artifact',n); rel('Assignment',nd,a); rel('Realization',a,ap)
rel('Association','DV-B-Workstation','NW-B-LAN'); rel('Association','ND-B-ServerCS1','NW-B-LAN'); rel('Association','ND-B-ServerCS2','NW-B-LAN')
rel('Association','NW-B-LAN','NW-B-Internet'); rel('Association','ND-B-SaaS','NW-B-Internet'); rel('Serving','TS-B-Backup','ND-B-ServerCS1')
# ---------- Target technology ----------
nodes = [
 ('ND-EdgeGateway','Node','Cụm biên (WAF + LB + API Gateway)'),('ND-AppCluster','Node','Cụm máy chủ ứng dụng (3 VM)'),
 ('ND-DataCluster','Node','Cụm CSDL (chính + dự phòng)'),('ND-MessageBroker','Node','Máy chủ hàng đợi thông điệp'),
 ('ND-ObjectStore','Node','Kho lưu trữ đối tượng (WORM)'),('ND-SecurityPlatform','Node','Nền tảng định danh & chính sách'),
 ('ND-AuditStore','Node','Kho lưu vết append-only'),('ND-KeyVault','Node','Quản lý khóa & ký số (KMS/HSM)'),
 ('ND-SecOps','Node','Giám sát & SIEM'),('ND-BackupDR','Node','Sao lưu & DR (vùng 2)'),
 ('ND-SiteCS1','Node','Hạ tầng cơ sở 1'),('ND-SiteCS2','Node','Hạ tầng cơ sở 2'),
 ('ND-SiteServerCS1','Node','Máy chủ tại CS1 (hệ thống Retain)'),('ND-SiteServerCS2','Node','Máy chủ tại CS2 (hệ thống Retain)'),
 ('ND-PartnerPharmacy','Node','Hạ tầng nhà thuốc đối tác'),
 ('DV-Workstation','Device','Máy trạm nhân viên'),('DV-Kiosk','Device','Kiosk check-in'),('DV-IdCardReader','Device','Đầu đọc CCCD gắn chip'),
 ('DV-PatientMobile','Device','Điện thoại bệnh nhân'),
 ('SW-K8sRuntime','SystemSoftware','Nền tảng container'),('SW-PostgreSQL','SystemSoftware','PostgreSQL'),('SW-RabbitMQ','SystemSoftware','RabbitMQ'),
 ('SW-Keycloak','SystemSoftware','Keycloak (OIDC, MFA)'),('SW-OPA','SystemSoftware','Open Policy Agent'),('SW-Wazuh','SystemSoftware','SIEM'),
 ('NW-Internet','CommunicationNetwork','Internet (2 nhà mạng)'),('NW-SiteVPN','Path','VPN IPsec cơ sở ↔ DC'),('NW-PartnerChannel','Path','Kênh đối tác mTLS'),
 ('NW-DCInternal','CommunicationNetwork','Mạng nội bộ DC phân vùng'),
]
for c,t,n in nodes: el(c,t,n)
ts = [('TS-ApiGateway','Cổng API (PEP)','ND-EdgeGateway'),('TS-SecureChannel','Kênh truyền an toàn','ND-EdgeGateway'),
 ('TS-Identity','Xác thực & SSO (MFA)','ND-SecurityPlatform'),('TS-PolicyDecision','Quyết định quyền RBAC+ABAC','ND-SecurityPlatform'),
 ('TS-Audit','Lưu vết bất biến','ND-AuditStore'),('TS-Database','CSDL quan hệ có sao chép','ND-DataCluster'),
 ('TS-Messaging','Hàng đợi/sự kiện bền','ND-MessageBroker'),('TS-ObjectStorage','Lưu trữ đối tượng WORM','ND-ObjectStore'),
 ('TS-KeyManagement','Quản lý khóa mã hóa','ND-KeyVault'),('TS-Signing','Ký số','ND-KeyVault'),
 ('TS-Monitoring','Giám sát, cảnh báo','ND-SecOps'),('TS-SIEM','Phát hiện bất thường an ninh','ND-SecOps'),('TS-Backup','Sao lưu, khôi phục, DR','ND-BackupDR')]
for c,n,nd in ts: el(c,'TechnologyService',n); rel('Realization',nd,c)
for a,b in [('ND-AppCluster','SW-K8sRuntime'),('ND-DataCluster','SW-PostgreSQL'),('ND-AuditStore','SW-PostgreSQL'),('ND-MessageBroker','SW-RabbitMQ'),
            ('ND-SecurityPlatform','SW-Keycloak'),('ND-SecurityPlatform','SW-OPA'),('ND-SecOps','SW-Wazuh')]:
    rel('Composition' if a!='ND-AuditStore' else 'Assignment',a,b)
for a,b in [('ND-SiteCS1','DV-Workstation'),('ND-SiteCS1','DV-Kiosk'),('ND-SiteCS1','DV-IdCardReader'),('ND-SiteCS1','ND-SiteServerCS1'),('ND-SiteCS2','ND-SiteServerCS2')]:
    rel('Aggregation',a,b)
rel('Realization','NW-Internet','NW-SiteVPN'); rel('Realization','NW-Internet','NW-PartnerChannel')
for n in ['ND-SiteCS1','ND-SiteCS2','ND-EdgeGateway']: rel('Association','NW-SiteVPN',n)
rel('Association','NW-PartnerChannel','ND-PartnerPharmacy'); rel('Association','NW-PartnerChannel','ND-EdgeGateway')
rel('Association','DV-PatientMobile','NW-Internet')
for n in ['ND-EdgeGateway','ND-AppCluster','ND-DataCluster','ND-MessageBroker','ND-ObjectStore','ND-SecurityPlatform','ND-AuditStore','ND-KeyVault','ND-SecOps']:
    rel('Association','NW-DCInternal',n)
rel('Serving','TS-ObjectStorage','ND-AuditStore'); rel('Serving','TS-Signing','ND-AuditStore'); rel('Serving','TS-Backup','ND-DataCluster'); rel('Serving','TS-Backup','ND-AuditStore')
# ---------- App components (TV2 codes) + usage + deployment ----------
acs = [('AC-PatientPortal','Cổng bệnh nhân'),('AC-Booking','Quản lý lịch hẹn'),('AC-Reception','Tiếp đón'),('AC-EMR','Hồ sơ bệnh án điện tử'),
 ('AC-ePrescription','Kê đơn điện tử'),('AC-PharmacyGateway','Cổng kết nối nhà thuốc'),('AC-Notification','Thông báo'),('AC-IAM','Định danh & phân quyền'),
 ('AC-Audit','Lưu vết'),('AC-MasterData','Danh mục dùng chung'),('AC-Reporting','Báo cáo vận hành'),
 ('AC-HisLite-CS1','HIS-Lite (thu ngân/BHYT, Retain)'),('AC-ClinicSoft-CS2','ClinicSoft (thu ngân/BHYT, Retain)'),('EXT-PharmacySystem','Phần mềm nhà thuốc đối tác')]
for c,n in acs: el(c,'ApplicationComponent',n, 'Thuộc catalog TV2 — chỉ tham chiếu')
usage = {'AC-PatientPortal':['TS-ApiGateway','TS-SecureChannel','TS-Identity'],'AC-Booking':['TS-Database','TS-Messaging'],'AC-Reception':['TS-Database','TS-ApiGateway'],
 'AC-EMR':['TS-Database','TS-ObjectStorage','TS-PolicyDecision'],'AC-ePrescription':['TS-Database','TS-Signing','TS-Messaging','TS-PolicyDecision'],
 'AC-PharmacyGateway':['TS-ApiGateway','TS-SecureChannel','TS-Messaging','TS-Database'],'AC-Notification':['TS-Messaging'],'AC-IAM':['TS-Identity','TS-PolicyDecision'],
 'AC-Audit':['TS-Audit','TS-ObjectStorage','TS-Signing','TS-SIEM'],'AC-MasterData':['TS-Database'],'AC-Reporting':['TS-Database']}
for ac,tss in usage.items():
    for t in tss: rel('Serving',t,ac)
arts = [('ART-booking-svc','AC-Booking'),('ART-reception-svc','AC-Reception'),('ART-emr-svc','AC-EMR'),('ART-erx-svc','AC-ePrescription'),('ART-pharmacy-gw','AC-PharmacyGateway'),
 ('ART-notify-svc','AC-Notification'),('ART-portal-web','AC-PatientPortal'),('ART-reporting-svc','AC-Reporting'),('ART-masterdata-svc','AC-MasterData')]
for a,ac in arts: el(a,'Artifact','image container'); rel('Realization',a,ac); rel('Assignment','ND-AppCluster',a)
el('ART-iam-realm','Artifact','cấu hình IdP'); rel('Realization','ART-iam-realm','AC-IAM'); rel('Assignment','ND-SecurityPlatform','ART-iam-realm')
el('ART-abac-policy','Artifact','gói chính sách ABAC'); rel('Assignment','ND-SecurityPlatform','ART-abac-policy')
el('ART-audit-svc','Artifact','image audit-svc'); rel('Realization','ART-audit-svc','AC-Audit'); rel('Assignment','ND-AppCluster','ART-audit-svc')
el('ART-audit-log','Artifact','bảng audit_event + phân đoạn niêm phong'); rel('Assignment','ND-AuditStore','ART-audit-log')
el('ART-emr-db','Artifact','schema emr'); rel('Assignment','ND-DataCluster','ART-emr-db')
el('ART-erx-db','Artifact','schema erx'); rel('Assignment','ND-DataCluster','ART-erx-db')
for a,nd,ap,n in [('ART-hislite','ND-SiteServerCS1','AC-HisLite-CS1','bộ cài HIS-Lite'),('ART-clinicsoft','ND-SiteServerCS2','AC-ClinicSoft-CS2','bộ cài ClinicSoft'),('ART-pharmacy-sw','ND-PartnerPharmacy','EXT-PharmacySystem','phần mềm nhà thuốc')]:
    el(a,'Artifact',n); rel('Assignment',nd,a); rel('Realization',a,ap)
# ---------- Migration ----------
plts = [('PLT-0','Plateau','Hiện trạng'),('PLT-1','Plateau','Nền tảng an toàn & Kê đơn điện tử liên thông'),('PLT-2','Plateau','Đặt lịch, tiếp đón số & hồ sơ thống nhất'),('PLT-3','Plateau','Liên thông nhà thuốc & biến thể (Target)')]
for c,t,n in plts: el(c,t,n)
for a,b in [('PLT-0','PLT-1'),('PLT-1','PLT-2'),('PLT-2','PLT-3')]: rel('Triggering',a,b)
gaps = [('GAP-01','Thiếu hạ tầng tập trung, IAM, audit, ký số, kê đơn điện tử','PLT-0','PLT-1'),('GAP-02','Thiếu đặt lịch/tiếp đón số, dữ liệu BN phân tán','PLT-1','PLT-2'),('GAP-03','Thiếu kênh điện tử với nhà thuốc, năng lực biến thể, hệ thống cũ chưa thu hồi','PLT-2','PLT-3')]
for c,n,a,b in gaps: el(c,'Gap',n); rel('Association',c,a); rel('Association',c,b)
for c in ['ND-B-ServerCS1','ND-B-ServerCS2','ND-B-SaaS','NW-B-LAN','APP-B-HisLite','APP-B-ClinicSoft','APP-B-Sheet']: rel('Aggregation','PLT-0',c)
for c in ['ND-EdgeGateway','ND-AppCluster','ND-DataCluster','ND-SecurityPlatform','ND-AuditStore','ND-KeyVault','AC-IAM','AC-Audit','AC-EMR','AC-ePrescription','AC-MasterData']: rel('Aggregation','PLT-1',c)
for c in ['AC-Booking','AC-PatientPortal','AC-Reception','AC-Notification','AC-Reporting','DV-Kiosk','DV-IdCardReader']: rel('Aggregation','PLT-2',c)
for c in ['AC-PharmacyGateway','NW-PartnerChannel','ND-PartnerPharmacy']: rel('Aggregation','PLT-3',c)
wps = [('WP-01','Hạ tầng nền & mạng','PLT-1',[('DLV-01','Hạ tầng DC vận hành',['ND-EdgeGateway','ND-AppCluster','ND-DataCluster']),('DLV-02','Mạng cơ sở phân vùng',['ND-SiteCS1','ND-SiteCS2']),('DLV-03','Biên bản diễn tập DR',['ND-BackupDR'])]),
 ('WP-02','Định danh, phân quyền & lưu vết','PLT-1',[('DLV-04','IAM vận hành',['AC-IAM','ND-SecurityPlatform']),('DLV-05','Audit service + verify',['AC-Audit','ND-AuditStore']),('DLV-06','Bộ chính sách ABAC v1',['ART-abac-policy'])]),
 ('WP-03','Bệnh án lõi & Kê đơn điện tử','PLT-1',[('DLV-07','Kê đơn điện tử ký số tại 2 cơ sở',['AC-ePrescription','AC-EMR']),('DLV-08','Kết nối Hệ thống đơn thuốc quốc gia',['AC-ePrescription'])]),
 ('WP-04','Đặt lịch & tiếp đón số','PLT-2',[('DLV-09','Cổng đặt lịch',['AC-Booking','AC-PatientPortal']),('DLV-10','Tiếp đón QR/CCCD',['AC-Reception','DV-Kiosk']),('DLV-11','Báo cáo thời gian chờ',['AC-Reporting'])]),
 ('WP-05','Kết nối nhà thuốc','PLT-3',[('DLV-12','API nhà thuốc + webhook',['AC-PharmacyGateway']),('DLV-13','6 nhà thuốc đối tác kết nối',['NW-PartnerChannel'])]),
 ('WP-06','Năng lực theo biến thể','PLT-3',[('DLV-14','Năng lực biến thể + BPMN ngoại lệ',[])]),
 ('WP-07','Chuyển đổi dữ liệu & ngừng hệ thống cũ','PLT-3',[('DLV-15','Dữ liệu BN đã gộp',[]),('DLV-16','Biên bản ngừng hệ thống cũ',[])]),
 ('WP-08','Quản lý thay đổi, đào tạo & tuân thủ','PLT-3',[('DLV-17','Hồ sơ đánh giá tác động DLCN',[]),('DLV-18','Tài liệu đào tạo & SOP',[])])]
for c,n,plt,dl in wps:
    el(c,'WorkPackage',n)
    for d,dn,tg in dl:
        el(d,'Deliverable',dn); rel('Realization',c,d)
        for t in tg: rel('Realization',d,t)
for a,b in [('WP-01','WP-02'),('WP-02','WP-03'),('WP-03','WP-04'),('WP-03','WP-05'),('WP-04','WP-07'),('WP-05','WP-06')]: rel('Triggering',a,b)
for g,w in [('GAP-01','WP-01'),('GAP-01','WP-02'),('GAP-01','WP-03'),('GAP-02','WP-04'),('GAP-02','WP-07'),('GAP-03','WP-05'),('GAP-03','WP-06'),('GAP-03','WP-07')]: rel('Association',w,g)
el('EV-01','ImplementationEvent','Pilot kê đơn điện tử hoàn tất'); rel('Triggering','WP-03','EV-01'); rel('Triggering','EV-01','WP-04')

# ---------- Views ----------
views = []
def view(name, vp, layout, groups=()):
    """layout: list of (code, x, y, w, h); groups: (label, x,y,w,h, [codes])"""
    views.append((name, vp, layout, groups))
W,H = 170,55
def grid(codes, x0, y0, cols, dx=190, dy=75, w=W, h=H):
    return [(c, x0+(i%cols)*dx, y0+(i//cols)*dy, w, h) for i,c in enumerate(codes)]
view('TV3-01 Hạ tầng cơ sở (Baseline, PLT-0)', 'Technology',
     grid(['DV-B-Workstation','NW-B-LAN','NW-B-Internet','TS-B-Backup','ND-B-ServerCS1','ND-B-ServerCS2','ND-B-SaaS'], 20, 20, 4) + grid(['ART-B-hislite','ART-B-clinicsoft','ART-B-sheet'], 210, 200, 3) + grid(['APP-B-HisLite','APP-B-ClinicSoft','APP-B-Sheet'], 210, 300, 3))
tgt = []
zones = [('Cơ sở CS1/CS2', ['ND-SiteCS1','ND-SiteCS2','DV-Workstation','DV-Kiosk','DV-IdCardReader','ND-SiteServerCS1','ND-SiteServerCS2'], 20, 20, 2),
         ('Internet & đối tác', ['DV-PatientMobile','NW-Internet','ND-PartnerPharmacy','NW-SiteVPN','NW-PartnerChannel'], 20, 340, 2),
         ('DMZ', ['ND-EdgeGateway','TS-ApiGateway','TS-SecureChannel'], 440, 20, 1),
         ('Vùng App', ['ND-AppCluster','SW-K8sRuntime'], 440, 270, 1),
         ('Vùng Data', ['ND-DataCluster','SW-PostgreSQL','TS-Database','ND-MessageBroker','SW-RabbitMQ','TS-Messaging','ND-ObjectStore','TS-ObjectStorage'], 660, 20, 2),
         ('Vùng Security', ['ND-SecurityPlatform','SW-Keycloak','SW-OPA','TS-Identity','TS-PolicyDecision','ND-AuditStore','TS-Audit','ND-KeyVault','TS-KeyManagement','TS-Signing'], 1060, 20, 2),
         ('Mgmt & DR', ['ND-SecOps','SW-Wazuh','TS-Monitoring','TS-SIEM','ND-BackupDR','TS-Backup','NW-DCInternal'], 660, 380, 2)]
groups = []
for label, codes, x0, y0, cols in zones:
    g = grid(codes, x0+15, y0+35, cols); tgt += g
    rows = (len(codes)+cols-1)//cols
    groups.append((label, x0, y0, cols*190+10, rows*75+45, codes))
view('TV3-02 Hạ tầng cơ sở (Target, PLT-3)', 'Technology', tgt, groups)
use = grid([t for t,_,_ in ts], 20, 20, 7) + grid(list(usage.keys()), 20, 220, 6)
view('TV3-03 Sử dụng hạ tầng (Infrastructure Usage)', 'Technology Usage', use)
dep = grid(['ND-AppCluster','ND-DataCluster','ND-AuditStore','ND-SecurityPlatform'], 20, 20, 4, dx=260) + \
      grid([a for a,_ in arts]+['ART-audit-svc'], 20, 140, 5) + grid(['ART-emr-db','ART-erx-db','ART-audit-log','ART-iam-realm','ART-abac-policy'], 20, 320, 5) + \
      grid([ac for _,ac in arts]+['AC-Audit','AC-IAM'], 20, 420, 6) + grid(['ND-SiteServerCS1','ND-SiteServerCS2','ND-PartnerPharmacy','ART-hislite','ART-clinicsoft','ART-pharmacy-sw','AC-HisLite-CS1','AC-ClinicSoft-CS2','EXT-PharmacySystem'], 20, 620, 3)
view('TV3-04 Thực hiện và triển khai (Implementation & Deployment)', 'Implementation and Deployment', dep)
mig = grid(['PLT-0','PLT-1','PLT-2','PLT-3'], 20, 40, 4, dx=260, w=200, h=60) + grid(['GAP-01','GAP-02','GAP-03'], 150, 170, 3, dx=260, w=200, h=60)
view('TV3-05 Kế hoạch dịch chuyển (Migration)', 'Migration', mig)
proj = grid([w for w,_,_,_ in wps], 20, 20, 4, w=170) + grid([d for _,_,_,dl in wps for d,_,_ in dl], 20, 200, 6) + grid(['EV-01'], 20, 480, 1)
view('TV3-06 Dự án (Project)', 'Project', proj)
im = grid(['PLT-1','PLT-2','PLT-3'], 20, 20, 3, dx=400, w=200) + grid(['WP-01','WP-02','WP-03','WP-04','WP-07','WP-05','WP-06','WP-08'], 20, 120, 4, dx=200) + \
     grid(['GAP-01','GAP-02','GAP-03'], 20, 300, 3, dx=400, w=200)
view('TV3-07 Thực hiện và dịch chuyển (Implementation & Migration)', 'Implementation and Migration', im)

# ---------- Write XML ----------
q = lambda s: X.escape(s, {'"': '&quot;'})
idmap = {c: 'id-' + c.replace(' ', '_') for c in E}
out = ['<?xml version="1.0" encoding="UTF-8"?>',
 '<model xmlns="http://www.opengroup.org/xsd/archimate/3.0/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" identifier="id-ehealth-tv3">',
 '  <name xml:lang="vi">E-Health ngoại trú — Công nghệ &amp; Dịch chuyển (TV3)</name>',
 '  <documentation xml:lang="vi">Sinh tự động từ tech-catalog.md v0.1. Nhập vào Archi: File &gt; Import &gt; Open Exchange XML Model. Mã AC-* thuộc TV2, chỉ tham chiếu.</documentation>',
 '  <elements>']
for c,(t,n,d) in E.items():
    out.append(f'    <element identifier="{idmap[c]}" xsi:type="{t}"><name xml:lang="vi">{q(n)}</name>' + (f'<documentation xml:lang="vi">{q(d)}</documentation>' if d else '') + '</element>')
out.append('  </elements>\n  <relationships>')
for rid,t,s,d,n in R:
    out.append(f'    <relationship identifier="id-{rid}" source="{idmap[s]}" target="{idmap[d]}" xsi:type="{t}" />')
out.append('  </relationships>\n  <views>\n    <diagrams>')
vc = itertools.count(1)
for vi,(name, vp, layout, groups) in enumerate(views, 1):
    out.append(f'      <view identifier="id-v{vi}" xsi:type="Diagram"><name xml:lang="vi">{q(name)}</name>')
    placed = {}
    ingroup = {c for g in groups for c in g[5]}
    for gi,(label,x,y,w,h,codes) in enumerate(groups):
        out.append(f'        <node identifier="id-v{vi}-g{gi}" xsi:type="Container" x="{x}" y="{y}" w="{w}" h="{h}"><label xml:lang="vi">{q(label)}</label>')
        for c,cx,cy,cw,ch in layout:
            if c in codes:
                nid = f'id-v{vi}-n{next(vc)}'; placed[c] = nid
                out.append(f'          <node identifier="{nid}" elementRef="{idmap[c]}" xsi:type="Element" x="{cx}" y="{cy}" w="{cw}" h="{ch}" />')
        out.append('        </node>')
    for c,cx,cy,cw,ch in layout:
        if c in ingroup: continue
        nid = f'id-v{vi}-n{next(vc)}'; placed[c] = nid
        out.append(f'        <node identifier="{nid}" elementRef="{idmap[c]}" xsi:type="Element" x="{cx}" y="{cy}" w="{cw}" h="{ch}" />')
    for rid,t,s,d,n in R:
        if s in placed and d in placed:
            # avoid drawing composition/aggregation clutter for grouped target view is fine
            out.append(f'        <connection identifier="id-v{vi}-{rid}" relationshipRef="id-{rid}" xsi:type="Relationship" source="{placed[s]}" target="{placed[d]}" />')
    out.append('      </view>')
out.append('    </diagrams>\n  </views>\n</model>')
open('/mnt/project-files/ehealth-ea/02-models/archimate/ehealth-tv3-exchange.xml','w').write('\n'.join(out))
print(len(E),'elements',len(R),'relationships',len(views),'views')
