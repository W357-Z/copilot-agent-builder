# GAWB brand tokens

Colour and typeface constants used by the package's renderers
(`lib_png.py`) and DOCX builders (`lib_docx.py`). Source: GAWB Design and
Brand Guidelines (colours) — verify against the currently controlled brand
issue before producing client-facing material.

## Palette

| Token | HEX | RGB | Role | Defined in |
| ----- | --- | --- | ---- | ---------- |
| `GAWB_BLUE` | `#007CBB` | 0, 124, 187 | Primary brand (Pantone 7461 C); ICAM chart people column, table headers, H1 | `lib_png.py`, `BRAND_BLUE` |
| `GAWB_GREEN` | `#00A98F` | 0, 169, 143 | Secondary brand (Pantone 3268 C); environment column, H2 accent | `lib_png.py`, `BRAND_TEAL` |
| `GAWB_DEEPBLUE` | `#004E74` | 0, 78, 116 | Deep brand blue; people column chips, strong accents | `lib_png.py` |
| `GAWB_LIGHTBLUE` | `#00B3F0` | 0, 179, 240 | Bright accent; equipment column | `lib_png.py` |
| `GAWB_LIME` | `#D9E25A` | 217, 226, 90 | Lime accent; procedures column | `lib_png.py` |
| `GAWB_DEEPGREEN` | `#003A32` | 0, 58, 50 | Deep green; dark accents | `lib_png.py` |
| `GAWB_ORANGE` | `#FBAE42` | 251, 174, 66 | Orange accent; organisation column | `lib_png.py` |
| `INK` | `#1A2B33` | 26, 43, 51 | Neutral dark text on light panels | `lib_png.py` |
| `GREY` | `#5A6B72` | 90, 107, 114 | Secondary text, evidence refs | `lib_png.py` |
| `PANEL` | `#F0F7FA` | 240, 247, 250 | Light panel / box fill | `lib_png.py` |
| `WHITE` | `#FFFFFF` | 255, 255, 255 | Text on saturated fills | `lib_png.py` |
| `BRAND_LIGHT` | `#E8F3FA` | 232, 243, 250 | Light blue band (alternating table rows, key cells) | `lib_docx.py` |
| `BRAND_GREY` | `#595959` | 89, 89, 89 | Captions and footers in DOCX | `lib_docx.py` |

Chart column mapping (ICAM/PEEPO): People `GAWB_DEEPBLUE`, Environment
`GAWB_GREEN`, Equipment `GAWB_LIGHTBLUE`, Procedures `GAWB_LIME`,
Organisation `GAWB_ORANGE`. The standalone-artefact banner uses `GAWB_BLUE`
with `GAWB_GREEN` accents.

## Typefaces

- **Ubuntu** — corporate primary typeface (body on GAWB collateral). Not a
  standard Windows font; the brand guidelines direct users to the secondary
  typeface where Ubuntu is unavailable.
- **Verdana** — secondary typeface; **the package standard**. All DOCX
  outputs (`lib_docx.py`, `BRAND_FONT`) and embedded chart text
  (`lib_png.py`) use Verdana so documents render identically on machines
  without Ubuntu installed. Type never below 6pt per the guidelines; body
  text in the artefacts is 10pt+.

Do not introduce other fonts into package outputs. If a template author
later mandates Ubuntu for headings, update `BRAND_FONT` and the chart font
table together and re-render every sample.
