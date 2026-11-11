# results/ — Kết quả nộp BTL E-Health ngoại trú

Thư mục này gom **mọi sản phẩm nộp** theo đề `De_BTL_Kien_truc_HTTT_2026.pdf` (mục B, C) vào một chỗ. Đây là **bản sao**; các thư mục làm việc `00-brief/` … `07-report/` giữ nguyên, sửa ở đó rồi chép lại vào đây.

## Cấu trúc

| Thư mục | Nội dung |
|---|---|
| `01-bao-cao/` | Báo cáo `BaoCao-BTL-EHealth.docx` (bản chính), `.pdf` (xuất lại từ .docx ngày 11/11/2026, 34 trang), `.md` (nguồn) |
| `02-phan-tich-togaf/` | Bối cảnh, stakeholder, FR/NFR, ràng buộc, Vision (`catalog.md`, `TV1-motivation-business.md`), ứng dụng/dữ liệu (`app-catalog.md`, `TV2-application-data-adr.md`), công nghệ (`tech-catalog.md`, `technology.md`), Baseline/Target, Gap, Roadmap (`gap-roadmap.md`) |
| `03-so-do-nguon/` | File nguồn sơ đồ: ArchiMate `archimate/ehealth-full-model.archimate` (mở thẳng bằng Archi) + `.xml` (Open Exchange); BPMN `bpmn/*.bpmn` (luồng chính 01 + ngoại lệ 02A/02B/02C) |
| `04-anh-so-do/` | Ảnh xuất: 25 view ArchiMate (`archimate-views/V-*.png`, xuất từ Archi) và 4 sơ đồ BPMN (`bpmn/`) |
| `05-adr/` | Bộ ADR-001…004, mỗi ADR so sánh ≥ 2 phương án, có tiêu chí, lý do, đánh đổi |
| `06-kiem-chung/` | Ma trận truy vết `rtm.md`; tình huống bất thường/thay đổi `change-scenario.md` + `scenario-outage.sh` và kết quả chạy `scenario-outage-trace.txt`; sổ rủi ro `risk-register.md` |
| `07-prototype/` | Prototype mock: `openapi.yaml`, mock server Node (`node mock-server/server.js`), `demo.sh`, `api-trace.txt`, ảnh màn hình |
| `08-slide/` | `Slides-BTL-EHealth.pdf` (12 trang), bản chụp từ bộ slide trực tuyến |
| `09-bao-ve/` | Câu hỏi chuẩn bị bảo vệ `defense-qa.md` |

## Đối chiếu với đề

| Yêu cầu của đề | Có | Ở đâu |
|---|---|---|
| Bối cảnh, stakeholders, FR/NFR | ✅ | `02-phan-tich-togaf/catalog.md`; báo cáo chương 1–3 |
| Architecture Vision | ✅ | `02-phan-tich-togaf/`; view `V-MOT-1/2`, `V-STR-1..3` |
| Baseline/Target, Gap Analysis, roadmap | ✅ | `02-phan-tich-togaf/gap-roadmap.md`; view `V-BUS-0/1`, `V-TECH-0/1`, `V-MIG-1..3` |
| ArchiMate: Motivation, Business, Application, Technology, dữ liệu, chuyển đổi | ✅ | `03-so-do-nguon/archimate/` (25 view); ảnh ở `04-anh-so-do/archimate-views/` |
| BPMN ≥ 2 quy trình (luồng chính + ngoại lệ theo biến thể) | ✅ | `03-so-do-nguon/bpmn/` — 01 luồng chính + 3 ngoại lệ 02A/B/C |
| ≥ 2 ADR, mỗi ADR ≥ 2 phương án | ✅ | `05-adr/` — 4 ADR |
| Truy vết ≥ 3 yêu cầu xuyên mô hình | ✅ | `06-kiem-chung/rtm.md`; view `V-LAY-1/2` |
| Thử 01 tình huống bất thường/thay đổi | ✅ | `06-kiem-chung/change-scenario.md` + script và kết quả chạy |
| 06–08 rủi ro có đối sách | ✅ | `06-kiem-chung/risk-register.md` (8 rủi ro) |
| Prototype 01 kịch bản E2E + 01 ngoại lệ | ✅ | `07-prototype/` |
| Báo cáo 25–35 trang | ✅ | `01-bao-cao/` (34 trang) |
| Slide 10–12 trang | ✅ | `08-slide/` (12 trang) |

## Việc còn phải làm trước khi nộp

1. **Biến thể A/B/C**: khi biết biến thể được giao, giữ đúng một BPMN 02x và view `V-VAR-x`, sửa các chỗ đánh dấu ⟦BIẾN THỂ⟧ trong báo cáo (8 chỗ), dòng "Biến thể: [A / B / C]" trên slide 1 và slide 5.
2. **Báo cáo**: điền tên nhóm, MSSV ở trang bìa; xóa khung "Ghi chú biên tập"; mở .docx bằng Word, bấm F9 để cập nhật mục lục (bản PDF hiện chưa có mục lục), rồi xuất PDF lại; kiểm tra số hiệu văn bản pháp luật ở mục 3.3.
3. **Slide**: điền tên nhóm, thành viên ở slide 1. Bản PDF trong `08-slide/` là bản chụp; bản chính chỉnh sửa và xuất PPTX ở bộ slide trực tuyến của nhóm.
