# -*- coding: utf-8 -*-
"""Xuất ảnh PNG cho các view trong ehealth-full-model.xml (để chèn báo cáo/slide).
Chạy: node-less, cần Python + Playwright (chromium).  python3 render_views.py [VIEW_ID ...]
Ảnh ra: 02-models/exports/<VIEW_ID>.png. Ảnh chỉ để minh họa nhanh khi không có Archi. Ảnh trong exports/ hiện được xuất bằng Archi qua export_archi.ps1."""
import os, sys, html, math
from lxml import etree as ET
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'ehealth-full-model.xml'); OUTD = os.path.join(HERE, '..', 'exports')
NS = '{http://www.opengroup.org/xsd/archimate/3.0/}'; T = '{http://www.w3.org/2001/XMLSchema-instance}type'
root = ET.parse(SRC).getroot()
EL = {e.get('identifier'): (e.get(T), e.find(NS + 'name').text) for e in root.find(NS + 'elements')}
RL = {r.get('identifier'): (r.get(T), r.get('accessType')) for r in root.find(NS + 'relationships')}
LAYER = {'Motivation': ('#CCCCFF', 'Stakeholder Driver Assessment Goal Outcome Principle Requirement Constraint Value Meaning'),
         'Strategy': ('#F5DEAA', 'Capability Resource ValueStream CourseOfAction'),
         'Business': ('#FFF4B0', 'BusinessActor BusinessRole BusinessCollaboration BusinessInterface BusinessProcess BusinessFunction BusinessInteraction BusinessEvent BusinessService BusinessObject Contract Representation Product'),
         'Application': ('#C6F0F7', 'ApplicationComponent ApplicationCollaboration ApplicationInterface ApplicationFunction ApplicationProcess ApplicationEvent ApplicationService DataObject'),
         'Technology': ('#CDEBC0', 'Node Device SystemSoftware TechnologyService Artifact CommunicationNetwork Path TechnologyFunction'),
         'Migration': ('#FFE0E0', 'WorkPackage Deliverable ImplementationEvent Plateau Gap'),
         'Other': ('#F2F2F2', 'Grouping Location Junction')}
COLOR = {t: c for c, ts in LAYER.values() for t in ts.split()}
SHORT = {'BusinessProcess': 'Process', 'BusinessFunction': 'Function', 'BusinessService': 'Service', 'BusinessObject': 'Object', 'BusinessRole': 'Role',
         'BusinessActor': 'Actor', 'ApplicationComponent': 'Component', 'ApplicationService': 'App Service', 'ApplicationInterface': 'App Interface',
         'ApplicationFunction': 'App Function', 'DataObject': 'Data Object', 'TechnologyService': 'Tech Service', 'SystemSoftware': 'System SW',
         'CommunicationNetwork': 'Network', 'ValueStream': 'Value Stream', 'CourseOfAction': 'Course of Action', 'WorkPackage': 'Work Package',
         'ImplementationEvent': 'Impl. Event'}

def wrap(s, n):
    out, line = [], ''
    for w in s.split():
        if len(line) + len(w) + 1 > n and line: out.append(line); line = w
        else: line = (line + ' ' + w).strip()
    if line: out.append(line)
    return out[:3]

def clip(cx, cy, w, h, tx, ty):
    dx, dy = tx - cx, ty - cy
    if dx == 0 and dy == 0: return cx, cy
    s = min((w / 2) / abs(dx) if dx else 1e9, (h / 2) / abs(dy) if dy else 1e9)
    return cx + dx * s, cy + dy * s

