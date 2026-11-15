"""lib_docx.py - stdlib-only DOCX toolkit for the GAWB ICAM Investigation skill.

Fills Word content controls (SDT), dropdowns, date pickers and checkbox glyphs
in the controlled WHS-TMP-0207 template; clones repeating table rows; embeds
PNG charts; and creates new branded DOCX artefacts from scratch. No network,
no packages; Python 3.8+ standard library only.

Exit-code discipline lives in the calling scripts; this module raises
DocxFillError for caller-mapped failures.
"""
import os
import re
import shutil
import struct
import zipfile
import base64
import zlib
from xml.etree import ElementTree as ET

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
WNS = "{%s}" % W

NSMAP = {
    "wpc": "http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "o": "urn:schemas-microsoft-com:office:office",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "v": "urn:schemas-microsoft-com:vml",
    "wp14": "http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "w10": "urn:schemas-microsoft-com:office:word",
    "w": W,
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
    "wpg": "http://schemas.microsoft.com/office/word/2010/wordprocessingGroup",
    "wpi": "http://schemas.microsoft.com/office/word/2010/wordprocessingInk",
    "wne": "http://schemas.microsoft.com/office/word/2006/wordml",
    "wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
    "w16se": "http://schemas.microsoft.com/office/word/2015/wordml/symex",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
}
for _p, _u in NSMAP.items():
    ET.register_namespace(_p, _u)

PLACEHOLDERS = {
    "click or tap here to enter text",
    "choose an item.",
    "[title]",
    "click or tap to enter a date.",
    "date",
    "description",
    "type learnings here",
    "[type recommendation 1 here]",
    "person responsible",
    "reference#",
}

CHECKED = "\u2612"   # ballot box with X
UNCHECKED = "\u2610"  # ballot box


class DocxFillError(Exception):
    pass


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def is_placeholder(text):
    t = (text or "").strip().lower()
    return t in PLACEHOLDERS


def load_parts(path):
    """Read a docx/dotx into {name: bytes} preserving order."""
    with zipfile.ZipFile(path) as z:
        return {n: z.read(n) for n in z.namelist()}


def save_parts(parts, path):
    d = os.path.dirname(os.path.abspath(path))
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for n, data in parts.items():
            z.writestr(n, data)


def parse_xml(data):
    return ET.fromstring(data)


def serialise(root):
    return ET.tostring(root, xml_declaration=True, encoding="UTF-8")


def serialise_preserving_root(doc, original_bytes):
    """Serialise an edited document.xml, merging namespace declarations.

    ElementTree hoists every namespace declaration it emits onto its own
    root tag, and drops declarations referenced only by mc:Ignorable. The
    template root instead declares the Word prefix set, with some namespaces
    (a, pic, a14) declared inline deeper in the tree. The safe merge: keep
    the original root tag, add any declaration ET introduced; on prefix
    conflicts (same prefix, different URI) rename the ET prefix throughout.
    """
    import re as _re
    out = ET.tostring(doc, xml_declaration=True, encoding="UTF-8")
    m_et = _re.search(rb"<w:document\b[^>]*>", out)
    m_orig = _re.search(rb"<w:document\b[^>]*>", original_bytes)
    if not (m_et and m_orig):
        return out
    et_tag, orig_tag = m_et.group(0), m_orig.group(0)
    et_decls = _re.findall(rb'xmlns:([\w.-]+)="([^"]*)"', et_tag)
    orig_decls = dict(_re.findall(rb'xmlns:([\w.-]+)="([^"]*)"', orig_tag))
    extra = []
    renames = {}
    for prefix, uri in et_decls:
        old = orig_decls.get(prefix)
        if old == uri:
            continue
        if old is None:
            extra.append(b' xmlns:%s="%s"' % (prefix, uri))
        else:
            newp = prefix + b"x"
            renames.append((prefix, uri, newp))
            extra.append(b' xmlns:%s="%s"' % (newp, uri))
    merged = orig_tag[:-1] + b"".join(extra) + b">"
    if renames:
        for oldp, uri, newp in renames:
            # only rewrite prefixes that bind to this uri in ET output
            out = out.replace(b"<%s:" % oldp, b"<%s:" % newp)
            out = out.replace(b"</%s:" % oldp, b"</%s:" % newp)
            out = out.replace(b" %s:" % oldp, b" %s:" % newp)
        # rebuild merged tag accounting for renames inside it (none expected)
    out = out.replace(et_tag, merged, 1)
    d = _re.search(rb"<\?xml[^>]*\?>", original_bytes)
    if d:
        out = _re.sub(rb"^\s*<\?xml[^>]*\?>", lambda _: d.group(0), out, count=1)
    return out


