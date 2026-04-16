import fitz


def map_font(font_name):
    font_name_lower = font_name.lower()
    if "bold" in font_name_lower:
        return "hebo"
    elif "italic" in font_name_lower or "oblique" in font_name_lower:
        return "hebo"
    else:
        return "helv"


def process_pdf(input_path, search_text, replace_text):
    """Process a single PDF file, replacing all occurrences of search_text with replace_text.

    Args:
        input_path: Path to the input PDF file.
        search_text: Text to search for.
        replace_text: Text to replace with.

    Returns:
        Tuple of (output_path_or_None, replacement_count).
        output_path is None if no replacements were made.
    """
    doc = fitz.open(input_path)
    total_replaced = 0

    for page in doc:
        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    if search_text in span["text"]:
                        bbox = span["bbox"]
                        font_size = span["size"]
                        font_name = span["font"]
                        color = span["color"]

                        page.add_redact_annot(bbox, fill=(1, 1, 1))
                        page.apply_redactions()

                        page.insert_text(
                            (bbox[0], bbox[1] + font_size * 0.75),
                            replace_text,
                            fontname=map_font(font_name),
                            fontsize=font_size,
                            color=color,
                        )
                        total_replaced += 1

    output_path = None
    if total_replaced > 0:
        base_name = input_path.rsplit(".pdf", 1)[0]
        output_path = f"{base_name}_replaced.pdf"
        doc.save(output_path)

    doc.close()
    return output_path, total_replaced