def svg_view(v):
    nodes, boxes, conns = [], {}, []
    for n in v.iter(NS + 'node'):
        x, y, w, h = (int(n.get(k)) for k in 'xywh'); boxes[n.get('identifier')] = (x, y, w, h)
        if n.get('elementRef') and EL[n.get('elementRef')][0] == 'Grouping' and len(n.findall(NS + 'node')):
            nodes.insert(0, ('grp', x, y, w, h, None, EL[n.get('elementRef')][1]))
        elif n.get('elementRef'):
            t, name = EL[n.get('elementRef')]
            nodes.append(('el', x, y, w, h, t, name))
        else:
            lab = n.find(NS + 'label'); nodes.insert(0, ('grp', x, y, w, h, None, lab.text if lab is not None else ''))
    W = max(x + w for x, y, w, h in boxes.values()) + 20; H = max(y + h for x, y, w, h in boxes.values()) + 50
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="DejaVu Sans, Arial" font-size="11">',
         '<defs>'
         '<marker id="tri" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="9" markerHeight="9" orient="auto"><path d="M0,0L10,5L0,10z" fill="#333"/></marker>'
         '<marker id="open" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0L10,5L0,10" fill="none" stroke="#333"/></marker>'
         '<marker id="hollow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="10" markerHeight="10" orient="auto"><path d="M0,0L10,5L0,10z" fill="#fff" stroke="#333"/></marker>'
         '<marker id="dfill" viewBox="0 0 12 8" refX="0" refY="4" markerWidth="12" markerHeight="8" orient="auto"><path d="M0,4L6,0L12,4L6,8z" fill="#333"/></marker>'
         '<marker id="dhol" viewBox="0 0 12 8" refX="0" refY="4" markerWidth="12" markerHeight="8" orient="auto"><path d="M0,4L6,0L12,4L6,8z" fill="#fff" stroke="#333"/></marker>'
         '<marker id="dot" viewBox="0 0 8 8" refX="4" refY="4" markerWidth="6" markerHeight="6"><circle cx="4" cy="4" r="3.5" fill="#333"/></marker>'
         '</defs><rect width="100%" height="100%" fill="#fff"/>']
    for k, x, y, w, h, t, name in nodes:
        if k == 'grp':
            o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#FAFAFA" stroke="#999" stroke-dasharray="6 3" rx="3"/>'
                     f'<text x="{x+8}" y="{y+16}" font-weight="bold" fill="#555">{html.escape(name)}</text>')
    for c in v.iter(NS + 'connection'):
        t, acc = RL[c.get('relationshipRef')]
        sx, sy, sw, sh = boxes[c.get('source')]; tx, ty, tw, th = boxes[c.get('target')]
        scx, scy, tcx, tcy = sx + sw / 2, sy + sh / 2, tx + tw / 2, ty + th / 2
        if (t in ('Composition', 'Aggregation')) and sx <= tx and sy <= ty and sx + sw >= tx + tw and sy + sh >= ty + th: continue
        x1, y1 = clip(scx, scy, sw, sh, tcx, tcy); x2, y2 = clip(tcx, tcy, tw, th, scx, scy)
        st = {'Serving': ('', '', 'open'), 'Realization': ('4 3', '', 'hollow'), 'Composition': ('', 'dfill', ''), 'Aggregation': ('', 'dhol', ''),
              'Assignment': ('', 'dot', 'tri'), 'Access': ('2 3', '', 'open'), 'Flow': ('6 3', '', 'tri'), 'Triggering': ('', '', 'tri'),
              'Influence': ('6 3', '', 'open'), 'Association': ('', '', ''), 'Specialization': ('', '', 'hollow')}.get(t, ('', '', ''))
        dash, ms, me = st
        if t == 'Access' and acc == 'Read': x1, y1, x2, y2 = x2, y2, x1, y1   # mũi tên chỉ về phía đọc
        if t == 'Access' and acc == 'ReadWrite': ms = ''
        attrs = (f' stroke-dasharray="{dash}"' if dash else '') + (f' marker-start="url(#{ms})"' if ms else '') + (f' marker-end="url(#{me})"' if me else '')
        if abs(scy - tcy) < 5 and abs(scx - tcx) > max(sw, tw) * 1.3:   # cùng hàng, cách xa: vẽ cung để không đè lên hộp ở giữa
            sgn = 1 if (hash(c.get('identifier')) % 2) else -1
            ys, yt = (sy + sh, ty + th) if sgn > 0 else (sy, ty)
            bow = 25 + abs(scx - tcx) * 0.08
            x1, y1, x2, y2 = (scx, ys, tcx, yt)
            if t == 'Access' and acc == 'Read': x1, y1, x2, y2 = x2, y2, x1, y1
            o.append(f'<path d="M{x1:.0f},{y1:.0f} Q{(x1+x2)/2:.0f},{max(y1,y2)+sgn*bow if sgn>0 else min(y1,y2)-bow:.0f} {x2:.0f},{y2:.0f}" fill="none" stroke="#444" stroke-width="1.1"' + attrs + '/>')
            continue
        o.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#444" stroke-width="1.1"'
                 + (f' stroke-dasharray="{dash}"' if dash else '') + (f' marker-start="url(#{ms})"' if ms else '') + (f' marker-end="url(#{me})"' if me else '') + '/>')
    for k, x, y, w, h, t, name in nodes:
        if k != 'el': continue
        fill = COLOR.get(t, '#eee')
        rx = h / 2 if t.endswith('Service') or t in ('ValueStream',) else (12 if t in ('Capability', 'CourseOfAction') else 4)
        if t == 'Grouping':
            o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fff" stroke="#666" stroke-dasharray="8 4"/>')
        else:
            o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="#555"/>')
        code, _, rest = name.partition(' ')
        o.append(f'<text x="{x+w-5}" y="{y+11}" font-size="8.5" font-style="italic" fill="#666" text-anchor="end">{SHORT.get(t, t)}</text>')
        o.append(f'<text x="{x+w/2}" y="{y+24}" font-weight="bold" text-anchor="middle">{html.escape(code)}</text>')
        for i, ln in enumerate(wrap(rest, max(12, w // 6))):
            o.append(f'<text x="{x+w/2}" y="{y+37+i*11}" font-size="10" text-anchor="middle">{html.escape(ln)}</text>')
    o.append(f'<text x="20" y="{H-18}" font-size="13" fill="#555">{html.escape(v.find(NS+"name").text)}</text></svg>')
    return o, W, H

def main(ids):
    """Ghi SVG ra thư mục tạm rồi gọi Playwright (Node) chụp PNG ở tỉ lệ 2x."""
    import json, subprocess, tempfile
    tmp = tempfile.mkdtemp(); jobs = []
    for v in root.iter(NS + 'view'):
        if ids and v.get('identifier') not in ids: continue
        o, W, H = svg_view(v); f = os.path.join(tmp, v.get('identifier') + '.html')
        open(f, 'w').write('<body style="margin:0">' + ''.join(o) + '</body>')
        jobs.append([f, os.path.abspath(os.path.join(OUTD, v.get('identifier') + '.png')), W, H])
    js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();"
          "for(const [f,o,w,h] of %s){const p=await b.newPage({viewport:{width:w,height:h},deviceScaleFactor:2});"
          "await p.goto('file://'+f);await p.screenshot({path:o,fullPage:true});await p.close();console.log(o)}await b.close()})()") % json.dumps(jobs)
    subprocess.run(['node', '-e', js], check=True)

if __name__ == '__main__':
    main(sys.argv[1:])