# ------------------------------------------------------------------ SDT ----
def iter_sdts(root):
    return list(root.iter(WNS + "sdt"))


def sdt_kind(sdt):
    pr = sdt.find(WNS + "sdtPr")
    if pr is None:
        return "text"
    if pr.find(WNS + "docPartObj") is not None:
        return "docpart"
    if pr.find(WNS + "dropDownList") is not None or pr.find(WNS + "comboBox") is not None:
        return "list"
    if pr.find(WNS + "date") is not None:
        return "date"
    if pr.find(WNS + "checkbox") is not None:
        return "checkbox"
    return "text"


def sdt_text(sdt):
    cont = sdt.find(WNS + "sdtContent")
    if cont is None:
        return ""
    return "".join(t.text or "" for t in cont.iter(WNS + "t")).strip()


def _first_run_rpr(par):
    for r in par.iter(WNS + "r"):
        rpr = r.find(WNS + "rPr")
        if rpr is not None:
            return rpr
    return None


def _clear_placeholder_state(sdt):
    """Drop Word's placeholder markers so filled content is real content.

    <w:showingPlcHdr/> in sdtPr makes Word treat the visible text as the
    placeholder (it renders grey and disappears on first edit). Runs styled
    with the PlaceholderText character style render grey as well.
    """
    spr = sdt.find(WNS + "sdtPr")
    if spr is not None:
        for ph in spr.findall(WNS + "showingPlcHdr"):
            spr.remove(ph)


_PLACEHOLDER_SNIPPETS = ("click or tap here", "click or tap to enter",
                         "choose an item", "type ")
_PLACEHOLDER_EXACT = ("date", "description", "reference#", "person responsible")


def strip_resolved_placeholders(doc):
    """Remove <w:showingPlcHdr/> from SDTs whose content is now real text.

    SDTs filled indirectly (cell-wrapped content filled through the wrapping
    cell) keep the placeholder flag even though their text was replaced; Word
    would then render them grey and wipe them on first edit. Only flags on
    SDTs whose visible text still looks like placeholder text are kept.
    Returns the number of flags removed.
    """
    n = 0
    for sdt in doc.iter(WNS + "sdt"):
        spr = sdt.find(WNS + "sdtPr")
        if spr is None or spr.find(WNS + "showingPlcHdr") is None:
            continue
        text = "".join(t.text or "" for t in sdt.iter(WNS + "t")).strip()
        if not text:
            continue
        low = text.lower()
        if any(s in low for s in _PLACEHOLDER_SNIPPETS):
            continue
        if low in _PLACEHOLDER_EXACT or low.startswith("["):
            continue
        for ph in spr.findall(WNS + "showingPlcHdr"):
            spr.remove(ph)
        n += 1
    return n


def fill_sdt(sdt, value, multi=False):
    """Replace the visible content of an SDT with `value`.

    multi=True: value is a list of lines -> one paragraph per line, using the
    first content paragraph as the style template. multi=False: single line in
    the first content paragraph; remaining content paragraphs are removed.

    Handles both plain content (sdtContent > p...) and cell-wrapped content
    (sdtContent > tc > p...), preserving the wrapper structure.
    """
    cont = sdt.find(WNS + "sdtContent")
    if cont is None:
        raise DocxFillError("content control without sdtContent")
    # locate the fill block: direct p, else first direct tc (descend into it)
    block = None
    for c in list(cont):
        if c.tag == WNS + "p":
            block = c
            break
        if c.tag == WNS + "tc":
            block = c
            break
    if block is None:
        p = ET.SubElement(cont, WNS + "p")
        block = p
    if block.tag == WNS + "tc":
        host = block
        paras = block.findall(WNS + "p")
        if not paras:
            paras = [ET.SubElement(host, WNS + "p")]
    else:
        host = cont
        paras = [block]

    template = paras[0]
    _clear_placeholder_state(sdt)
    rpr = _first_run_rpr(template)
    if rpr is not None:
        # drop placeholder grey so filled text renders in the body style
        for col in rpr.findall(WNS + "color"):
            rpr.remove(col)
        for st in list(rpr.findall(WNS + "rStyle")):
            if st.get(WNS + "val", "") == "PlaceholderText":
                rpr.remove(st)

    lines = list(value) if multi else [str(value)]
    # remove existing paragraphs beyond the first
    for extra in list(host):
        if extra.tag == WNS + "p" and extra is not template:
            host.remove(extra)
    # clear the template paragraph's runs and bookmarks but keep pPr
    for child in list(template):
        if child.tag != WNS + "pPr":
            template.remove(child)
    for i, line in enumerate(lines):
        target = template if i == 0 else _clone_par(template)
        if i > 0:
            host.append(target)
        run = ET.SubElement(target, WNS + "r")
        if rpr is not None:
            run.append(_deepcopy(rpr))
        t = ET.SubElement(run, WNS + "t")
        t.text = str(line)
        if str(line) != str(line).strip():
            t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")


