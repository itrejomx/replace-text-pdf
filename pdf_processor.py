import fitz

_SYSTEM_FONTS = {
    "arial,bold,italic": "/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf",
    "arial,italic":      "/System/Library/Fonts/Supplemental/Arial Italic.ttf",
    "arial,bold":        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "arial":             "/System/Library/Fonts/Supplemental/Arial.ttf",
}

_BASE14_FALLBACK = {
    "bold+italic": "hebi",
    "italic":      "heit",
    "bold":        "hebo",
    "regular":     "helv",
}

_font_cache = {}


def _resolve_font(font_name: str):
    """Return a (fontname, fontfile, fontbuffer) triple for insert_text."""
    key = font_name.lower().strip()
    # Strip subset prefix like "DEVEXP+Arial,Bold" → "arial,bold"
    if "+" in key:
        key = key.split("+", 1)[1]

    if key in _font_cache:
        return _font_cache[key]

    # Try system font lookup first (exact match then prefix match)
    path = _SYSTEM_FONTS.get(key)
    if path is None:
        for k, p in _SYSTEM_FONTS.items():
            if key.startswith(k) or k.startswith(key):
                path = p
                break

    if path:
        result = (None, path, None)
    else:
        # Fallback to base-14 Helvetica variants
        variant = "regular"
        if "bold" in key and "italic" in key:
            variant = "bold+italic"
        elif "bold" in key:
            variant = "bold"
        elif "italic" in key or "oblique" in key:
            variant = "italic"
        result = (_BASE14_FALLBACK[variant], None, None)

    _font_cache[key] = result
    return result


def process_pdf(input_path, search_text, replace_text):
    doc = fitz.open(input_path)
    total_replaced = 0

    for page in doc:
        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
        redactions = []

        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    if search_text not in span["text"]:
                        continue

                    new_text = span["text"].replace(search_text, replace_text)
                    redactions.append({
                        "bbox": span["bbox"],
                        "origin": span["origin"],
                        "font_size": span["size"],
                        "font_name": span["font"],
                        "color": span["color"],
                        "new_text": new_text,
                    })
                    total_replaced += span["text"].count(search_text)

        if not redactions:
            continue

        for r in redactions:
            page.add_redact_annot(r["bbox"], fill=(1, 1, 1))
        page.apply_redactions()

        for r in redactions:
            bbox = r["bbox"]
            fontname, fontfile, _ = _resolve_font(r["font_name"])
            kwargs = {"fontsize": r["font_size"], "color": _normalize_color(r["color"])}
            if fontfile:
                kwargs["fontfile"] = fontfile
                kwargs["fontname"] = "F" + str(abs(hash(fontfile)) % 10000)
            else:
                kwargs["fontname"] = fontname
            page.insert_text(
                r["origin"],
                r["new_text"],
                **kwargs,
            )

    output_path = None
    if total_replaced > 0:
        base_name = input_path.rsplit(".pdf", 1)[0]
        output_path = f"{base_name}_replaced.pdf"
        doc.save(output_path)

    doc.close()
    return output_path, total_replaced


def _normalize_color(color):
    if isinstance(color, (list, tuple)):
        return tuple(color)
    r = ((color >> 16) & 0xFF) / 255
    g = ((color >> 8) & 0xFF) / 255
    b = (color & 0xFF) / 255
    return (r, g, b)
