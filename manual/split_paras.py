import sys, re

def split_paragraph(html_path):
    with open(html_path, encoding='utf-8') as f:
        content = f.read()
    # Find the first <p>...</p> block (non-greedy)
    m = re.search(r'(<p>.*?)</p>', content, re.DOTALL)
    if not m:
        return  # nothing to do
    block = m.group(1)
    # Decide a split point: try after ~900 chars, but move back to last punctuation
    split_point = 900
    if len(block) > split_point:
        # Look back up to 100 chars for '.', '!' or '?'
        window = block[split_point-100:split_point+1]
        # Find right‑most punctuation in that window
        punct_match = re.search(r'[.!?]', window)
        if punct_match:
            # adjust position relative to start of block
            split_point = split_point - 100 + punct_match.start() + 1
        # Clamp
        split_point = max(split_point, 1)
        split_point = min(split_point, len(block))
        # Insert closing and opening tags
        block = block[:split_point] + '</p><p>' + block[split_point:]
        # Replace the original block with the modified one
        content = content.replace(m.group(0), block, 1)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python split_paras.py <path-to-html>")
        sys.exit(1)
    split_paragraph(sys.argv[1])