def _deepcopy(el):
    return ET.fromstring(ET.tostring(el))


def _clone_par(par):
    c = _deepcopy(par)
    for child in list(c):
        if child.tag != WNS + "pPr":
            c.remove(child)
    return c


def set_checkbox(sdt, checked):
    _clear_placeholder_state(sdt)
    cont = sdt.find(WNS + "sdtContent")
    glyph = CHECKED if checked else UNCHECKED
    for t in cont.iter(WNS + "t"):
        if (t.text or "").strip() in (CHECKED, UNCHECKED):
            t.text = glyph
            return True
    return False


def fill_plain_paragraph(par, value):
    """Replace all runs in a plain (non-SDT) paragraph with one run."""
    rpr = _first_run_rpr(par)
    if rpr is not None:
        # drop placeholder grey so filled text renders in the body style
        for col in rpr.findall(WNS + "color"):
            rpr.remove(col)
        for st in list(rpr.findall(WNS + "rStyle")):
            if st.get(WNS + "val", "") == "PlaceholderText":
                rpr.remove(st)
    for child in list(par):
        if child.tag != WNS + "pPr":
            par.remove(child)
    run = ET.SubElement(par, WNS + "r")
    if rpr is not None:
        run.append(_deepcopy(rpr))
    t = ET.SubElement(run, WNS + "t")
    t.text = str(value)
    if str(value) != str(value).strip():
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")


# ---------------------------------------------------------------- tables ---
def find_table(root, header_snippets):
    """Return the w:tbl whose first data-ish row contains all header snippets."""
    best = None
    for tbl in root.iter(WNS + "tbl"):
        rows = tbl.findall(WNS + "tr")
        if not rows:
            continue
        texts = []
        for r in rows[:3]:
            texts.append(" ".join("".join(t.text or "" for t in c.iter(WNS + "t"))
                                  for c in r.findall(WNS + "tc")))
        joined = " ".join(texts)
        if all(sn.lower() in joined.lower() for sn in header_snippets):
            best = tbl
            break
    return best


def clone_rows(tbl, n_data):
    """Ensure the table has n_data rows after its header rows.

    Header rows = rows whose cells contain heading text (non-placeholder).
    The LAST existing data row (or last row) is the row template.
    Returns list of data-row elements.
    """
    rows = tbl.findall(WNS + "tr")
    if not rows:
        raise DocxFillError("table without rows")
    def is_header(r):
        txts = "".join(t.text or "" for t in r.iter(WNS + "t")).strip().lower()
        return bool(txts) and not is_placeholder(txts) and not txts.startswith("click or tap")
    n_head = 0
    for r in rows:
        if is_header(r):
            n_head += 1
        else:
            break
    template = rows[-1] if len(rows) > n_head else rows[-1]
    data_rows = rows[n_head:]
    while len(data_rows) < n_data:
        new_r = _deepcopy(template)
        tbl.append(new_r)
        data_rows = tbl.findall(WNS + "tr")[n_head:]
    # remove surplus rows if fewer data items than existing rows
    while len(data_rows) > n_data:
        tbl.remove(data_rows.pop())
    return data_rows


