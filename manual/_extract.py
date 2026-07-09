import zipfile, re
from xml.etree import ElementTree as ET
from collections import Counter

docx = r"C:\Users\Henry\Documents\MY VAULT\Documents\New Tennis Knowledge\CAM_NANG_TENNIS_2026_CongThucDonGian.docx"

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
with zipfile.ZipFile(docx) as z:
    xml = z.read('word/document.xml').decode('utf-8')

root = ET.fromstring(xml)
body = root.find(f'{{{W}}}body')

paras = []
for p in body.iter(f'{{{W}}}p'):
    texts = []
    for t in p.iter(f'{{{W}}}t'):
        texts.append(t.text or '')
    txt = ''.join(texts)
    pPr = p.find(f'{{{W}}}pPr')
    style = ''
    if pPr is not None:
        pStyle = pPr.find(f'{{{W}}}pStyle')
        if pStyle is not None:
            style = pStyle.get(f'{{{W}}}val')
    paras.append((style, txt))

print("TOTAL PARAS:", len(paras))
print("=== STYLES USED ===")
print(Counter(s for s, _ in paras))
print("=== ALL PARAS (style | text) ===")
for i, (s, t) in enumerate(paras):
    print(f"[{i}] {s!r} | {t!r}")
