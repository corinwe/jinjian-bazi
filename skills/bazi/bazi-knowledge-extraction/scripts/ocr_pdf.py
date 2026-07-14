#!/usr/bin/env python3
"""
金鉴真人·OCR PDF提取脚本
用途：将扫描件PDF（图片PDF）通过tesseract OCR转为完整文本
用法：python3 ocr_pdf.py <编号> <PDF文件名>
示例：python3 ocr_pdf.py 二 doc_xxx_易道知识应用第二部分.pdf

输出：ocr_parts/易道知识应用_第<编号>部分_全文.txt
      同时每页的PNG图片保存到 ocr_parts/part_<编号>/page_XX.png
"""
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
    # 保存PNG以备后续核查
    png_path = os.path.join(out_base, f"page_{i+1:02d}.png")
    img.save(png_path, "PNG")
    # OCR
    text = pytesseract.image_to_string(img, lang='chi_sim')
    lines.append(f"\n===== 第{i+1}页 =====\n{text}")

full = "".join(lines)
out_path = os.path.join(base, "ocr_parts", f"易道知识应用_第{part}部分_全文.txt")
with open(out_path, "w") as f:
    f.write(full)
print(f"DONE:{part}:{len(full)}字")