def fill_row(row, values, kinds=None):
    """Fill a table row's cells positionally.

    values: list of strings ("" clears). kinds: optional list of
    'text'|'date'|'list' hints per cell; auto-detected when omitted.
    A cell holding an SDT is filled through the SDT; otherwise the cell's
    first paragraph is filled directly.
    """
    cells = row.findall(WNS + "tc")
    if kinds is None:
        kinds = ["text"] * len(cells)
    n = min(len(cells), len(values))
    report = []
    for i in range(n):
        cell = cells[i]
        val, kind = values[i], kinds[i]
        sdts = list(cell.iter(WNS + "sdt"))
        if sdts:
            sdt = sdts[0]
            k = sdt_kind(sdt)
            if k == "date" or kind == "date":
                fill_sdt(sdt, val)
            elif k == "list" or kind == "list":
                fill_sdt(sdt, val)
            else:
                fill_sdt(sdt, val)
            report.append(("sdt", k))
        else:
            pars = cell.findall(WNS + "p")
            if not pars:
                pars = [ET.SubElement(cell, WNS + "p")]
            fill_plain_paragraph(pars[0], val)
            report.append(("par", kind))
    return report


# ---------------------------------------------------------------- images ---
EMU_PER_CM = 360000


def add_png(parts, png_path, width_cm=15.0):
    """Add a PNG part + relationship; return (rid, media_name, cx, cy)."""
    import struct as _struct
    with open(png_path, "rb") as f:
        data = f.read()
    w_px, h_px = _png_size(data)
    media = sorted([n for n in parts if n.startswith("word/media/")])
    idx = len(media) + 1
    name = "word/media/image_icam_%d.png" % idx
    parts[name] = data

    rels_key = "word/_rels/document.xml.rels"
    rels = parse_xml(parts[rels_key])
    rids = [r.get("Id") for r in rels]
    n = 1
    while "rIdIcam%d" % n in rids:
        n += 1
    rid = "rIdIcam%d" % n
    rel_el = ET.SubElement(rels, "{http://schemas.openxmlformats.org/package/2006/relationships}Relationship")
    rel_el.set("Id", rid)
    rel_el.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
    rel_el.set("Target", name.replace("word/", ""))
    parts[rels_key] = serialise(rels)

    ct_key = "[Content_Types].xml"
    ct = parse_xml(parts[ct_key])
    has_png = any(d.get("Extension", "").lower() == "png"
                  for d in ct.iter("{http://schemas.openxmlformats.org/package/2006/content-types}Default"))
    if not has_png:
        d = ET.Element("{http://schemas.openxmlformats.org/package/2006/content-types}Default")
        d.set("Extension", "png")
        d.set("ContentType", "image/png")
        ct.insert(0, d)
        parts[ct_key] = serialise(ct)

    cx = int(width_cm * EMU_PER_CM)
    cy = int(cx * h_px / max(1, w_px))
    return rid, name, cx, cy


