import zipfile
from xml.etree import ElementTree as ET
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def wt(t):return f'{{{W}}}{t}'
with zipfile.ZipFile(r"C:\Users\Henry\Documents\MY VAULT\Documents\New Tennis Knowledge\CAM_NANG_TENNIS_2026_CongThucDonGian.docx") as z:
    root=ET.fromstring(z.read('word/document.xml'))
body=root.find(wt('body'))
for i,tbl in enumerate(body.findall(wt('tbl'))):
    rows=[r.findall(wt('tc')) for r in tbl.findall(wt('tr'))]
    shape=(len(rows),max((len(r) for r in rows),default=0))
    # first cell text
    first=''
    if rows and rows[0]:
        first=''.join(t.text or '' for t in rows[0][0].iter(wt('t')))
    print(i, shape, repr(first[:50]))
