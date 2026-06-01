# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

```bash
pip install -r requirements.txt
python app.py
```

The server starts at `http://localhost:5000`.

## Architecture

This is a two-file Flask app:

- **`app.py`** — HTTP layer. Accepts a POST to `/convert` with a multipart form containing `file` (xlsx) and `factory_name` (string). Calls `processor.convert_excel()` and streams the result back as a file download. Also serves the Zanex admin template assets from `HTML/zanex/assets/` under the `/zanex/` URL prefix.

- **`processor.py`** — Pure transformation logic with no Flask dependency. `convert_excel(input_bytes, factory_name) -> bytes` is the sole public entry point. Internally it:
  1. **Parses** the input workbook (`_parse_input` → `_parse_block`): detects PO blocks by scanning for rows where col A = "COLOR" and col B contains "SIZE". Each block yields a `po_name`, `style_groups` (columns), and `colors` (rows with per-size quantities).
  2. **Writes Section 1** (detailed): one `_write_color_block` per color per group, followed by a color-total row, group subtotal, optional PO total, and a grand TOTAL row.
  3. **Writes Section 2** (summary): a compact view with one row per color, merged metadata cells, and a grand total.

- **`templates/index.html`** — Single-page UI using the Zanex Bootstrap admin theme. Drag-and-drop upload zone, factory name input, and JS fetch to `/convert` that triggers a file download on success.

## Key data shapes

```python
# Output of _parse_input
style_num: str
po_blocks: list[{
    'po_name': str,           # e.g. "123456-USA"
    'style_groups': [{'name': str, 'sizes': [(col_idx, size_label)]}],
    'colors': [{'color': str, 'group_qtys': {group_name: {size_label: int}}}]
}]
```

## Styling conventions in processor.py

All Excel styling uses named color constants (`C_HEADER_GREEN`, `C_DATA_PEACH`, etc.) defined at the top of the file. Helper functions `_fill`, `_font`, `_align`, `_thin_border`, `_apply`, and `_style_row` encapsulate openpyxl style objects — use these instead of constructing styles inline.
