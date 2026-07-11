import zipfile, re, html
from xml.etree import ElementTree as ET

DOCX = r"C:\Users\Henry\Documents\MY VAULT\Documents\New Tennis Knowledge\CAM_NANG_TENNIS_2026_CongThucDonGian.docx"
OUT = r"C:\Users\Henry\GITHUB\tennis-biomechanics\manual"
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

def wt(tag): return f'{{{W}}}{tag}'

with zipfile.ZipFile(DOCX) as z:
    root = ET.fromstring(z.read('word/document.xml').decode('utf-8'))

body = root.find(wt('body'))

def para_text(p):
    parts = []
    for t in p.iter(wt('t')):
        parts.append(t.text or '')
    return ''.join(parts)

def para_style(p):
    pPr = p.find(wt('pPr'))
    if pPr is not None:
        ps = pPr.find(wt('pStyle'))
        if ps is not None:
            return ps.get(wt('val'))
    return ''

# Walk body children preserving order
elements = []  # each: ('p', style, text) or ('tbl', rows)
for child in body:
    tag = child.tag
    if tag == wt('p'):
        elements.append(('p', para_style(child), para_text(child)))
    elif tag == wt('tbl'):
        rows = []
        for tr in child.findall(wt('tr')):
            cells = []
            for tc in tr.findall(wt('tc')):
                # keep inner paragraphs as separate lines
                cell_paras = [para_text(p) for p in tc.findall(wt('p'))]
                cell_paras = [cp.strip() for cp in cell_paras if cp.strip()]
                if len(cell_paras) <= 1:
                    cells.append(' '.join(cell_paras))
                else:
                    cells.append(cell_paras)  # multi-line cell
            rows.append(cells)
        elements.append(('tbl', None, rows))

# Split into chapters by Heading1 starting with CHƯƠNG
chapters = {}
order = []
cur = None
for kind, style, text in elements:
    if kind == 'p' and style == 'Heading1' and text.strip().upper().startswith('CHƯƠNG'):
        m = re.search(r'CHƯƠNG\s+(\d+)', text, re.IGNORECASE)
        if m:
            cur = int(m.group(1))
            chapters[cur] = []
            order.append(cur)
            continue
    if cur is not None:
        chapters[cur].append((kind, style, text))

def clean_title(raw):
    t = re.sub(r'^CHƯƠNG\s+', '', raw, flags=re.IGNORECASE).strip()
    t = re.split(r'\s*\(', t)[0].strip()  # drop parenthetical English
    return 'Chương ' + t

def esc(s):
    return html.escape(s, quote=True)

def is_formula(text):
    s = text.strip()
    if '=' not in s:
        return False
    if s.endswith(('.', '!', '?')):
        return False
    return len(s) <= 220

def render_chapter(els):
    out = []
    buf_list = []
    def flush_list():
        if buf_list:
            out.append('<ul>' + ''.join(f'<li>{esc(x)}</li>' for x in buf_list) + '</ul>')
            buf_list.clear()
    for kind, style, text in els:
        if kind == 'tbl':
            flush_list()
            rows = text
            if not rows:
                continue
            # single-cell table = callout box; cell may be multi-line list
            if len(rows) == 1 and len(rows[0]) == 1:
                cell = rows[0][0]
                if isinstance(cell, list):
                    lines = [l for l in cell if l.strip()]
                else:
                    parts = re.split(r'(?<=[.!?])[ \t]+(?=[A-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝĐ🔢💡📌])', cell.strip())
                    lines = [p.strip() for p in parts if p.strip()]
                if not lines:
                    lines = [cell] if isinstance(cell, str) else ['']
                box = '<br>'.join(esc(l) for l in lines)
                out.append(f'<div class="formula-box">{box}</div>')
                continue
            # render table; cells may be lists -> join with <br>
            def cell_html(c):
                if isinstance(c, list):
                    return '<br>'.join(esc(x) for x in c if x.strip())
                return esc(c)
            head = rows[0]
            body_rows = rows[1:]
            th = ''.join(f'<th>{cell_html(c)}</th>' for c in head)
            trs = []
            for r in body_rows:
                trs.append('<tr>' + ''.join(f'<td>{cell_html(c)}</td>' for c in r) + '</tr>')
            out.append(f'<div class="table-wrapper"><table><thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table></div>')
            continue
        # paragraph
        t = text.strip()
        if not t:
            flush_list()
            continue
        if style == 'Heading2':
            flush_list(); out.append(f'<h2>{esc(t)}</h2>'); continue
        if style == 'Heading3':
            flush_list(); out.append(f'<h3>{esc(t)}</h3>'); continue
        if style == 'ListParagraph':
            buf_list.append(t); continue
        # normal paragraph
        flush_list()
        if t.startswith('🔢') or t.startswith('💡') or t.startswith('📌'):
            label = t.lstrip('🔢💡📌 ').strip()
            cls = 'tip' if t[:1] in ('💡', '📌') else 'formula-label'
            out.append(f'<div class="{cls}"><strong>{esc(label)}</strong></div>')
        elif is_formula(t):
            out.append(f'<div class="formula">{esc(t)}</div>')
        else:
            out.append(f'<p>{esc(t)}</p>')
    flush_list()
    return '\n'.join(out)

