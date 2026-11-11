# Kiến trúc HTTT cho E-Health ngoại trú (BTL 2026)

Bài tập lớn môn Kiến trúc Hệ thống thông tin: kiến trúc doanh nghiệp (ArchiMate 3.1 + BPMN + ADR) cho chuỗi **đặt lịch → tiếp đón → khám → kê đơn điện tử → cấp thuốc** của *Phòng khám Đa khoa An Tâm* (hư cấu, 2 cơ sở, ~500 lượt/ngày, 6 nhà thuốc đối tác, lộ trình 12 tháng).

## Cấu trúc thư mục

| Thư mục | Nội dung | Phụ trách |
|---|---|---|
| `00-brief/` | Rà soát file hướng dẫn so với đề | TV3 |
| `01-vision/catalog.md` | Danh mục mã chung: giả định, stakeholder, driver, goal, outcome, principle, FR/NFR, ràng buộc, phần tử Business | TV1 |
| `02-models/` | Mô hình Archi (Open Exchange XML), BPMN (`bpmn/`), ảnh xuất view (`exports/`), danh mục ứng dụng (`app-catalog.md`) và công nghệ (`tech-catalog.md`, `technology.md`) | TV1, TV2, TV3 |
| `03-adr/` | ADR-001 kiểu tích hợp, ADR-002 RBAC+ABAC, ADR-003 kho audit, ADR-004 mô hình dữ liệu đơn thuốc | TV2, TV3 |
| `04-prototype/` | OpenAPI, mock server Node (không cần cài thư viện), giao diện thử, kịch bản curl, ảnh chụp màn hình | TV3 |
| `05-verification/` | Ma trận truy vết (RTM), gap & roadmap, sổ rủi ro, kịch bản thay đổi/bất thường (`change-scenario.md`), câu hỏi bảo vệ (`defense-qa.md`) | TV2, TV3 |
| `06-docs/` | Bản Markdown của tài liệu TV1 và TV2 (xuất từ Claude Docs) | TV1, TV2 |
| `07-report/` | Báo cáo tổng hợp (`BaoCao-BTL-EHealth.md` → `.docx` bằng `build_report.sh`, cần pandoc) | Cả nhóm |
| `results/` | **Bản nộp**: gom mọi sản phẩm theo đề vào một chỗ, kèm bảng đối chiếu ([`results/README.md`](results/README.md)) | Cả nhóm |

## Mở mô hình

- **Archi:** File → Import → Open Exchange XML Model, chọn **`02-models/archimate/ehealth-full-model.xml`** (mô hình gộp đủ các tầng, 25 view; sinh lại bằng `python3 02-models/archimate/build_full_model.py`, xuất ảnh bằng `render_views.py`). File `ehealth-full-model.archimate` mở thẳng được trong Archi; ảnh view xuất bằng Archi qua `export_archi.ps1`. Hai file nguồn riêng của TV1 và TV3 vẫn giữ để tham khảo, không import chung với file gộp vì sẽ trùng phần tử.
- **BPMN:** mở các file `02-models/bpmn/*.bpmn` bằng Camunda Modeler hoặc bpmn.io.

## Chạy prototype

```bash
cd 04-prototype
node mock-server/server.js   # http://localhost:4010 (Node >= 18)
bash demo.sh all             # hoặc: lõi | A | B | C
```

Chi tiết: [`04-prototype/README.md`](04-prototype/README.md).
