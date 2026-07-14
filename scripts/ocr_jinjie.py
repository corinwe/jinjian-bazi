import sys, os, pytesseract, re
from pdf2image import convert_from_path

part = sys.argv[1]
pdf_name = sys.argv[2]

# 修正映射
replacements = [
    ("芝位", "爻位"), ("区位", "爻位"), ("功位", "爻位"), ("攻位", "爻位"),
    ("芝", "爻"), ("莹", "爻"),
    ("印组", "印星"),
    ("天王", "天干"), ("俯伤", "食伤"),
    ("玉十甲子", "五十甲子"),
    ("三六芝", "三六爻"),
]

def fix_text(text):
    for old, new in replacements:
        text = text.replace(old, new)
    return text

base = "/root/.hermes/profiles/jinjian-zhenren/cache/documents"
out_base = os.path.join(base, "ocr_jinjie")
os.makedirs(out_base, exist_ok=True)

pdf_path = os.path.join(base, pdf_name)
images = convert_from_path(pdf_path, dpi=300)
lines = []
for i, img in enumerate(images):
    text = pytesseract.image_to_string(img, lang='chi_sim')
    lines.append(f"\n===== 第{i+1}页 =====\n{text}")

raw = "".join(lines)
fixed = fix_text(raw)

out_path = os.path.join(out_base, f"易道进阶知识_第{part}部分_全文.md")
with open(out_path, "w") as f:
    f.write(fixed)

print(f"DONE:{part}:{len(images)}页:{len(fixed)}字")
