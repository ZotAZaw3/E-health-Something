#!/usr/bin/env bash
# Thử nghiệm tình huống bất thường (05-verification/change-scenario.md, mục 1):
# Hệ thống đơn thuốc quốc gia ngừng giữa giờ cao điểm. Cần mock đang chạy: node mock-server/server.js
B=${BASE:-http://localhost:4010}
j() { python3 -c 'import sys,json; d=sys.stdin.read(); print(json.dumps(json.loads(d),ensure_ascii=False,indent=2) if d.strip() else "")'; }
call() { local tok=$1 m=$2 path=$3 data=$4 extra=$5; echo; echo "\$ $m $path  [token: $tok]${data:+  body: $data}"
  curl -s -w '\n<<HTTP %{http_code}>>\n' -X "$m" "$B$path" -H "Authorization: Bearer $tok" -H 'Content-Type: application/json' ${extra:+-H "$extra"} ${data:+-d "$data"} > /tmp/ehr.$$
  sed '$d' /tmp/ehr.$$ | j; tail -1 /tmp/ehr.$$; }
last() { sed '$d' /tmp/ehr.$$ | python3 -c "import sys,json; d=json.load(sys.stdin); print(eval('d'+sys.argv[1]))" "$1"; }
h() { echo; echo "================ $* ================"; }
curl -s -X POST $B/_demo/reset >/dev/null
h "0. Chuẩn bị: BN P001 đặt lịch, check-in (luồng chính BP-01, BP-02)"
call tok-bn-p001 POST /appointments '{"slotId":"S-20261105-AN-1","reason":"Ho"}' >/dev/null; QR=$(last "['checkInCode']")
call tok-letan-cs1 POST /encounters "{\"checkInCode\":\"$QR\",\"idNumber\":\"001085012345\"}" >/dev/null; ENC=$(last "['encounterId']")
h "1. SỰ CỐ: Hệ thống đơn thuốc quốc gia ngừng (giả lập)"
call tok-dpo POST /_demo/national-rx '{"up":false}'
h "2. Bác sĩ vẫn kê + ký đơn được (PR-01: không chặn khám chữa bệnh); đơn vào outbox, trạng thái liên thông QUEUED"
call tok-bs-an POST /prescriptions "{\"encounterId\":\"$ENC\",\"items\":[{\"drugCode\":\"CEFU500\",\"dosage\":\"1 viên x 2\",\"quantity\":14}]}" >/dev/null; RX=$(last "['prescriptionId']")
call tok-bs-an POST /prescriptions/$RX/issue; CODE=$(last "['rxCode']")
h "3. Nhà thuốc vẫn tra đơn qua cổng của phòng khám (không phụ thuộc hệ thống quốc gia) và cấp thuốc"
call tok-ds-nt01 GET "/pharmacy/prescriptions/$CODE?verifier=5678"
call tok-ds-nt01 POST /pharmacy/dispenses "{\"rxCode\":\"$CODE\",\"items\":[{\"itemId\":\"L1\",\"quantity\":14}]}" "Idempotency-Key: NT01-OUTAGE-0001"
h "4. Giám sát: outbox đang tồn 1 đơn chưa liên thông"
call tok-dpo GET /_demo/national-rx
h "5. Hệ thống quốc gia hoạt động lại → gửi bù từ outbox, ghi audit SUBMIT_NATIONAL_RX"
call tok-dpo POST /_demo/national-rx '{"up":true}'
h "6. Gọi lại lần nữa (giả lập job chạy lặp) → không gửi trùng (idempotent)"
call tok-dpo POST /_demo/national-rx '{"up":true}'
h "7. Kiểm tra trạng thái đơn và chuỗi audit vẫn hợp lệ"
call tok-bs-an GET /prescriptions/$RX
call tok-dpo GET /audit-events/verify
