import pathlib, re

manual_dir = pathlib.Path(r"C:/Users/Henry/GITHUB/tennis-biomechanics/manual")
for i in range(2, 13):
    file_path = manual_dir / f"{i}.html"
    if not file_path.exists():
        print(f"{file_path} not found")
        continue
    content = file_path.read_text(encoding='utf-8')
    # split all <p> blocks
    def split_para(match):
        opening = match.group(1)
        body = match.group(2)
        # split by sentence boundaries
        parts = re.split(r'(?<=[.!?])\s+(?=[A-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝĐ])', body)
        parts = [p for p in parts if p.strip()]
        return opening + ('</p><p>'.join(parts)) + '</p>'
    new_content = re.sub(r'(<p>)(.*?)</p>', split_para, content, flags=re.DOTALL)
    file_path.write_text(new_content, encoding='utf-8')
    print(f"Processed {file_path}")
print("Done.")
