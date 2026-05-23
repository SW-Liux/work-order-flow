"""
文档解析脚本：将 Word(.docx) 和 PDF 文件转换为高保真 Markdown。
图片按文档流嵌入正确位置，保留加粗、目录、编号列表、表格内格式。

依赖安装：
    pip install python-docx pdfplumber Pillow

使用方式：
    python parse_doc.py input.docx -o output_dir/
    python parse_doc.py input.pdf -o output_dir/

输出：
    output_dir/content.md   — 文档内容（Markdown格式）
    output_dir/images/      — 提取的图片（仅 Word）
"""

import argparse
import os
import sys
import re
from pathlib import Path


WPML_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
DRAW_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
WP_NS = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"

NAMESPACES = {
    "w": WPML_NS,
    "a": DRAW_NS,
    "r": REL_NS,
    "wp": WP_NS,
}


def _extract_image_from_run(run_element, doc_part, images_dir, img_counter):
    """从 run XML 元素中提取内联图片"""
    blips = run_element.findall(f".//{{{DRAW_NS}}}blip")
    results = []
    for blip in blips:
        r_embed = blip.get(f"{{{REL_NS}}}embed")
        if not r_embed:
            continue
        try:
            rel = doc_part.rels[r_embed]
            img_data = rel.target_part.blob
            ext = rel.target_part.content_type.split("/")[-1]
            if ext == "jpeg":
                ext = "jpg"
            if ext in ("x-emf", "x-wmf", "emf", "wmf"):
                ext = "png"
            img_counter += 1
            img_filename = f"image_{img_counter:03d}.{ext}"
            with open(os.path.join(images_dir, img_filename), "wb") as f:
                f.write(img_data)
            results.append(f"![图片{img_counter}](images/{img_filename})")
        except (KeyError, AttributeError):
            pass
    return results, img_counter


def _run_to_md(run):
    """将 run 转为 markdown 文本，保留加粗和斜体"""
    text = run.text or ""
    if not text.strip():
        return text
    is_bold = run.bold
    is_italic = run.italic
    if is_bold and is_italic:
        return f"***{text}***"
    elif is_bold:
        return f"**{text}**"
    elif is_italic:
        return f"*{text}*"
    return text


def _is_toc_paragraph(para):
    """检查段落是否是目录项（TOC）"""
    style_name = para.style.name if para.style else ""
    if "toc" in style_name.lower():
        return True
    # 检查是否有 HYPERLINK 字段指向 _Toc
    xml_str = para._p.xml
    if "_Toc" in xml_str:
        return True
    return False


def _para_to_md(para, doc_part, images_dir, img_counter, list_counters):
    """将段落转为 Markdown，保留格式"""
    style_name = para.style.name.lower() if para.style else ""

    # 构建 run 内容（含图片和格式）
    md_parts = []
    has_image = False

    for run in para.runs:
        imgs, img_counter = _extract_image_from_run(run._r, doc_part, images_dir, img_counter)
        if imgs:
            has_image = True
            md_parts.extend(imgs)
        run_text = _run_to_md(run)
        if run_text:
            md_parts.append(run_text)

    text = "".join(md_parts).strip()
    if not text:
        return "", img_counter

    # 目录项
    if _is_toc_paragraph(para):
        return text, img_counter

    # 标题
    if "heading 1" in style_name:
        clean = re.sub(r"\*{2,}(.*?)\*{2,}", r"\1", text)
        return f"## **{clean}**", img_counter
    elif "heading 2" in style_name:
        clean = re.sub(r"\*{2,}(.*?)\*{2,}", r"\1", text)
        return f"### **{clean}**", img_counter
    elif "heading 3" in style_name:
        clean = re.sub(r"\*{2,}(.*?)\*{2,}", r"\1", text)
        return f"#### **{clean}**", img_counter
    elif "heading" in style_name:
        clean = re.sub(r"\*{2,}(.*?)\*{2,}", r"\1", text)
        return f"##### **{clean}**", img_counter

    # 编号列表
    numPr = para._p.find(f".//{{{WPML_NS}}}numPr")
    if numPr is not None:
        ilvl_el = numPr.find(f"{{{WPML_NS}}}ilvl")
        level = int(ilvl_el.get(f"{{{WPML_NS}}}val", "0")) if ilvl_el is not None else 0
        numId_el = numPr.find(f"{{{WPML_NS}}}numId")
        numId = numId_el.get(f"{{{WPML_NS}}}val", "0") if numId_el is not None else "0"

        key = f"{numId}_{level}"
        if key not in list_counters:
            list_counters[key] = 0
        list_counters[key] += 1

        indent = "    " * level
        return f"{indent}{list_counters[key]}.  {text}", img_counter

    # 无序列表
    if "list" in style_name:
        text_clean = text.lstrip("•-·").strip()
        return f"- {text_clean}", img_counter

    return text, img_counter


def _cell_to_md(cell, doc_part=None, images_dir=None, img_counter=0):
    """将表格单元格转为 markdown，保留加粗、换行和图片"""
    parts = []
    for para in cell.paragraphs:
        para_parts = []
        for run in para.runs:
            para_parts.append(_run_to_md(run))
        if doc_part and images_dir:
            for run_el in para._element.findall(f".//{{{WPML_NS}}}r"):
                img_refs, img_counter = _extract_image_from_run(
                    run_el, doc_part, images_dir, img_counter
                )
                para_parts.extend(img_refs)
        line = "".join(para_parts).strip()
        if line:
            parts.append(line)

    text = "<br><br>".join(parts) if len(parts) > 1 else (parts[0] if parts else "")
    return text, img_counter


