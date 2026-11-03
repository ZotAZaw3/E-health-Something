// Mock API E-Health ngoại trú (TV3) — chạy: node server.js  (Node >= 18, không cần cài thư viện)
// Mục đích: minh họa 1 kịch bản end-to-end + các ngoại lệ, đúng hợp đồng trong ../openapi.yaml.
// Dữ liệu trong bộ nhớ, giả lập (mock). Không dùng cho dữ liệu thật.
'use strict';
const http = require('http');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const PORT = process.env.PORT || 4010;

// ---------- Dữ liệu mẫu ----------
const users = {
  'tok-bn-p001':   { userId: 'bn-p001',   role: 'BR-BenhNhan', facility: null, patientId: 'P001', name: 'Nguyễn Văn Hùng' },
  'tok-letan-cs1': { userId: 'letan-cs1', role: 'BR-LeTan',    facility: 'CS1', name: 'Lễ tân Phạm Thu' },
  'tok-bs-an':     { userId: 'bs-an',     role: 'BR-BacSi',    facility: 'CS1', name: 'BS Trần An', specialty: 'NOI' },
  'tok-bs-binh':   { userId: 'bs-binh',   role: 'BR-BacSi',    facility: 'CS1', name: 'BS Lê Bình', specialty: 'NOI' },
  'tok-ds-nt01':   { userId: 'ds-nt01',   role: 'BR-DuocSi',   facility: null, pharmacyId: 'NT-01', pharmacyType: 'PARTNER', name: 'DS Hoàng Mai (NT-01)' },
  'tok-ds-nbcs1':  { userId: 'ds-nbcs1',  role: 'BR-DuocSi',   facility: 'CS1', pharmacyId: 'NB-CS1', pharmacyType: 'INTERNAL', name: 'DS nội bộ CS1' },
  'tok-dpo':       { userId: 'dpo',       role: 'BR-QuanTriBaoMat', facility: null, name: 'DPO Đỗ Hạnh' },
};
const patients = {
  P001: { patientId: 'P001', fullName: 'Nguyễn Văn Hùng', birthYear: 1985, idNumber: '001085012345', phone: '0912345678',
          facility: 'CS1', allergies: [{ substanceClass: 'PENICILLIN', note: 'Phát ban 2019' }],
          history: [{ date: '2026-06-10', icd10: 'J02.9', text: 'Viêm họng cấp' }] },
  P002: { patientId: 'P002', fullName: 'Trần Thị Lan', birthYear: 1990, idNumber: '001190067890', phone: '0987654321',
          facility: 'CS2', allergies: [], history: [] },
};
const drugs = {
  'AMOX500': { code: 'AMOX500', name: 'Amoxicillin 500mg', class: 'PENICILLIN', controlled: false },
  'CEFU500': { code: 'CEFU500', name: 'Cefuroxim 500mg', class: 'CEPHALOSPORIN', controlled: false },
  'PARA500': { code: 'PARA500', name: 'Paracetamol 500mg', class: 'ANALGESIC', controlled: false },
  'LORA10':  { code: 'LORA10',  name: 'Loratadin 10mg', class: 'ANTIHISTAMINE', controlled: false },
  'DIAZ5':   { code: 'DIAZ5',   name: 'Diazepam 5mg', class: 'BENZODIAZEPINE', controlled: true },
};
const slots = [];
['08:00','08:15','08:30','08:45','09:00'].forEach((t, i) =>
  slots.push({ slotId: `S-20261105-AN-${i+1}`, practitionerId: 'bs-an', practitionerName: 'BS Trần An', specialty: 'NOI', facility: 'CS1', start: `2026-11-05T${t}:00+07:00`, available: true }));
const appointments = {}, encounters = {}, prescriptions = {}, dispenses = {}, breakGlass = {}, idem = {};
let seq = 1; const id = (p) => `${p}-${String(seq++).padStart(4, '0')}`;

// ---------- Audit append-only + chuỗi băm (ADR-003) ----------
const auditLog = []; let lastHash = '0'.repeat(64);
const sortDeep = (v) => Array.isArray(v) ? v.map(sortDeep) : v && typeof v === 'object' ? Object.keys(v).sort().reduce((o, k) => (o[k] = sortDeep(v[k]), o), {}) : v;
function canon(e) { const { hash, prevHash, ...rest } = e; return JSON.stringify(sortDeep(rest)); } // dạng chuẩn hóa: khóa sắp xếp ở mọi cấp
function audit(actor, action, resource, decision, extra = {}) {
  const e = { eventId: crypto.randomUUID(), ts: new Date().toISOString(),
    actor: actor ? { userId: actor.userId, role: actor.role, facility: actor.facility || null, pharmacyId: actor.pharmacyId || null } : null,
    action, resource, decision, breakGlass: !!extra.breakGlass, reason: extra.reason || null,
    outcome: extra.outcome || 'SUCCESS', correlationId: extra.correlationId || null };
  e.prevHash = lastHash; e.hash = crypto.createHash('sha256').update(lastHash + canon(e)).digest('hex'); lastHash = e.hash;
  auditLog.push(e); return e;
}
function verifyChain() {
  let prev = '0'.repeat(64);
  for (let i = 0; i < auditLog.length; i++) {
    const e = auditLog[i];
    const h = crypto.createHash('sha256').update(prev + canon(e)).digest('hex');
    if (e.prevHash !== prev || e.hash !== h) return { valid: false, checked: i + 1, firstBrokenIndex: i, firstBrokenEventId: e.eventId };
    prev = e.hash;
  }
  return { valid: true, checked: auditLog.length, lastHash: prev };
}

