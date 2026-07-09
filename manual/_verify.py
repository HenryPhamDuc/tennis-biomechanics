"""Verify the 12 generated HTML files against the source docx."""
import zipfile, re, html
from xml.etree import ElementTree as ET
from html.parser import HTMLParser

DOCX = r"C:\Users\Henry\Documents\MY VAULT\Documents\New Tennis Knowledge\CAM_NANG_TENNIS_2026_CongThucDonGian.docx"
MANUAL = r"C:\Users\Henry\GITHUB\tennis-biomechanics\manual"
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def wt(t): return f'{{{W}}}{t}'

# --- extract docx text per chapter ---
with zipfile.ZipFile(DOCX) as z:
    root = ET.fromstring(z.read('word/document.xml'))
body = root.find(wt('body'))
paras = []
for p in body.iter(wt('p')):
    txt = ''.join(t.text or '' for t in p.iter(wt('t')))
    paras.append(txt.strip())

# chapters 1-12 text blocks (Heading1 .. next Heading1)
def chapter_block(n):
    # real chapter Heading1 is uppercase "CHƯƠNG n:" (case-sensitive); TOC entries are "Chương n:" (lowercase)
    start = None
    for i,t in enumerate(paras):
        if re.match(rf'CHƯƠNG\s+{n}\b', t):
            start = i; break
    if start is None: return []
    end = len(paras)
    for j in range(start+1, len(paras)):
        if re.match(r'CHƯƠNG\s+\d+\b', paras[j]):
            end = j; break
    out=[]
    for idx,t in enumerate(paras[start:end]):
        # skip the Heading1 chapter title line itself (rendered title-cased)
        if re.match(rf'CHƯƠNG\s+{n}\b', t):
            continue
        # skip TOC dot-leader lines and appendix entries
        if '....' in t: continue
        if t.startswith('Phụ lục'): continue
        out.append(t)
    return out

def norm(s):
    s = re.sub(r'🔢|💡|📌', '', s)        # drop emoji markers
    s = re.sub(r'\s+', ' ', s).strip().lower()
    return s

# --- HTML well-formedness check ---
class V(HTMLParser):
    def __init__(self):
        super().__init__(); self.ok=True; self.errs=[]
    def error(self,m): self.ok=False; self.errs.append(m)

# --- mashed-sentence detector: a <p> containing two sentences that BOTH
#     start with uppercase and are joined with no space+punct (heuristic) ---
def mashed_check(s):
    bad=[]
    for m in re.finditer(r'<p>(.*?)</p>', s, re.S):
        body=m.group(1)
        # strip tags
        txt=re.sub(r'<[^>]+>','',body)
        # find pattern: lowercase letter followed directly by uppercase letter with no punctuation/space between
        if re.search(r'[a-záàảãạăắằẳẵặâấầẩẫậđéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ][A-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝĐ]', txt):
            bad.append(txt[:80])
    return bad

total_issues=0
for n in range(1,13):
    src = chapter_block(n)
    target = set()
    for t in src:
        if len(t) < 8:  # skip tiny labels/numbers
            continue
        target.add(t)
    htmlpath = f"{MANUAL}/{n}.html"
    s = open(htmlpath, encoding='utf-8').read()
    # well-formed
    v=V(); v.feed(s)
    wf = v.ok
    # coverage: each meaningful source para should be fully present
    plain = re.sub(r'<[^>]+>',' ', s)
    plain = html.unescape(plain)
    plain_norm = norm(plain)
    missing=[]
    for t in target:
        # normalize whitespace
        nt = norm(t)
        if nt and nt not in plain_norm:
            missing.append(t[:60])
    mashed = mashed_check(s)
    issues = (0 if wf else 1) + len(missing) + len(mashed)
    total_issues += issues
    status = "OK" if issues==0 else "FAIL"
    print(f"ch{n:>2}: wellformed={wf} missing={len(missing)} mashed={len(mashed)} -> {status}")
    for mm in missing[:3]: print("      MISSING:", mm)
    for mb in mashed[:3]: print("      MASHED :", mb)

print("\nTOTAL ISSUES:", total_issues)
print("RESULT:", "PASS" if total_issues==0 else "NEEDS FIX")