HEAD = '''<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__ - Cẩm Nang Tennis 2026</title>
<meta name="description" content="__TITLE__ - Cẩm Nang Tennis Hiện Đại 2026">
<style>
:root{--p:#2563eb;--s:#7c3aed;--bg:#f8fafc;--c:#fff;--t:#1e293b;--m:#64748b;--b:#e2e8f0;}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:"Segoe UI",sans-serif;background:var(--bg);color:var(--t);line-height:1.8}
.container{max-width:900px;margin:0 auto;padding:0 20px}
header{background:linear-gradient(135deg,var(--p),var(--s));color:#fff;padding:40px 0;text-align:center}
header h1{font-size:1.8rem;font-weight:800;margin-bottom:10px}
nav{background:var(--c);border-bottom:2px solid var(--b);padding:15px 0;position:sticky;top:0;z-index:100;box-shadow:0 2px 8px rgba(0,0,0,.05)}
nav .container{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px}
nav a{font-weight:600;color:var(--p);text-decoration:none;padding:8px 16px;border-radius:6px;transition:all .2s;border:2px solid transparent}
nav a:hover{background:var(--p);color:#fff;border-color:var(--p)}
nav .title{font-weight:600;color:var(--t);font-size:.95rem;flex:1;text-align:center;min-width:200px}
main{padding:40px 0}
.content{background:var(--c);padding:40px;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,.05)}
.content h1{font-size:2rem;color:var(--p);margin-bottom:20px;padding-bottom:16px;border-bottom:3px solid var(--p);line-height:1.3}
.content h2{font-size:1.5rem;color:var(--p);margin:36px 0 16px;padding-top:20px;border-top:2px solid var(--b);line-height:1.4}
.content h3{font-size:1.25rem;color:var(--s);margin:24px 0 12px;line-height:1.4}
.content h4{font-size:1.1rem;color:var(--t);margin:20px 0 10px;font-weight:600}
.content p{margin:14px 0;color:var(--t);font-size:1rem;line-height:1.8}
.content ul{margin:14px 0 14px 28px}
.content li{margin:6px 0;color:var(--t);font-size:1rem;line-height:1.7}
.content strong{color:var(--p);font-weight:600}
.content em{color:var(--s);font-style:italic;font-weight:500}
.formula{background:#f8fafc;padding:16px;border-radius:8px;margin:20px 0;font-family:monospace;font-size:1.05rem;text-align:center;border-left:4px solid var(--p);overflow-x:auto;white-space:pre-wrap;word-break:break-word;line-height:1.5;text-align:left}
.formula-box{background:#eff6ff;padding:16px 20px;border-radius:8px;margin:20px 0;border-left:4px solid var(--p);line-height:1.7;color:var(--t);font-size:1rem}
.formula-label strong{color:var(--p)}
.tip{background:#fef3c7;padding:16px;border-radius:8px;margin:20px 0;border-left:4px solid #f59e0b;line-height:1.7}
.tip strong{color:#92400e}
.table-wrapper{overflow-x:auto;margin:20px 0}
table{width:100%;border-collapse:collapse;border:2px solid var(--b)}
th{background:var(--p);color:#fff;padding:12px;text-align:left;font-weight:600}
td{padding:10px 12px;border:1px solid var(--b)}
tr:nth-child(even){background:#f8fafc}
.footer-nav{display:flex;justify-content:space-between;align-items:center;margin-top:40px;padding-top:20px;border-top:2px solid var(--b);gap:10px;flex-wrap:wrap}
.footer-nav a{padding:10px 20px;background:var(--c);border:2px solid var(--p);border-radius:6px;text-decoration:none;color:var(--p);font-weight:600;transition:all .2s}
.footer-nav a:hover{background:var(--p);color:#fff}
@media(max-width:768px){.content{padding:20px}header h1{font-size:1.4rem}.content h1{font-size:1.5rem}.footer-nav{flex-direction:column}}
</style>
</head>'''

for n in order:
    if n < 1 or n > 12:
        continue
    els = chapters[n]
    # chapter title = first Heading1 (we stored separately? we appended only body; title is the heading itself not stored)
    # find title from original elements
    title_raw = None
    for kind, style, text in elements:
        if kind=='p' and style=='Heading1' and text.strip().upper().startswith('CHƯƠNG'):
            m = re.search(r'CHƯƠNG\s+(\d+)', text, re.IGNORECASE)
            if m and int(m.group(1))==n:
                title_raw = text; break
    disp = clean_title(title_raw)
    body_html = render_chapter(els)
    prev = 12 if n == 1 else n-1
    nxt = 1 if n == 12 else n+1
    page = HEAD.replace('__TITLE__', disp) + f'''
<body>
<header><div class=container>
<h1>{esc(disp)}</h1>
</div></header>
<nav><div class=container>
<a href="../">Trang Chủ</a>
<span class=title>Chương {n} / 12</span>
<a href="{prev}.html">Chương {prev}</a>
<a href="{nxt}.html">Chương {nxt} →</a>
</div></nav>
<main><div class=container>
<div class=content>
{body_html}
<div class=footer-nav>
<a href="../">Trang Chủ</a>
<a href="{prev}.html">← Chương {prev}</a>
<a href="{nxt}.html">Chương {nxt} →</a>
</div>
</div></main>
</body>
</html>'''
    with open(f'{OUT}/{n}.html', 'w', encoding='utf-8') as f:
        f.write(page)
    print(f"Wrote {n}.html  ({len(body_html)} body chars, {len(els)} source elems)")
print("ORDER:", order)