// ---------- PDP: RBAC + ABAC (ADR-002) ----------
function decideRecordAccess(u, patientId) {
  if (u.role === 'BR-BenhNhan') return u.patientId === patientId ? { allow: true, policyId: 'RBAC-SELF' } : { allow: false, policyId: 'RBAC-SELF' };
  if (!['BR-BacSi', 'BR-DieuDuong'].includes(u.role)) return { allow: false, policyId: 'RBAC-ROLE', reason: 'Vai trò không được xem bệnh án' };
  const now = Date.now();
  const care = Object.values(encounters).some(en => en.patientId === patientId && en.practitionerId === u.userId &&
    (en.status === 'IN_PROGRESS' || en.status === 'WAITING' || now - Date.parse(en.openedAt) < 90 * 864e5));
  if (care) return { allow: true, policyId: 'POL-01' };
  const bg = breakGlass[`${u.userId}|${patientId}`];
  if (bg && Date.parse(bg.expiresAt) > now) return { allow: true, policyId: 'POL-07', breakGlass: true, reason: bg.reason };
  return { allow: false, policyId: 'POL-01', reason: 'Không có quan hệ điều trị với bệnh nhân này' };
}

// ---------- HTTP helpers ----------
function send(res, code, body, headers = {}) {
  res.writeHead(code, { 'Content-Type': 'application/json; charset=utf-8', 'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Authorization, Content-Type, Idempotency-Key', 'Access-Control-Allow-Methods': 'GET,POST,PATCH,OPTIONS', ...headers });
  res.end(body === undefined ? '' : JSON.stringify(body, null, 2));
}
const problem = (res, code, title, detail, extra = {}) => send(res, code, { type: `https://ehealth.example/errors/${code}`, title, status: code, detail, ...extra }, { 'Content-Type': 'application/problem+json; charset=utf-8' });
function readBody(req) { return new Promise(r => { let d = ''; req.on('data', c => d += c); req.on('end', () => { try { r(d ? JSON.parse(d) : {}); } catch { r(null); } }); }); }
function auth(req) { const h = req.headers.authorization || ''; return users[h.replace(/^Bearer\s+/i, '')] || null; }
const need = (u, res, ...roles) => { if (!u) { problem(res, 401, 'Chưa xác thực', 'Thiếu hoặc sai token'); return false; }
  if (roles.length && !roles.includes(u.role)) { audit(u, 'ACCESS', { type: 'Endpoint' }, { result: 'DENY', policyId: 'RBAC-ROLE' }, { outcome: 'FAILURE' });
    problem(res, 403, 'Không đủ quyền', `Vai trò ${u.role} không được gọi chức năng này`, { policyId: 'RBAC-ROLE' }); return false; } return true; };
const rxView = (rx) => ({ ...rx, items: rx.items.map(it => ({ ...it })) });
function rxStatus(rx) {
  if (['REVOKED', 'SUPERSEDED', 'DRAFT'].includes(rx.status)) return rx.status;
  const total = rx.items.reduce((s, i) => s + i.quantity, 0), done = rx.items.reduce((s, i) => s + i.dispensedQty, 0);
  return done === 0 ? 'ISSUED' : done < total ? 'PARTIALLY_DISPENSED' : 'DISPENSED';
}