def _png_size(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise DocxFillError("not a PNG file")
    w, h = struct.unpack(">II", data[16:24])
    return w, h


DRAWING_XML = (
    '<w:drawing xmlns:w="%s" xmlns:wp="%s" xmlns:a="%s" xmlns:pic="%s" xmlns:r="%s">'
    '<wp:inline distT="0" distB="0" distL="0" distR="0">'
    "<wp:extent cx=\"{cx}\" cy=\"{cy}\"/>"
    "<wp:docPr id=\"{id}\" name=\"{name}\"/>"
    '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
    "<pic:pic>"
    '<pic:nvPicPr><pic:cNvPr id="{id}" name="{name}"/><pic:cNvPicPr/></pic:nvPicPr>'
    '<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
    '<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
    '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
    "</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing>"
) % (NSMAP["w"], NSMAP["wp"], NSMAP["a"], NSMAP["pic"], NSMAP["r"])


def insert_image_after(anchor_par, rid, name, cx, cy, doc_id=1, caption=None):
    """Insert an inline-image paragraph (plus optional caption) after anchor."""
    xml = (DRAWING_XML.replace("{cx}", str(cx)).replace("{cy}", str(cy))
           .replace("{id}", str(doc_id)).replace("{name}", esc(name))
           .replace("{rid}", rid))
    pic_p = ET.Element(WNS + "p")
    jc = ET.SubElement(ET.SubElement(pic_p, WNS + "pPr"), WNS + "jc")
    jc.set(WNS + "val", "center")
    run = ET.SubElement(pic_p, WNS + "r")
    run.append(ET.fromstring(xml))
    anchor_par.addnext(pic_p)
    last = pic_p
    if caption:
        cap_p = ET.Element(WNS + "p")
        ppr = ET.SubElement(cap_p, WNS + "pPr")
        jc2 = ET.SubElement(ppr, WNS + "jc")
        jc2.set(WNS + "val", "center")
        r = ET.SubElement(cap_p, WNS + "r")
        rpr = ET.SubElement(r, WNS + "rPr")
        ET.SubElement(rpr, WNS + "i")
        t = ET.SubElement(r, WNS + "t")
        t.text = caption
        last.addnext(cap_p)
        last = cap_p
    return last


def find_paragraph_by_text(root, snippet):
    for p in root.iter(WNS + "p"):
        txt = "".join(t.text or "" for t in p.iter(WNS + "t"))
        if snippet.lower() in txt.lower():
            return p
    return None


# ------------------------------------------------------- branded creation ---
# GAWB brand tokens (Design and Brand Guidelines: Pantone 7461 C primary,
# Pantone 3268 C secondary; Verdana is the brand-approved universally
# available typeface, used for generated artefacts).
BRAND_BLUE = "007CBB"    # Pantone 7461 C
BRAND_TEAL = "00A98F"    # Pantone 3268 C
BRAND_LIGHT = "E8F3FA"   # light blue band for alternating rows / key cells
BRAND_GREY = "595959"    # captions and footers
BRAND_FONT = "Verdana"

_A4_W = 11906
_A4_H = 16838
_MARGIN = 1134          # 2 cm in twentieths of a point
_USABLE = _A4_W - 2 * _MARGIN

PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"

_DOC_SHELL = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<w:document xmlns:w="%s" xmlns:r="%s"><w:body>'
    '<w:sectPr><w:footerReference r:id="rIdFooter" w:type="default"/>'
    '<w:pgSz w:w="%d" w:h="%d"/>'
    '<w:pgMar w:top="%d" w:right="%d" w:bottom="%d" w:left="%d"'
    ' w:header="709" w:footer="709" w:gutter="0"/>'
    "</w:sectPr></w:body></w:document>"
) % (NSMAP["w"], NSMAP["r"], _A4_W, _A4_H, _MARGIN, _MARGIN, _MARGIN, _MARGIN)

_CT_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Types xmlns="%s">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Default Extension="png" ContentType="image/png"/>'
    '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
    '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
    '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
    '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
    '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
    "</Types>"
) % CT_NS

_RELS_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="%s">'
    '<Relationship Id="rId1" Type="%s/officeDocument" Target="word/document.xml"/>'
    '<Relationship Id="rId2" Type="%s/metadata/core-properties" Target="docProps/core.xml"/>'
    '<Relationship Id="rId3" Type="%s/extended-properties" Target="docProps/app.xml"/>'
    "</Relationships>"
) % (PKG, "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
     PKG, "http://schemas.openxmlformats.org/officeDocument/2006/relationships")

_DOC_RELS_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="%s">'
    '<Relationship Id="rIdStyles" Type="%s/styles" Target="styles.xml"/>'
    '<Relationship Id="rIdFooter" Type="%s/footer" Target="footer1.xml"/>'
    "</Relationships>"
) % (PKG,
     "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
     "http://schemas.openxmlformats.org/officeDocument/2006/relationships")

_STYLES_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<w:styles xmlns:w="%s">'
    "<w:docDefaults><w:rPrDefault><w:rPr>"
    '<w:rFonts w:ascii="%s" w:hAnsi="%s" w:cs="%s"/>'
    '<w:color w:val="262626"/><w:sz w:val="19"/><w:szCs w:val="19"/>'
    "</w:rPr></w:rPrDefault>"
    "<w:pPrDefault><w:pPr>"
    '<w:spacing w:after="120" w:line="264" w:lineRule="auto"/>'
    "</w:pPr></w:pPrDefault></w:docDefaults>"
    '<w:style w:type="paragraph" w:default="1" w:styleId="Normal">'
    '<w:name w:val="Normal"/><w:qFormat/></w:style>'
    "</w:styles>"
) % (NSMAP["w"], BRAND_FONT, BRAND_FONT, BRAND_FONT)

