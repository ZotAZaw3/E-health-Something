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
| `05-verification/` | Ma trận truy vết (RTM), gap & roadmap, sổ rủi ro | TV2, TV3 |
| `06-docs/` | Bản Markdown của tài liệu TV1 và TV2 (xuất từ Claude Docs) | TV1, TV2 |

## Mở mô hình

- **Archi:** File → Import → Open Exchange XML Model, chọn `02-models/ehealth-tv1-motivation-business.xml` và `02-models/archimate/ehealth-tv3-exchange.xml` (sinh lại bằng `python3 02-models/archimate/gen_tv3_exchange.py`).
- **BPMN:** mở các file `02-models/bpmn/*.bpmn` bằng Camunda Modeler hoặc bpmn.io.

## Chạy prototype

```bash
cd 04-prototype
node mock-server/server.js   # http://localhost:4010 (Node >= 18)
bash demo.sh all             # hoặc: lõi | A | B | C
```

Chi tiết: [`04-prototype/README.md`](04-prototype/README.md).
