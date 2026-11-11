#!/usr/bin/env bash
# Kịch bản demo API (cần: node mock-server/server.js đang chạy, curl, python3 để in đẹp)
# Chạy: bash demo.sh [lõi|A|B|C|all]   (mặc định: all)
B=${BASE:-http://localhost:4010}; MODE=${1:-all}
j() { python3 -c 'import sys,json; d=sys.stdin.read(); print(json.dumps(json.loads(d),ensure_ascii=False,indent=2) if d.strip() else "")'; }
call() { local tok=$1 m=$2 path=$3 data=$4 extra=$5; echo; echo "\$ $m $path  [token: $tok]${data:+  body: $data}"
  curl -s -w '\n<<HTTP %{http_code}>>\n' -X "$m" "$B$path" -H "Authorization: Bearer $tok" -H 'Content-Type: application/json' ${extra:+-H "$extra"} ${data:+-d "$data"} > /tmp/ehr.$$
  sed '$d' /tmp/ehr.$$ | j; tail -1 /tmp/ehr.$$; }
last() { sed '$d' /tmp/ehr.$$ | python3 -c "import sys,json; d=json.load(sys.stdin); print(eval('d'+sys.argv[1]))" "$1"; }
h() { echo; echo "================ $* ================"; }

curl -s -X POST $B/_demo/reset >/dev/null
h "LUỒNG CHÍNH (E2E) — BP-01 → BP-05"
h "1. BN P001 xem khung giờ và đặt lịch (AS-BookAppointment, FR-01)"
call tok-bn-p001 GET "/slots?specialty=NOI"
call tok-bn-p001 POST /appointments '{"slotId":"S-20261105-AN-1","reason":"Ho, sốt 3 ngày"}'; QR=$(last "['checkInCode']")
h "1b. Ngoại lệ phụ: người khác đặt trùng khung giờ → 409 + gợi ý"
call tok-letan-cs1 POST /appointments '{"slotId":"S-20261105-AN-1","patientId":"P002"}'
h "1c. BN P002 đặt khung 08:15 rồi đổi sang 08:30 (FR-02, khung cũ được giải phóng)"
call tok-letan-cs1 POST /appointments '{"slotId":"S-20261105-AN-2","patientId":"P002"}'; APT2=$(last "['appointmentId']")
call tok-letan-cs1 PATCH /appointments/$APT2 '{"action":"RESCHEDULE","newSlotId":"S-20261105-AN-3"}'
h "2. Lễ tân check-in bằng QR + CCCD (AS-CheckIn, AS-VerifyInsurance, FR-03)"
call tok-letan-cs1 POST /encounters "{\"checkInCode\":\"$QR\",\"idNumber\":\"001085012345\"}"; ENC=$(last "['encounterId']")
h "3. BS An (được phân công) xem hàng chờ và hồ sơ (AS-ViewMedicalRecord, POL-01 PERMIT)"
call tok-bs-an GET /encounters
call tok-bs-an GET /patients/P001/records
h "4. BS An kê Amoxicillin → hệ thống chặn vì dị ứng penicillin (AS-CheckDrugSafety, FR-05)"
call tok-bs-an POST /prescriptions "{\"encounterId\":\"$ENC\",\"diagnosis\":{\"icd10\":\"J20.9\",\"text\":\"Viêm phế quản cấp\"},\"items\":[{\"drugCode\":\"AMOX500\",\"dosage\":\"1 viên x 2 lần/ngày\",\"quantity\":14},{\"drugCode\":\"PARA500\",\"dosage\":\"khi sốt\",\"quantity\":10}]}"
h "5. BS An đổi sang Cefuroxim → đơn nháp, rồi ký số và phát hành (FR-05, FR-06, CON-03)"
call tok-bs-an POST /prescriptions "{\"encounterId\":\"$ENC\",\"diagnosis\":{\"icd10\":\"J20.9\",\"text\":\"Viêm phế quản cấp\"},\"items\":[{\"drugCode\":\"CEFU500\",\"dosage\":\"1 viên x 2 lần/ngày, 7 ngày\",\"quantity\":14},{\"drugCode\":\"PARA500\",\"dosage\":\"khi sốt\",\"quantity\":10}]}"; RX=$(last "['prescriptionId']")
call tok-bs-an POST /prescriptions/$RX/issue; CODE=$(last "['rxCode']")
h "6. Nhà thuốc đối tác NT-01 tra đơn bằng mã + 4 số cuối SĐT (AS-ReceivePrescription, POL-04)"
call tok-ds-nt01 GET "/pharmacy/prescriptions/$CODE?verifier=5678"
h "7. NT-01 ghi nhận cấp đủ thuốc, có Idempotency-Key (AS-RecordDispense, NFR-DAT-01)"
call tok-ds-nt01 POST /pharmacy/dispenses "{\"rxCode\":\"$CODE\",\"items\":[{\"itemId\":\"L1\",\"quantity\":14},{\"itemId\":\"L2\",\"quantity\":10}]}" "Idempotency-Key: NT01-20261105-000001"
h "7b. Mạng chập chờn, phần mềm nhà thuốc gửi lại cùng khóa → không tạo bản ghi thứ 2"
call tok-ds-nt01 POST /pharmacy/dispenses "{\"rxCode\":\"$CODE\",\"items\":[{\"itemId\":\"L1\",\"quantity\":14},{\"itemId\":\"L2\",\"quantity\":10}]}" "Idempotency-Key: NT01-20261105-000001"
h "7c. Nhà thuốc khác cố cấp đơn đã giao NT-01 → 403 (ASSUMP-10); NT-01 cấp thêm → 409 vượt số lượng"
call tok-ds-nbcs1 POST /pharmacy/dispenses "{\"rxCode\":\"$CODE\",\"items\":[{\"itemId\":\"L1\",\"quantity\":14}]}" "Idempotency-Key: NBCS1-20261105-000009"
call tok-ds-nt01 POST /pharmacy/dispenses "{\"rxCode\":\"$CODE\",\"items\":[{\"itemId\":\"L1\",\"quantity\":1}]}" "Idempotency-Key: NT01-20261105-000099"

if [[ $MODE == all || $MODE == lõi ]]; then
h "NGOẠI LỆ LÕI — truy cập trái phép bị chặn, break-glass, kiểm chứng nhật ký (NFR-SEC-02/03)"
h "E1. BS Bình (không phụ trách P001) mở hồ sơ → 403, ghi DENY"
call tok-bs-binh GET /patients/P001/records
h "E2. BS Bình khai báo truy cập khẩn cấp có lý do → được xem 4 giờ, có cờ breakGlass"
call tok-bs-binh POST /access/break-glass '{"patientId":"P001","reason":"BN khó thở tại phòng chờ, BS An đang làm thủ thuật"}'
call tok-bs-binh GET /patients/P001/records
h "E3. Break-glass không cho phép kê đơn"
call tok-bs-binh POST /prescriptions "{\"encounterId\":\"$ENC\",\"items\":[{\"drugCode\":\"PARA500\",\"quantity\":5}]}"
h "E4. Lễ tân cố xem bệnh án → 403 (RBAC)"
call tok-letan-cs1 GET /patients/P001/records
h "E5. DPO xem các lần bị từ chối và break-glass trên hồ sơ P001"
call tok-dpo GET "/audit-events?patientRef=P001&decision=DENY"
h "E6. DPO kiểm chứng chuỗi băm → hợp lệ; giả lập sửa 1 bản ghi DENY thành PERMIT → phát hiện"
call tok-dpo GET /audit-events/verify
IDX=$(curl -s "$B/audit-events" -H 'Authorization: Bearer tok-dpo' | python3 -c "import sys,json; d=json.load(sys.stdin)['items']; print([i for i,e in enumerate(d) if e['decision']['result']=='DENY'][0])")
call tok-dpo POST /_demo/tamper "{\"index\":$IDX}"
call tok-dpo GET /audit-events/verify
fi

if [[ $MODE == all || $MODE == C ]]; then
h "BIẾN THỂ C — sửa/thu hồi đơn"
call tok-bs-an POST /prescriptions/$RX/revoke '{"reason":"Kê nhầm liều"}'
h "C1. Đơn đã cấp đủ → không thu hồi được, bác sĩ lập phiên bản điều chỉnh (đơn cũ SUPERSEDED, giữ lịch sử)"
call tok-bs-an POST /prescriptions/$RX/amend '{"reason":"Giảm liều Paracetamol do men gan tăng","items":[{"drugCode":"CEFU500","dosage":"1 viên x 2 lần/ngày, 7 ngày","quantity":14},{"drugCode":"PARA500","dosage":"tối đa 2 viên/ngày","quantity":4}]}'
call tok-ds-nt01 GET "/pharmacy/prescriptions/$CODE?verifier=5678"
call tok-ds-nt01 POST "/pharmacy/prescriptions/$CODE/ack"
h "C2. Đơn thứ hai chưa cấp → thu hồi được, nhà thuốc tra thấy REVOKED và không cấp được"
call tok-bs-an POST /prescriptions "{\"encounterId\":\"$ENC\",\"items\":[{\"drugCode\":\"LORA10\",\"dosage\":\"1 viên/ngày\",\"quantity\":7}]}"; RX2=$(last "['prescriptionId']")
call tok-bs-an POST /prescriptions/$RX2/issue; CODE2=$(last "['rxCode']")
call tok-bs-an POST /prescriptions/$RX2/revoke '{"reason":"BN báo đang dùng thuốc tương tự"}'
call tok-ds-nt01 POST /pharmacy/dispenses "{\"rxCode\":\"$CODE2\",\"items\":[{\"itemId\":\"L1\",\"quantity\":7}]}" "Idempotency-Key: NT01-20261105-000002"
fi

if [[ $MODE == all || $MODE == B ]]; then
h "BIẾN THỂ B — nhà thuốc mất kết nối, đồng bộ lại (ASSUMP-10: đơn chỉ giao 1 nhà thuốc)"
call tok-bs-an POST /prescriptions "{\"encounterId\":\"$ENC\",\"items\":[{\"drugCode\":\"PARA500\",\"dosage\":\"khi sốt\",\"quantity\":10}]}"; RX3=$(last "['prescriptionId']")
call tok-bs-an POST /prescriptions/$RX3/issue; CODE3=$(last "['rxCode']")
h "B1. NT-01 tra đơn khi còn mạng → đơn được giao NT-01 và lưu vào bộ nhớ đệm của agent"
call tok-ds-nt01 GET "/pharmacy/prescriptions/$CODE3?verifier=5678"
h "B2. NT-01 mất mạng: quầy 1 cấp 10 viên (dispenseId NT01-OFF-001); quầy 2 không biết, cấp lại 10 viên (NT01-OFF-002)"
h "B3. Có mạng lại, agent đồng bộ lô: bản ghi đã gửi trước đó + 2 bản ghi offline"
call tok-ds-nt01 POST /pharmacy/sync "{\"dispenses\":[{\"idempotencyKey\":\"NT01-20261105-000001\",\"rxCode\":\"$CODE\",\"items\":[{\"itemId\":\"L1\",\"quantity\":14}]},{\"idempotencyKey\":\"NT01-OFF-001\",\"rxCode\":\"$CODE3\",\"dispensedAt\":\"2026-11-05T10:12:00+07:00\",\"items\":[{\"itemId\":\"L1\",\"quantity\":10}]},{\"idempotencyKey\":\"NT01-OFF-002\",\"rxCode\":\"$CODE3\",\"dispensedAt\":\"2026-11-05T10:20:00+07:00\",\"items\":[{\"itemId\":\"L1\",\"quantity\":10}]}]}"
fi

if [[ $MODE == all || $MODE == A ]]; then
h "BIẾN THỂ A — ghép định danh liên cơ sở"
call tok-letan-cs1 GET "/patients/match?idNumber=001190067890"
call tok-letan-cs1 GET "/patients/match?fullName=Tr%E1%BA%A7n%20Th%E1%BB%8B%20Lan&birthYear=1990"
fi
rm -f /tmp/ehr.$$