def _footer_xml():
    ftr = ET.Element(WNS + "ftr")
    p = ET.SubElement(ftr, WNS + "p")
    ppr = ET.SubElement(p, WNS + "pPr")
    jc = ET.SubElement(ppr, WNS + "jc")
    jc.set(WNS + "val", "right")

    def small_run(par, text):
        r = ET.SubElement(par, WNS + "r")
        r.append(_rpr(size=14, colour=BRAND_GREY))
        t = ET.SubElement(r, WNS + "t")
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        t.text = text

    small_run(p, "Page ")
    for instr in ("PAGE", "NUMPAGES"):
        fld = ET.SubElement(p, WNS + "fldSimple")
        fld.set(WNS + "instr", " %s " % instr)
        r = ET.SubElement(fld, WNS + "r")
        r.append(_rpr(size=14, colour=BRAND_GREY))
        ET.SubElement(r, WNS + "t").text = "1"
        if instr == "PAGE":
            small_run(p, " of ")
    return serialise(ftr)


_APP_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"'
    ' xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
    "<Application>GAWB ICAM Investigation Skill</Application>"
    "</Properties>"
)


def new_parts(title):
    """Minimal valid DOCX parts dict with GAWB defaults."""
    core = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"'
        ' xmlns:dc="http://purl.org/dc/elements/1.1/">'
        "<dc:title>%s</dc:title>"
        "<dc:creator>GAWB ICAM Investigation Skill</dc:creator>"
        "<cp:lastModifiedBy>GAWB ICAM Investigation Skill</cp:lastModifiedBy>"
        "</cp:coreProperties>"
    ) % esc(title)
    return {
        "[Content_Types].xml": _CT_XML.encode("utf-8"),
        "_rels/.rels": _RELS_XML.encode("utf-8"),
        "word/document.xml": _DOC_SHELL.encode("utf-8"),
        "word/_rels/document.xml.rels": _DOC_RELS_XML.encode("utf-8"),
        "word/styles.xml": _STYLES_XML.encode("utf-8"),
        "word/footer1.xml": _footer_xml(),
        "docProps/core.xml": core.encode("utf-8"),
        "docProps/app.xml": _APP_XML.encode("utf-8"),
    }


def open_doc(title):
    """Return (parts, document_root, body) for building a branded document."""
    parts = new_parts(title)
    doc = parse_xml(parts["word/document.xml"])
    body = doc.find(WNS + "body")
    return parts, doc, body


def _body_append(body, el):
    """Append keeping w:sectPr as the last body child."""
    sect = body.find(WNS + "sectPr")
    if sect is not None:
        body.insert(list(body).index(sect), el)
    else:
        body.append(el)


def _rpr(bold=False, italic=False, size=None, colour=None, font=None, underline=False):
    rpr = ET.Element(WNS + "rPr")
    rf = ET.SubElement(rpr, WNS + "rFonts")
    f = font or BRAND_FONT
    rf.set(WNS + "ascii", f)
    rf.set(WNS + "hAnsi", f)
    rf.set(WNS + "cs", f)
    if bold:
        ET.SubElement(rpr, WNS + "b")
        ET.SubElement(rpr, WNS + "bCs")
    if italic:
        ET.SubElement(rpr, WNS + "i")
        ET.SubElement(rpr, WNS + "iCs")
    if colour:
        c = ET.SubElement(rpr, WNS + "color")
        c.set(WNS + "val", colour)
    if size is not None:
        sz = ET.SubElement(rpr, WNS + "sz")
        sz.set(WNS + "val", str(size))
        szcs = ET.SubElement(rpr, WNS + "szCs")
        szcs.set(WNS + "val", str(size))
    if underline:
        u = ET.SubElement(rpr, WNS + "u")
        u.set(WNS + "val", "single")
    return rpr


