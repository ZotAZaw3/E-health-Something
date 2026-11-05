#!/usr/bin/env bash
# Dựng báo cáo Word + PDF từ BaoCao-BTL-EHealth.md (cần pandoc, python-docx, LibreOffice)
set -e; cd "$(dirname "$0")"
pandoc BaoCao-BTL-EHealth.md -o BaoCao-BTL-EHealth.docx --reference-doc=reference.docx --toc --toc-depth=2 --number-sections --lua-filter=imgw.lua --resource-path=.
python3 postprocess.py BaoCao-BTL-EHealth.docx
soffice --headless --convert-to pdf BaoCao-BTL-EHealth.docx >/dev/null 2>&1 && pdfinfo BaoCao-BTL-EHealth.pdf | grep Pages && rm -f BaoCao-BTL-EHealth.pdf  # PDF chỉ để đếm trang; Mục lục cần mở Word cập nhật
