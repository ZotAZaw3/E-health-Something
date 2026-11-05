# Kẻ viền bảng, căn giữa ảnh, ngắt trang sau Mục lục — chạy sau pandoc
import sys
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
d = Document(sys.argv[1])
for t in d.tables:
    tblPr = t._tbl.tblPr
    b = OxmlElement('w:tblBorders')
    for e in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        x = OxmlElement(f'w:{e}'); x.set(qn('w:val'), 'single'); x.set(qn('w:sz'), '4'); x.set(qn('w:color'), '808080'); b.append(x)
    old = tblPr.find(qn('w:tblBorders'))
    if old is not None: tblPr.remove(old)
    tblPr.append(b)
    if len(t.columns) >= 7:
        from docx.shared import Pt
        for row in t.rows:
            for c in row.cells:
                for pp in c.paragraphs:
                    for r in pp.runs: r.font.size = Pt(9)
    for c in t.rows[0].cells:
        for p in c.paragraphs:
            for r in p.runs: r.bold = True
for p in d.paragraphs:
    if p._p.xpath('.//pic:pic'): p.alignment = WD_ALIGN_PARAGRAPH.CENTER
d.save(sys.argv[1])