def _mk_par(runs, jc=None, shd=None, outline=None, before=None, after=None,
            left=None, hanging=None):
    # child order per schema: shd, spacing, ind, jc, outlineLvl
    p = ET.Element(WNS + "p")
    ppr = ET.SubElement(p, WNS + "pPr")
    if shd is not None:
        s = ET.SubElement(ppr, WNS + "shd")
        s.set(WNS + "val", "clear")
        s.set(WNS + "color", "auto")
        s.set(WNS + "fill", shd)
    if before is not None or after is not None:
        sp = ET.SubElement(ppr, WNS + "spacing")
        if before is not None:
            sp.set(WNS + "before", str(before))
        if after is not None:
            sp.set(WNS + "after", str(after))
    if left is not None or hanging is not None:
        ind = ET.SubElement(ppr, WNS + "ind")
        if left is not None:
            ind.set(WNS + "left", str(left))
        if hanging is not None:
            ind.set(WNS + "hanging", str(hanging))
    if jc is not None:
        j = ET.SubElement(ppr, WNS + "jc")
        j.set(WNS + "val", jc)
    if outline is not None:
        o = ET.SubElement(ppr, WNS + "outlineLvl")
        o.set(WNS + "val", str(outline))
    for text, kw in runs:
        r = ET.SubElement(p, WNS + "r")
        r.append(_rpr(**kw))
        t = ET.SubElement(r, WNS + "t")
        t.text = str(text)
        if str(text) != str(text).strip():
            t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    return p


def banner(body, title, subtitle=None, fill=None):
    """Full-width brand banner: white bold title (and subtitle) on brand blue."""
    fill = fill or BRAND_BLUE
    size = 30 if len(title) <= 42 else 24
    _body_append(body, _mk_par(
        [(title, dict(bold=True, size=size, colour="FFFFFF"))],
        shd=fill, after=0 if subtitle else 240))
    if subtitle:
        _body_append(body, _mk_par(
            [(subtitle, dict(size=16, colour="FFFFFF"))], shd=fill, after=240))


def heading(body, text, level=1):
    if level == 1:
        p = _mk_par([(text, dict(bold=True, size=24, colour=BRAND_BLUE))],
                    outline=0, before=280, after=120)
    else:
        p = _mk_par([(text, dict(bold=True, size=21, colour=BRAND_TEAL))],
                    outline=1, before=220, after=100)
    _body_append(body, p)
    return p


def para(body, text, bold=False, italic=False, size=None, colour=None,
         align=None, after=None):
    p = _mk_par([(text, dict(bold=bold, italic=italic, size=size,
                             colour=colour))],
                jc=align, after=after)
    _body_append(body, p)
    return p


def bullets(body, items, glyph="\u2022", bold_first=False):
    for item in items:
        if bold_first and ": " in item:
            head, rest = item.split(": ", 1)
            runs = [("%s  " % glyph, dict(colour=BRAND_BLUE, bold=True)),
                    (head + ": ", dict(bold=True)),
                    (rest, dict())]
            p = _mk_par(runs, left=340, hanging=170)
        else:
            p = _mk_par([("%s  " % glyph, dict(colour=BRAND_BLUE, bold=True)),
                         (item, dict())], left=340, hanging=170)
        _body_append(body, p)


def checklist(body, items):
    bullets(body, items, glyph=UNCHECKED)


def _tc(width, text, bold=False, colour=None, fill=None, size=None,
        italic=False):
    tc = ET.Element(WNS + "tc")
    tcpr = ET.SubElement(tc, WNS + "tcPr")
    w = ET.SubElement(tcpr, WNS + "tcW")
    w.set(WNS + "w", str(width))
    w.set(WNS + "type", "dxa")
    if fill:
        s = ET.SubElement(tcpr, WNS + "shd")
        s.set(WNS + "val", "clear")
        s.set(WNS + "color", "auto")
        s.set(WNS + "fill", fill)
    va = ET.SubElement(tcpr, WNS + "vAlign")
    va.set(WNS + "val", "center")
    lines = str(text).split("\n") if text is not None else [""]
    for i, line in enumerate(lines):
        p = _mk_par([(line, dict(bold=bold, colour=colour, size=size,
                                 italic=italic))], after=40 if i < len(lines) - 1 else 0)
        tc.append(p)
    return tc


