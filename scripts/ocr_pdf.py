import os, sys, pytesseract
from pdf2image import convert_from_path

part = sys.argv[1]
pdf_name = sys.argv[2]

base = "/root/.hermes/profiles/jinjian-zhenren/cache/documents"
out_base = os.path.join(base, "ocr_parts", f"part_{part}")
os.makedirs(out_base, exist_ok=True)
pdf_path = os.path.join(base, pdf_name)

images = convert_from_path(pdf_path, dpi=300)
lines = []
for i, img in enumerate(images):
    text = pytesseract.image_to_string(img, lang='chi_sim')
    lines.append(f"\n===== 第{i+1}页 =====\n{text}")

full = "".join(lines)
out_path = os.path.join(base, "ocr_parts", f"易道知识应用_第{part}部分_全文.txt")
with open(out_path, "w") as f:
    f.write(full)
print(f"DONE:{part}:{len(full)}字")
