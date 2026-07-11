import re, pathlib
path = pathlib.Path("C:/Users/Henry/GITHUB/tennis-biomechanics/manual/1.html")
content = path.read_text(encoding='utf-8')
# Find the section between <h2>1.2. and next <h2>
start_tag = '<h2>1.2.'
end_tag = '<h2>'  # will match following headings
start = content.find(start_tag)
if start == -1:
    print('Section start not found')
    exit()
# Find next <h2> after start
next_found = content.find(end_tag, start + len(start_tag))
if next_found == -1:
    next_found = len(content)
section = content[start:next_found]
# Replace in section any end-of-sentence punctuation followed by space and capital letter
# but avoid splitting inside tags like <p>, <a>, etc. We'll split only inside plain text blocks.
# Find all <p>...</p> forms within section
new_section = section
p_regex = re.compile(r'(<p>)(.*?)</p>', re.DOTALL)

def split_paragraph(match):
    opening, body = match.group(1), match.group(2)
    # Split body by punctuation that ends a sentence: . ! ? followed by space and capital letter
    parts = re.split(r'(?<=[.!?])\s+(?=[A-ZÁÀÃÂĂ…])', body)
    # Filter empty
    parts = [p for p in parts if p.strip()]
    return opening + ('</p><p>'.join(parts)) + '</p>'
new_section = p_regex.sub(split_paragraph, new_section)
# Replace back in content
new_content = content[:start] + new_section + content[next_found:]
# Write back
path.write_text(new_content, encoding='utf-8')
print('Split complete')