def table(body, headers, rows, fracs=None, size=17, header_fill=None,
          banded=True):
    """Branded table; fracs = relative column widths (sum need not be 1)."""
    n = len(headers) if headers else len(rows[0]) if rows else 0
    if fracs is None:
        fracs = [1] * n
    total = float(sum(fracs)) or 1.0
    widths = [int(_USABLE * f / total) for f in fracs]
    tbl = ET.Element(WNS + "tbl")
    tblpr = ET.SubElement(tbl, WNS + "tblPr")
    tw = ET.SubElement(tblpr, WNS + "tblW")
    tw.set(WNS + "w", str(_USABLE))
    tw.set(WNS + "type", "dxa")
    borders = ET.SubElement(tblpr, WNS + "tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b = ET.SubElement(borders, WNS + edge)
        b.set(WNS + "val", "single")
        b.set(WNS + "sz", "4")
        b.set(WNS + "color", "B7C9D6")
    layout = ET.SubElement(tblpr, WNS + "tblLayout")
    layout.set(WNS + "type", "fixed")
    grid = ET.SubElement(tbl, WNS + "tblGrid")
    for wd in widths:
        gc = ET.SubElement(grid, WNS + "gridCol")
        gc.set(WNS + "w", str(wd))
    if headers:
        tr = ET.SubElement(tbl, WNS + "tr")
        trpr = ET.SubElement(tr, WNS + "trPr")
        ET.SubElement(trpr, WNS + "tblHeader")
        for i, htext in enumerate(headers):
            tr.append(_tc(widths[i], htext, bold=True, colour="FFFFFF",
                          fill=header_fill or BRAND_BLUE, size=size))
    for ri, row in enumerate(rows):
        tr = ET.SubElement(tbl, WNS + "tr")
        fill = BRAND_LIGHT if (banded and ri % 2 == 1) else None
        for i, cell in enumerate(row):
            tr.append(_tc(widths[i], cell, fill=fill, size=size))
    _body_append(body, tbl)
    return tbl


def kv_table(body, pairs, key_frac=0.26, key_fill=None):
    """Two-column table: bold shaded key column, plain value column."""
    return _kv(body, pairs, key_frac, key_fill)


def _kv(body, pairs, key_frac, key_fill):
    total = float(key_frac) * 4  # key gets key_frac/4 of width
    widths = [int(_USABLE * key_frac / (key_frac + 1)), _USABLE - int(_USABLE * key_frac / (key_frac + 1))]
    tbl = ET.Element(WNS + "tbl")
    tblpr = ET.SubElement(tbl, WNS + "tblPr")
    tw = ET.SubElement(tblpr, WNS + "tblW")
    tw.set(WNS + "w", str(_USABLE))
    tw.set(WNS + "type", "dxa")
    borders = ET.SubElement(tblpr, WNS + "tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b = ET.SubElement(borders, WNS + edge)
        b.set(WNS + "val", "single")
        b.set(WNS + "sz", "4")
        b.set(WNS + "color", "B7C9D6")
    layout = ET.SubElement(tblpr, WNS + "tblLayout")
    layout.set(WNS + "type", "fixed")
    grid = ET.SubElement(tbl, WNS + "tblGrid")
    for wd in widths:
        gc = ET.SubElement(grid, WNS + "gridCol")
        gc.set(WNS + "w", str(wd))
    for k, v in pairs:
        tr = ET.SubElement(tbl, WNS + "tr")
        tr.append(_tc(widths[0], k, bold=True, fill=key_fill or BRAND_LIGHT, size=17))
        tr.append(_tc(widths[1], v, size=17))
    _body_append(body, tbl)
    return tbl


def insert_png_body(body, parts, png_path, width_cm=16.5, doc_id=90):
    """Embed a PNG at the end of a branded document body."""
    rid, name, cx, cy = add_png(parts, png_path, width_cm=width_cm)
    xml = (DRAWING_XML.replace("{cx}", str(cx)).replace("{cy}", str(cy))
           .replace("{id}", str(doc_id)).replace("{name}", esc(name))
           .replace("{rid}", rid))
    p = ET.Element(WNS + "p")
    jc = ET.SubElement(ET.SubElement(p, WNS + "pPr"), WNS + "jc")
    jc.set(WNS + "val", "center")
    r = ET.SubElement(p, WNS + "r")
    r.append(ET.fromstring(xml))
    _body_append(body, p)
    return p


def save_doc(parts, doc, path):
    parts["word/document.xml"] = serialise(doc)
    save_parts(parts, path)