// ---------- Router ----------
const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`); const p = url.pathname; const m = req.method;
  if (m === 'OPTIONS') return send(res, 204);
  if (m === 'GET' && (p === '/' || p.startsWith('/ui'))) {
    const f = path.join(__dirname, 'public', p === '/' ? 'index.html' : p.replace(/^\/ui\//, ''));
    if (!f.startsWith(path.join(__dirname, 'public'))) return send(res, 404, {});
    return fs.readFile(f, (err, data) => { if (err) return send(res, 404, {}); res.writeHead(200, { 'Content-Type': f.endsWith('.html') ? 'text/html; charset=utf-8' : 'text/plain' }); res.end(data); });
  }
  if (m === 'GET' && p === '/openapi.yaml') { res.writeHead(200, { 'Content-Type': 'text/yaml; charset=utf-8' }); return res.end(fs.readFileSync(path.join(__dirname, '..', 'openapi.yaml'))); }
  const u = auth(req);
  const body = ['POST', 'PUT', 'PATCH'].includes(m) ? await readBody(req) : {};
  if (body === null) return problem(res, 400, 'JSON không hợp lệ', 'Không đọc được thân yêu cầu');
  const corr = req.headers['x-correlation-id'] || null;
  let mm;

  // AS-BookAppointment
  if (m === 'GET' && p === '/slots') { if (!need(u, res)) return;
    return send(res, 200, slots.filter(s => (!url.searchParams.get('specialty') || s.specialty === url.searchParams.get('specialty')))); }
  if (m === 'POST' && p === '/appointments') { if (!need(u, res, 'BR-BenhNhan', 'BR-LeTan')) return;
    const s = slots.find(x => x.slotId === body.slotId); const pid = u.role === 'BR-BenhNhan' ? u.patientId : body.patientId;
    if (!s || !patients[pid]) return problem(res, 422, 'Dữ liệu không hợp lệ', 'slotId hoặc patientId không tồn tại');
    if (!s.available) return problem(res, 409, 'Khung giờ đã có người đặt', 'Vui lòng chọn khung giờ khác', { alternatives: slots.filter(x => x.available).slice(0, 3).map(x => x.slotId) });
    s.available = false; const a = { appointmentId: id('APT'), patientId: pid, slotId: s.slotId, practitionerId: s.practitionerId, facility: s.facility, start: s.start, reason: body.reason || null, status: 'BOOKED' };
    a.checkInCode = `QR-${a.appointmentId}`; appointments[a.appointmentId] = a;
    audit(u, 'CREATE', { type: 'Appointment', id: a.appointmentId, patientRef: pid }, { result: 'PERMIT', policyId: 'RBAC' }, { correlationId: corr });
    return send(res, 201, { ...a, notification: { channel: 'SMS', to: patients[pid].phone.replace(/\d(?=\d{3})/g, '*'), status: 'QUEUED' } }, { Location: `/appointments/${a.appointmentId}` }); }

  // AS-CancelAppointment (FR-02): hủy hoặc đổi lịch, giải phóng khung giờ
  if (m === 'PATCH' && (mm = p.match(/^\/appointments\/([^/]+)$/))) { if (!need(u, res, 'BR-BenhNhan', 'BR-LeTan')) return;
    const a = appointments[mm[1]]; if (!a || (u.role === 'BR-BenhNhan' && a.patientId !== u.patientId)) return problem(res, 404, 'Không tìm thấy lịch hẹn', mm[1]);
    if (a.status !== 'BOOKED') return problem(res, 409, 'Không đổi được', `Lịch hẹn đang ở trạng thái ${a.status}`);
    const old = slots.find(x => x.slotId === a.slotId);
    if (body.action === 'CANCEL') { a.status = 'CANCELLED'; old.available = true; }
    else if (body.action === 'RESCHEDULE') { const ns = slots.find(x => x.slotId === body.newSlotId);
      if (!ns || !ns.available) return problem(res, 409, 'Khung giờ mới không còn trống', body.newSlotId || '');
      old.available = true; ns.available = false; Object.assign(a, { slotId: ns.slotId, start: ns.start, practitionerId: ns.practitionerId }); }
    else return problem(res, 422, 'Dữ liệu không hợp lệ', 'action phải là CANCEL hoặc RESCHEDULE');
    audit(u, 'UPDATE', { type: 'Appointment', id: a.appointmentId, patientRef: a.patientId }, { result: 'PERMIT', policyId: 'RBAC' }, { reason: body.action });
    return send(res, 200, { ...a, notification: { channel: 'SMS', status: 'QUEUED' } }); }

  // AS-CheckIn
  if (m === 'POST' && p === '/encounters') { if (!need(u, res, 'BR-LeTan')) return;
    const a = Object.values(appointments).find(x => x.checkInCode === body.checkInCode || x.appointmentId === body.appointmentId);
    if (!a) return problem(res, 404, 'Không tìm thấy lịch hẹn', 'Mã check-in không đúng');
    const pt = patients[a.patientId];
    if (body.idNumber && body.idNumber !== pt.idNumber) { audit(u, 'CHECK_IN', { type: 'Appointment', id: a.appointmentId, patientRef: pt.patientId }, { result: 'PERMIT', policyId: 'RBAC' }, { outcome: 'FAILURE', correlationId: corr });
      return problem(res, 422, 'Danh tính không khớp', 'Số CCCD không khớp hồ sơ lịch hẹn — chuyển xác minh thủ công'); }
    if (a.status !== 'BOOKED') return problem(res, 409, 'Lịch hẹn đã check-in hoặc đã hủy', `Trạng thái hiện tại: ${a.status}`);
    a.status = 'CHECKED_IN';
    const en = { encounterId: id('ENC'), patientId: pt.patientId, appointmentId: a.appointmentId, practitionerId: a.practitionerId, facility: a.facility, status: 'WAITING', queueNumber: Object.keys(encounters).length + 1, openedAt: new Date().toISOString(),
      insurance: { cardNumber: 'DN4010123456789', verified: true, source: 'EXT-InsurancePortal (mock)' } };
    encounters[en.encounterId] = en;
    audit(u, 'CREATE', { type: 'Encounter', id: en.encounterId, patientRef: pt.patientId }, { result: 'PERMIT', policyId: 'RBAC' }, { correlationId: corr });
    return send(res, 201, en, { Location: `/encounters/${en.encounterId}` }); }
  if (m === 'GET' && p === '/encounters') { if (!need(u, res, 'BR-BacSi', 'BR-LeTan', 'BR-DieuDuong')) return;
    const list = Object.values(encounters).filter(e => u.role !== 'BR-BacSi' || e.practitionerId === u.userId).map(e => ({ ...e, patientName: patients[e.patientId].fullName }));
    return send(res, 200, list); }

  // AS-ViewMedicalRecord (ABAC)
  if (m === 'GET' && (mm = p.match(/^\/patients\/([^/]+)\/records$/))) { if (!need(u, res)) return;
    const pid = mm[1]; if (!patients[pid]) return problem(res, 404, 'Không tìm thấy', 'Bệnh nhân không tồn tại');
    const d = decideRecordAccess(u, pid);
    audit(u, 'READ', { type: 'ClinicalRecord', id: pid, patientRef: pid }, { result: d.allow ? 'PERMIT' : 'DENY', policyId: d.policyId }, { breakGlass: d.breakGlass, reason: d.reason, outcome: d.allow ? 'SUCCESS' : 'FAILURE', correlationId: corr });
    if (!d.allow) return problem(res, 403, 'Truy cập bị từ chối', d.reason || 'Không đủ quyền', { policyId: d.policyId, breakGlassAllowed: ['BR-BacSi', 'BR-DieuDuong'].includes(u.role), breakGlassEndpoint: '/access/break-glass' });
    const pt = patients[pid];
    return send(res, 200, { patientId: pid, fullName: pt.fullName, birthYear: pt.birthYear, allergies: pt.allergies, history: pt.history,
      prescriptions: Object.values(prescriptions).filter(r => r.patientId === pid).map(r => ({ prescriptionId: r.prescriptionId, rxCode: r.rxCode, status: rxStatus(r), issuedAt: r.issuedAt })),
      access: { policyId: d.policyId, breakGlass: !!d.breakGlass } }); }

  // Break-glass (POL-07)
  if (m === 'POST' && p === '/access/break-glass') { if (!need(u, res, 'BR-BacSi', 'BR-DieuDuong')) return;
    if (!patients[body.patientId] || !body.reason || body.reason.trim().length < 10) return problem(res, 422, 'Thiếu lý do', 'Bắt buộc nhập lý do truy cập khẩn cấp (≥ 10 ký tự)');
    const g = { grantId: id('BG'), userId: u.userId, patientId: body.patientId, reason: body.reason, grantedAt: new Date().toISOString(), expiresAt: new Date(Date.now() + 4 * 3600e3).toISOString(), reviewDueBy: new Date(Date.now() + 24 * 3600e3).toISOString(), reviewer: 'BR-QuanTriBaoMat' };
    breakGlass[`${u.userId}|${body.patientId}`] = g;
    audit(u, 'BREAK_GLASS', { type: 'Patient', id: body.patientId, patientRef: body.patientId }, { result: 'PERMIT', policyId: 'POL-07' }, { breakGlass: true, reason: body.reason, correlationId: corr });
    return send(res, 201, g); }

  // AS-IssuePrescription + AS-CheckDrugSafety
  if (m === 'POST' && p === '/prescriptions') { if (!need(u, res, 'BR-BacSi')) return;
    const en = encounters[body.encounterId]; if (!en) return problem(res, 422, 'Dữ liệu không hợp lệ', 'encounterId không tồn tại');
    const d = decideRecordAccess(u, en.patientId);
    if (!d.allow || d.breakGlass) { audit(u, 'CREATE', { type: 'Prescription', patientRef: en.patientId }, { result: 'DENY', policyId: d.breakGlass ? 'POL-07' : d.policyId }, { outcome: 'FAILURE', correlationId: corr });
      return problem(res, 403, 'Không được kê đơn', 'Chỉ bác sĩ phụ trách lượt khám được kê đơn (break-glass chỉ cho phép xem)', { policyId: 'POL-01' }); }
    const items = (body.items || []).map((it, i) => ({ itemId: `L${i + 1}`, drugCode: it.drugCode, drugName: drugs[it.drugCode]?.name, dosage: it.dosage, quantity: it.quantity, dispensedQty: 0, controlled: !!drugs[it.drugCode]?.controlled }));
    if (!items.length || items.some(i => !i.drugName || !(i.quantity > 0))) return problem(res, 422, 'Dữ liệu không hợp lệ', 'Thiếu thuốc hoặc mã thuốc/số lượng sai');
    const pt = patients[en.patientId]; const alerts = [];
    items.forEach(i => pt.allergies.forEach(a => { if (drugs[i.drugCode].class === a.substanceClass) alerts.push({ severity: 'HIGH', type: 'ALLERGY', itemId: i.itemId, message: `${i.drugName} thuộc nhóm ${a.substanceClass}, BN có tiền sử dị ứng (${a.note})` }); }));
    if (alerts.length && !body.overrideReason) { audit(u, 'CREATE', { type: 'Prescription', patientRef: en.patientId }, { result: 'PERMIT', policyId: 'POL-01' }, { outcome: 'FAILURE', reason: 'SAFETY_ALERT', correlationId: corr });
      return problem(res, 422, 'Cảnh báo an toàn thuốc', 'Đơn có cảnh báo mức cao; sửa đơn hoặc ghi lý do bỏ qua (overrideReason)', { alerts }); }
    const rx = { prescriptionId: id('RX'), version: 1, encounterId: en.encounterId, patientId: en.patientId, practitionerId: u.userId, facility: en.facility, diagnosis: body.diagnosis || null, items, status: 'DRAFT', safetyCheck: { alerts, overrideReason: body.overrideReason || null } };
    prescriptions[rx.prescriptionId] = rx; en.status = 'IN_PROGRESS';
    audit(u, 'CREATE', { type: 'Prescription', id: rx.prescriptionId, patientRef: en.patientId }, { result: 'PERMIT', policyId: 'POL-01' }, { correlationId: corr });
    return send(res, 201, rxView(rx), { Location: `/prescriptions/${rx.prescriptionId}` }); }
  if (m === 'POST' && (mm = p.match(/^\/prescriptions\/([^/]+)\/issue$/))) { if (!need(u, res, 'BR-BacSi')) return;
    const rx = prescriptions[mm[1]]; if (!rx) return problem(res, 404, 'Không tìm thấy', 'Đơn không tồn tại');
    if (rx.practitionerId !== u.userId) return problem(res, 403, 'Không được ký', 'Chỉ bác sĩ lập đơn được ký', { policyId: 'POL-01' });
    if (rx.status !== 'DRAFT') return problem(res, 409, 'Đơn đã phát hành', 'Không ký lại đơn đã phát hành; dùng điều chỉnh đơn (biến thể C)', { policyId: 'POL-05' });
    rx.status = 'ISSUED'; rx.issuedAt = new Date().toISOString(); rx.rxCode = `${rx.facility}${Date.now().toString().slice(-8)}-c`;
    rx.signature = { alg: 'RS256', keyId: 'kms://cs1/bs-an/2026', value: crypto.createHash('sha256').update(JSON.stringify(rx.items) + rx.rxCode).digest('base64').slice(0, 32) + '…', signedBy: u.userId, provider: 'CA ký số từ xa (mock)' };
    rx.nationalRx = { system: 'EXT-NationalRxSystem (mock)', status: 'SUBMITTED', submittedAt: rx.issuedAt };
    audit(u, 'SIGN', { type: 'Prescription', id: rx.prescriptionId, patientRef: rx.patientId }, { result: 'PERMIT', policyId: 'POL-01' }, { correlationId: corr });
    return send(res, 200, { ...rxView(rx), status: rxStatus(rx), notification: { channel: 'SMS', message: `Đơn thuốc ${rx.rxCode} đã phát hành`, status: 'QUEUED' } }); }
  if (m === 'GET' && (mm = p.match(/^\/prescriptions\/([^/]+)$/))) { if (!need(u, res, 'BR-BacSi', 'BR-BenhNhan')) return;
    const rx = prescriptions[mm[1]]; if (!rx) return problem(res, 404, 'Không tìm thấy', 'Đơn không tồn tại');
    const d = decideRecordAccess(u, rx.patientId);
    audit(u, 'READ', { type: 'Prescription', id: rx.prescriptionId, patientRef: rx.patientId }, { result: d.allow ? 'PERMIT' : 'DENY', policyId: d.policyId }, { breakGlass: d.breakGlass, outcome: d.allow ? 'SUCCESS' : 'FAILURE' });
    if (!d.allow) return problem(res, 403, 'Truy cập bị từ chối', d.reason, { policyId: d.policyId });
    return send(res, 200, { ...rxView(rx), status: rxStatus(rx) }); }

  // Biến thể C: thu hồi / điều chỉnh
  if (m === 'POST' && (mm = p.match(/^\/prescriptions\/([^/]+)\/(revoke|amend)$/))) { if (!need(u, res, 'BR-BacSi')) return;
    const rx = prescriptions[mm[1]]; if (!rx) return problem(res, 404, 'Không tìm thấy', 'Đơn không tồn tại');
    if (rx.practitionerId !== u.userId) return problem(res, 403, 'Không được thay đổi', 'Chỉ bác sĩ lập đơn', { policyId: 'POL-01' });
    if (!body.reason) return problem(res, 422, 'Thiếu lý do', 'Bắt buộc lý do điều chỉnh/thu hồi');
    const st = rxStatus(rx);
    if (['REVOKED', 'SUPERSEDED', 'DRAFT'].includes(st)) return problem(res, 409, 'Trạng thái không hợp lệ', `Đơn đang ở trạng thái ${st}`);
    if (mm[2] === 'revoke') {
      if (st !== 'ISSUED') { audit(u, 'REVOKE', { type: 'Prescription', id: rx.prescriptionId, patientRef: rx.patientId }, { result: 'DENY', policyId: 'POL-05' }, { outcome: 'FAILURE', reason: body.reason });
        return problem(res, 409, 'Không thu hồi được đơn đã cấp', `Đơn đã ${st}; tạo đơn điều chỉnh (POST /prescriptions/{id}/amend) và thông báo nhà thuốc + BN`, { policyId: 'POL-05', currentStatus: st }); }
      rx.status = 'REVOKED'; rx.revokedAt = new Date().toISOString(); rx.revokeReason = body.reason;
      audit(u, 'REVOKE', { type: 'Prescription', id: rx.prescriptionId, patientRef: rx.patientId }, { result: 'PERMIT', policyId: 'POL-05' }, { reason: body.reason });
      return send(res, 200, { ...rxView(rx), status: 'REVOKED', events: [{ type: 'PrescriptionRevoked', to: ['AC-PharmacyGateway', 'AC-Notification'], status: 'PUBLISHED' }] }); }
    const items = (body.items || []).map((it, i) => ({ itemId: `L${i + 1}`, drugCode: it.drugCode, drugName: drugs[it.drugCode]?.name, dosage: it.dosage, quantity: it.quantity, dispensedQty: 0, controlled: !!drugs[it.drugCode]?.controlled }));
    if (!items.length || items.some(i => !i.drugName)) return problem(res, 422, 'Dữ liệu không hợp lệ', 'Danh sách thuốc điều chỉnh không hợp lệ');
    // Không cấp lại phần đã cấp theo phiên bản cũ: số đã cấp của cùng mã thuốc được chuyển sang phiên bản mới
    const warnings = [];
    items.forEach(it => { const old = rx.items.filter(o => o.drugCode === it.drugCode).reduce((s, o) => s + o.dispensedQty, 0);
      it.dispensedQty = Math.min(old, it.quantity);
      if (old > it.quantity) warnings.push({ drugName: it.drugName, dispensed: old, newQuantity: it.quantity, message: 'BN đã nhận nhiều hơn số lượng mới — dược sĩ liên hệ BN hướng dẫn/thu hồi thuốc thừa' }); });
    rx.items.filter(o => o.dispensedQty > 0 && !items.some(i => i.drugCode === o.drugCode)).forEach(o =>
      warnings.push({ drugName: o.drugName, dispensed: o.dispensedQty, newQuantity: 0, message: 'Thuốc bị bỏ khỏi đơn nhưng BN đã nhận — cần tư vấn ngừng dùng' }));
    rx.status = 'SUPERSEDED';
    const nv = { ...rx, prescriptionId: id('RX'), version: rx.version + 1, supersedes: rx.prescriptionId, items, status: 'ISSUED', issuedAt: new Date().toISOString(), amendReason: body.reason };
    nv.signature = { ...rx.signature, value: crypto.createHash('sha256').update(JSON.stringify(items) + nv.prescriptionId).digest('base64').slice(0, 32) + '…' };
    nv.rxCode = `${rx.rxCode.split('-')[0]}-v${nv.version}`; prescriptions[nv.prescriptionId] = nv; rx.supersededBy = nv.prescriptionId;
    audit(u, 'AMEND', { type: 'Prescription', id: nv.prescriptionId, patientRef: rx.patientId }, { result: 'PERMIT', policyId: 'POL-05' }, { reason: body.reason });
    return send(res, 201, { previous: { prescriptionId: rx.prescriptionId, status: 'SUPERSEDED', dispensedBefore: rx.items.map(i => ({ itemId: i.itemId, drugName: i.drugName, dispensedQty: i.dispensedQty })) }, current: { ...rxView(nv), status: rxStatus(nv) }, warnings, events: [{ type: 'PrescriptionAmended', to: ['AC-PharmacyGateway', 'AC-Notification'], status: 'PUBLISHED' }] }); }

  // AS-ReceivePrescription (nhà thuốc, POL-04)
  if (m === 'GET' && (mm = p.match(/^\/pharmacy\/prescriptions\/([^/]+)$/))) { if (!need(u, res, 'BR-DuocSi')) return;
    const rx = Object.values(prescriptions).find(r => r.rxCode === mm[1]);
    const ok = rx && url.searchParams.get('verifier') === patients[rx.patientId].phone.slice(-4);
    if (ok && rx.assignedPharmacyId && rx.assignedPharmacyId !== u.pharmacyId && ['ISSUED'].includes(rxStatus(rx)) === false) {
      audit(u, 'READ', { type: 'Prescription', id: rx.prescriptionId, patientRef: rx.patientId }, { result: 'DENY', policyId: 'POL-04' }, { outcome: 'FAILURE', reason: 'ASSIGNED_TO_OTHER_PHARMACY' });
      return problem(res, 403, 'Đơn đang giao nhà thuốc khác', `Đơn đã được ${rx.assignedPharmacyId} nhận và cấp (ASSUMP-10)`, { policyId: 'POL-04' }); }
    if (ok && rx.assignedPharmacyId && rx.assignedPharmacyId !== u.pharmacyId && rxStatus(rx) === 'ISSUED') rx.assignedPharmacyId = u.pharmacyId; // BN đổi nhà thuốc khi chưa cấp: chuyển giao
    if (ok && !rx.assignedPharmacyId) rx.assignedPharmacyId = u.pharmacyId; // nhà thuốc đầu tiên tra đơn hợp lệ nhận giao đơn
    audit(u, 'READ', { type: 'Prescription', id: rx?.prescriptionId || mm[1], patientRef: rx?.patientId || null }, { result: ok ? 'PERMIT' : 'DENY', policyId: 'POL-04' }, { outcome: ok ? 'SUCCESS' : 'FAILURE' });
    if (!ok) return problem(res, 404, 'Không tìm thấy đơn', 'Mã đơn hoặc mã xác minh (4 số cuối SĐT) không đúng', { policyId: 'POL-04' });
    const pt = patients[rx.patientId]; const st = rxStatus(rx);
    return send(res, 200, { rxCode: rx.rxCode, prescriptionId: rx.prescriptionId, version: rx.version, status: st, patient: { fullName: pt.fullName, birthYear: pt.birthYear },
      prescriber: users['tok-' + rx.practitionerId]?.name || rx.practitionerId, issuedAt: rx.issuedAt, signatureValid: !!rx.signature || !!rx.supersedes, items: rx.items,
      dispensable: st === 'ISSUED' || st === 'PARTIALLY_DISPENSED', note: st === 'SUPERSEDED' ? `Đơn đã được thay bằng phiên bản mới (${prescriptions[rx.supersededBy]?.rxCode})` : undefined }); }

  // Biến thể C (FR-C3): nhà thuốc xác nhận đã nhận thông báo sửa/thu hồi đơn
  if (m === 'POST' && (mm = p.match(/^\/pharmacy\/prescriptions\/([^/]+)\/ack$/))) { if (!need(u, res, 'BR-DuocSi')) return;
    const rx = Object.values(prescriptions).find(r => r.rxCode === mm[1]); if (!rx) return problem(res, 404, 'Không tìm thấy đơn', mm[1]);
    if (!['REVOKED', 'SUPERSEDED'].includes(rx.status)) return problem(res, 409, 'Không có thay đổi cần xác nhận', `Đơn đang ở trạng thái ${rxStatus(rx)}`);
    rx.acks = rx.acks || []; const ack = { pharmacyId: u.pharmacyId, pharmacistId: u.userId, event: rx.status === 'REVOKED' ? 'PrescriptionRevoked' : 'PrescriptionAmended', ackAt: new Date().toISOString() }; rx.acks.push(ack);
    audit(u, 'ACK_CHANGE', { type: 'Prescription', id: rx.prescriptionId, patientRef: rx.patientId }, { result: 'PERMIT', policyId: 'POL-04' }, {});
    return send(res, 200, ack); }

  // AS-RecordDispense (idempotent, NFR-DAT-01)
  if (m === 'POST' && p === '/pharmacy/dispenses') { if (!need(u, res, 'BR-DuocSi')) return;
    const key = req.headers['idempotency-key']; if (!key) return problem(res, 400, 'Thiếu Idempotency-Key', 'Mỗi lần ghi nhận cấp thuốc phải có khóa duy nhất');
    if (idem[key]) { const prev = idem[key]; return send(res, 200, { ...prev.body, idempotentReplay: true }); }
    const rx = Object.values(prescriptions).find(r => r.rxCode === body.rxCode);
    if (!rx) return problem(res, 404, 'Không tìm thấy đơn', 'rxCode không tồn tại');
    const st = rxStatus(rx);
    const fail = (code, title, detail, extra) => { audit(u, 'DISPENSE', { type: 'Prescription', id: rx.prescriptionId, patientRef: rx.patientId }, { result: 'DENY', policyId: extra.policyId || 'POL-05' }, { outcome: 'FAILURE' }); return problem(res, code, title, detail, extra); };
    if (rx.assignedPharmacyId && rx.assignedPharmacyId !== u.pharmacyId) return fail(403, 'Đơn đang giao nhà thuốc khác', `Đơn giao ${rx.assignedPharmacyId}; BN cần đổi nhà thuốc trước khi cấp (ASSUMP-10)`, { policyId: 'POL-04' });
    if (!['ISSUED', 'PARTIALLY_DISPENSED'].includes(st)) return fail(409, 'Đơn không còn hiệu lực để cấp', `Trạng thái: ${st}`, { policyId: 'POL-05', currentStatus: st });
    for (const line of body.items || []) { const it = rx.items.find(i => i.itemId === line.itemId);
      if (!it) return fail(422, 'Dòng thuốc không tồn tại', line.itemId, {});
      if (it.controlled && u.pharmacyType !== 'INTERNAL') return fail(403, 'Thuốc kiểm soát đặc biệt', `${it.drugName}: chỉ nhà thuốc nội bộ được cấp (CON-04)`, { policyId: 'POL-06' });
      if (it.dispensedQty + line.quantity > it.quantity) return fail(409, 'Vượt số lượng kê', `${it.drugName}: đã cấp ${it.dispensedQty}/${it.quantity}, yêu cầu thêm ${line.quantity}`, { policyId: 'NFR-DAT-01' }); }
    (body.items || []).forEach(line => { rx.items.find(i => i.itemId === line.itemId).dispensedQty += line.quantity; });
    const dr = { dispenseId: id('DSP'), idempotencyKey: key, rxCode: rx.rxCode, prescriptionId: rx.prescriptionId, pharmacyId: u.pharmacyId, pharmacistId: u.userId, items: body.items, dispensedAt: body.dispensedAt || new Date().toISOString(), prescriptionStatus: rxStatus(rx) };
    dispenses[dr.dispenseId] = dr; idem[key] = { code: 201, body: dr };
    audit(u, 'DISPENSE', { type: 'Prescription', id: rx.prescriptionId, patientRef: rx.patientId }, { result: 'PERMIT', policyId: 'POL-04' }, { correlationId: corr });
    return send(res, 201, dr, { Location: `/pharmacy/dispenses/${dr.dispenseId}` }); }

  // Biến thể B: đồng bộ lô cấp thuốc offline
  if (m === 'POST' && p === '/pharmacy/sync') { if (!need(u, res, 'BR-DuocSi')) return;
    const results = (body.dispenses || []).map(d => {
      if (idem[d.idempotencyKey]) return { idempotencyKey: d.idempotencyKey, result: 'DUPLICATE', dispenseId: idem[d.idempotencyKey].body.dispenseId };
      const rx = Object.values(prescriptions).find(r => r.rxCode === d.rxCode);
      if (!rx) return { idempotencyKey: d.idempotencyKey, result: 'REJECTED', reason: 'Không tìm thấy đơn' };
      const st = rxStatus(rx);
      const over = (d.items || []).find(l => { const it = rx.items.find(i => i.itemId === l.itemId); return !it || it.dispensedQty + l.quantity > it.quantity; });
      if (!['ISSUED', 'PARTIALLY_DISPENSED'].includes(st) || over) {
        const cid = id('REC'); audit(u, 'DISPENSE_SYNC', { type: 'Prescription', id: rx.prescriptionId, patientRef: rx.patientId }, { result: 'DENY', policyId: 'FR-B3' }, { outcome: 'FAILURE', reason: 'CONFLICT ' + cid });
        return { idempotencyKey: d.idempotencyKey, result: 'CONFLICT', reconciliationCaseId: cid, reason: over ? 'Cấp vượt số lượng (có thể đã cấp ở nơi khác)' : `Đơn ở trạng thái ${st}`, action: 'Chuyển BR-QuanLy + dược sĩ đối soát thủ công' }; }
      d.items.forEach(l => { rx.items.find(i => i.itemId === l.itemId).dispensedQty += l.quantity; });
      const dr = { dispenseId: id('DSP'), idempotencyKey: d.idempotencyKey, rxCode: rx.rxCode, prescriptionId: rx.prescriptionId, pharmacyId: u.pharmacyId, pharmacistId: u.userId, items: d.items, dispensedAt: d.dispensedAt, offline: true, prescriptionStatus: rxStatus(rx) };
      dispenses[dr.dispenseId] = dr; idem[d.idempotencyKey] = { code: 201, body: dr };
      audit(u, 'DISPENSE_SYNC', { type: 'Prescription', id: rx.prescriptionId, patientRef: rx.patientId }, { result: 'PERMIT', policyId: 'POL-04' }, {});
      return { idempotencyKey: d.idempotencyKey, result: 'ACCEPTED', dispenseId: dr.dispenseId }; });
    return send(res, 200, { batchId: id('SYNC'), results }); }

  // Biến thể A: ghép định danh
  if (m === 'GET' && p === '/patients/match') { if (!need(u, res, 'BR-LeTan', 'BR-BacSi')) return;
    const idn = url.searchParams.get('idNumber'), name = (url.searchParams.get('fullName') || '').toLowerCase(), by = Number(url.searchParams.get('birthYear'));
    const cands = Object.values(patients).map(pt => { let score = 0; if (idn && pt.idNumber === idn) score += 0.9; if (name && pt.fullName.toLowerCase() === name) score += 0.06; if (by && pt.birthYear === by) score += 0.04;
      return { patientId: pt.patientId, facility: pt.facility, score: Math.round(score * 100) / 100 }; }).filter(c => c.score > 0).sort((a, b) => b.score - a.score);
    audit(u, 'MATCH', { type: 'Patient', id: cands[0]?.patientId || null }, { result: 'PERMIT', policyId: 'RBAC' }, {});
    const decision = cands[0]?.score >= 0.9 ? 'AUTO_LINK' : cands.length ? 'MANUAL_REVIEW' : 'NO_MATCH';
    return send(res, 200, { decision, candidates: cands }); }

  // AS-QueryAudit (chỉ DPO; BN xem vết hồ sơ của mình)
  if (m === 'GET' && p === '/audit-events') { if (!need(u, res, 'BR-QuanTriBaoMat', 'BR-BenhNhan')) return;
    let list = auditLog; const pr = u.role === 'BR-BenhNhan' ? u.patientId : url.searchParams.get('patientRef');
    if (pr) list = list.filter(e => e.resource?.patientRef === pr);
    if (url.searchParams.get('decision')) list = list.filter(e => e.decision?.result === url.searchParams.get('decision'));
    audit(u, 'READ', { type: 'AuditEvent', patientRef: pr || null }, { result: 'PERMIT', policyId: 'RBAC' }, {});
    return send(res, 200, { count: list.length, items: list }); }
  if (m === 'GET' && p === '/audit-events/verify') { if (!need(u, res, 'BR-QuanTriBaoMat')) return; return send(res, 200, verifyChain()); }
  if (m === 'POST' && p === '/_demo/tamper') { // CHỈ CÓ TRONG MOCK: giả lập kẻ xấu sửa 1 bản ghi để minh họa verify
    if (!need(u, res, 'BR-QuanTriBaoMat')) return; const e = auditLog[body.index ?? 0]; if (!e) return problem(res, 404, 'Không có bản ghi', '');
    e.decision = { ...e.decision, result: 'PERMIT' }; e.actor = { ...e.actor, userId: 'someone-else' }; return send(res, 200, { tampered: e.eventId }); }
  if (m === 'POST' && p === '/_demo/reset') { Object.keys(appointments).forEach(k => delete appointments[k]); Object.keys(encounters).forEach(k => delete encounters[k]);
    Object.keys(prescriptions).forEach(k => delete prescriptions[k]); Object.keys(dispenses).forEach(k => delete dispenses[k]); Object.keys(breakGlass).forEach(k => delete breakGlass[k]);
    Object.keys(idem).forEach(k => delete idem[k]); auditLog.length = 0; lastHash = '0'.repeat(64); slots.forEach(s => s.available = true); seq = 1; return send(res, 200, { reset: true }); }

  return problem(res, 404, 'Không có endpoint', `${m} ${p}`);
});
server.listen(PORT, () => console.log(`E-Health mock API: http://localhost:${PORT}  (UI: /, OpenAPI: /openapi.yaml)`));