def _table_to_md(table, doc_part=None, images_dir=None, img_counter=0):
    """将表格转为 Markdown，保留单元格内加粗、换行和图片"""
    rows_md = []
    for row_idx, row in enumerate(table.rows):
        cells_md = []
        for cell in row.cells:
            cell_text, img_counter = _cell_to_md(
                cell, doc_part, images_dir, img_counter
            )
            cells_md.append(cell_text)
        rows_md.append("| " + " | ".join(cells_md) + " |")
        if row_idx == 0:
            rows_md.append("| " + " | ".join(["---"] * len(cells_md)) + " |")
    return "\n".join(rows_md), img_counter


def parse_docx(file_path: str, output_dir: str) -> str:
    """按文档流顺序解析 Word 文档，高保真转换"""
    try:
        from docx import Document
        from docx.oxml.ns import qn
    except ImportError:
        print("Error: python-docx not installed. Run: pip install python-docx")
        sys.exit(1)

    doc = Document(file_path)
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    md_lines = []
    img_counter = 0
    list_counters = {}
    in_toc = False

    table_elements = {}
    for table in doc.tables:
        table_elements[id(table._tbl)] = table

    body = doc.element.body
    for child in body:
        tag = child.tag

        if tag == qn("w:p"):
            from docx.text.paragraph import Paragraph
            para = Paragraph(child, doc)

            # 检测目录区域
            text_check = para.text.strip()
            if text_check == "目录":
                in_toc = True
                md_lines.append("")
                md_lines.append("**目录**")
                md_lines.append("")
                continue

            if in_toc:
                if _is_toc_paragraph(para):
                    line, img_counter = _para_to_md(para, doc.part, images_dir, img_counter, list_counters)
                    if line:
                        md_lines.append(line)
                    continue
                else:
                    if text_check:
                        in_toc = False

            line, img_counter = _para_to_md(para, doc.part, images_dir, img_counter, list_counters)
            md_lines.append(line)

        elif tag == qn("w:tbl"):
            tbl_obj = table_elements.get(id(child))
            if tbl_obj:
                md_lines.append("")
                tbl_md, img_counter = _table_to_md(
                    tbl_obj, doc.part, images_dir, img_counter
                )
                md_lines.append(tbl_md)
                md_lines.append("")

        elif tag == qn("w:sectPr"):
            pass

    content = "\n".join(md_lines)
    content = re.sub(r"\n{4,}", "\n\n\n", content)
    return content


def parse_pdf(file_path: str, output_dir: str) -> str:
    """解析 PDF 文档，清理噪声，保留结构"""
    try:
        import pdfplumber
    except ImportError:
        print("Error: pdfplumber not installed. Run: pip install pdfplumber")
        sys.exit(1)

    md_lines = []
    # 用于去重的噪声模式（钉钉 PDF 水印）
    noise_patterns = [
        re.compile(r"(新\s*){2,}"),
        re.compile(r"(刘\s*){2,}"),
    ]

    with pdfplumber.open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            md_lines.append(f"\n---\n\n**第 {page_num} 页**\n")

            text = page.extract_text()
            if text:
                cleaned = text
                for pattern in noise_patterns:
                    cleaned = pattern.sub("", cleaned)
                # 去除页脚
                cleaned = re.sub(r"第 \d+ 页\s*$", "", cleaned, flags=re.MULTILINE)
                cleaned = cleaned.strip()
                if cleaned:
                    md_lines.append(cleaned)

            tables = page.extract_tables()
            for t_idx, table in enumerate(tables):
                if not table:
                    continue
                md_lines.append("")
                for row_idx, row in enumerate(table):
                    cells = []
                    for cell in row:
                        c = str(cell).strip().replace("\n", "<br>") if cell else ""
                        # 清理水印
                        for pattern in noise_patterns:
                            c = pattern.sub("", c)
                        cells.append(c)
                    md_lines.append("| " + " | ".join(cells) + " |")
                    if row_idx == 0:
                        md_lines.append("| " + " | ".join(["---"] * len(cells)) + " |")
                md_lines.append("")

    return "\n".join(md_lines)


def main():
    parser = argparse.ArgumentParser(description="将 Word/PDF 文档转换为 Markdown")
    parser.add_argument("input_file", help="输入文件路径 (.docx 或 .pdf)")
    parser.add_argument("-o", "--output", default=".", help="输出目录 (默认: 当前目录)")
    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)

    output_dir = args.output
    os.makedirs(output_dir, exist_ok=True)

    ext = input_path.suffix.lower()
    if ext == ".docx":
        print(f"Parsing Word document: {input_path.name}")
        content = parse_docx(str(input_path), output_dir)
    elif ext == ".pdf":
        print(f"Parsing PDF document: {input_path.name}")
        content = parse_pdf(str(input_path), output_dir)
    else:
        print(f"Error: Unsupported file type '{ext}'. Supported: .docx, .pdf")
        sys.exit(1)

    output_file = os.path.join(output_dir, "content.md")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Done! Output: {output_file}")
    if ext == ".docx":
        images_dir = os.path.join(output_dir, "images")
        if os.path.exists(images_dir):
            img_count = len([f for f in os.listdir(images_dir) if not f.startswith(".")])
            if img_count > 0:
                print(f"Extracted {img_count} images to {images_dir}/")


if __name__ == "__main__":
    main()
