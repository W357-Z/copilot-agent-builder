"""render_charts.py - generate the ICAM chart artefacts as branded PNG images.

Usage:
    python3 render_charts.py <investigation.json> <output_dir> [--only timeline|fivewhys|icam|peepo]

Reads the investigation data file (schema in references/data-contract.md) and
writes:
    icam-timeline.png   Section 11 timeline chart
    icam-5whys.png      Section 11 5-Whys chain
    icam-chart.png      Appendix 12.3 ICAM analysis chart
    peepo-chart.png     Section 10 PEEPO contributing-factor chart

Exit codes: 0 = all charts rendered; 3 = one or more charts skipped because
their data section is missing (JSON report on stdout); 2 = usage error.
Stdlib only; no network. GAWB brand colours from Design & Brand Guidelines.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_png import (Canvas, GAWB_BLUE, GAWB_GREEN, GAWB_DEEPBLUE, GAWB_DEEPGREEN,
                     GAWB_LIGHTBLUE, GAWB_LIME, GAWB_ORANGE, INK, GREY, PANEL, WHITE)

CHARTS = ["timeline", "fivewhys", "icam", "peepo"]

CAT_META = [
    ("organisational", "ORGANISATIONAL FACTORS", GAWB_DEEPBLUE),
    ("task_env", "TASK / ENVIRONMENTAL CONDITIONS", GAWB_GREEN),
    ("individual_team", "INDIVIDUAL / TEAM ACTIONS", GAWB_ORANGE),
    ("absent_failed", "ABSENT / FAILED DEFENCES", GAWB_BLUE),
]
PEEPO_META = [
    ("people", "PEOPLE", GAWB_DEEPBLUE),
    ("environment", "ENVIRONMENT", GAWB_GREEN),
    ("equipment", "EQUIPMENT", GAWB_LIGHTBLUE),
    ("procedures", "PROCEDURES", GAWB_LIME),
    ("organisation", "ORGANISATION", GAWB_ORANGE),
]


def _factor_lines(c, text, width, size=10):
    return c.wrap(str(text), width, size)


def render_icam(data, out):
    factors = data.get("factors") or {}
    incident = data.get("incident") or {}
    desc = incident.get("basic_event") or incident.get("description") or "Incident"
    W = 1560
    col_w = (W - 40 - 3 * 20) / 4.0
    c = Canvas(W, 400)
    top = c.header_band("ICAM ANALYSIS CHART",
                        "Incident Cause Analysis Method - contributing factors") + 6
    head_y = top + 26
    boxes = []
    y = head_y + 40
    for key, label, col in CAT_META:
        boxes.append((key, label, col, y))
        items = factors.get(key) or []
        hgt = 52 * 4 + 14 * 3 if False else 0
        col_h = 0
        col_h += 34
        for it in items:
            lines = _factor_lines(c, it.get("text", ""), col_w - 30)
            bh = max(44, 20 + len(lines) * 13)
            col_h += bh + 12
        y = max(y, top + 40 + col_h + 30)
    total_h = int(y + 150)
    c2 = Canvas(W, total_h)
    top = c2.header_band("ICAM ANALYSIS CHART",
                         "Incident Cause Analysis Method - contributing factors") + 6
    head_y = top + 26
    col_x = [20 + i * (col_w + 20) for i in range(4)]
    bottoms = {}
    y_start = head_y + 44
    for i, (key, label, col) in enumerate(CAT_META):
        x = col_x[i]
        c2.rect(x, head_y - 16, col_w, 34, col, radius=6)
        c2.wrapped(x + col_w / 2, head_y + 3, label, col_w - 16, 10.5, WHITE, True, "center", 1.15)
        yy = y_start
        for it in (factors.get(key) or []):
            code = (it.get("code") or "").strip()
            txt = it.get("text", "")
            lines = c2.wrap(txt, col_w - 34, 10)
            bh = max(46, 24 + len(lines) * 13)
            c2.rect(x, yy, col_w, bh, PANEL, radius=5, outline=col, outline_w=1.2)
            c2.rect(x, yy, 6, bh, col, radius=3)
            if code:
                c2.text(x + 14, yy + 20, code, 9.5, col, True)
                c2.wrapped(x + 14, yy + 34, txt, col_w - 30, 10, INK)
            else:
                c2.wrapped(x + 14, yy + 22, txt, col_w - 30, 10, INK)
            bottoms.setdefault(key, []).append(yy + bh)
            yy += bh + 12
    inc_w = 480
    inc_x = (W - inc_w) / 2
    all_bottoms = [b for lst in bottoms.values() for b in lst]
    bus_y = max(all_bottoms) + 26 if all_bottoms else inc_y - 20
    inc_y = bus_y + 44
    for i, (key, label, col) in enumerate(CAT_META):
        if key not in bottoms:
            continue
        cx = col_x[i] + col_w / 2
        for b in bottoms[key]:
            c2.line(cx, b + 3, cx, bus_y, col, 1.2)
        c2.line(cx, bus_y, W / 2, bus_y, col, 1.2)
    c2.arrow(W / 2, bus_y, W / 2, inc_y - 4, GAWB_DEEPBLUE, 1.8)
    c2.rect(inc_x, inc_y, inc_w, 72, GAWB_DEEPBLUE, radius=8)
    c2.text(W / 2, inc_y + 30, "INCIDENT", 14, WHITE, True, "center")
    lines = c2.wrap(desc, inc_w - 30, 10)
    c2.wrapped(W / 2, inc_y + 48, desc, inc_w - 30, 10, (200, 224, 236), False, "center", 1.2)
    return c2.save(out)


def _peepo_items(raw):
    """Normalise a PEEPO column: dict {text, ref} entries or plain strings."""
    items = []
    for it in (raw or []):
        if isinstance(it, dict):
            items.append((str(it.get("text", "")), str(it.get("ref", ""))))
        else:
            items.append((str(it), ""))
    return items


def render_peepo(data, out):
    peepo = data.get("peepo") or {}
    W = 1700
    col_w = (W - 40 - 4 * 16) / 5.0
    c0 = Canvas(W, 300)
    max_col = 0
    col_heights = []
    for key, label, col in PEEPO_META:
        h = 70
        for text, ref in _peepo_items(peepo.get(key)):
            lines = c0.wrap(text, col_w - 28, 10)
            h += max(42, 20 + len(lines) * 13) + 10
        col_heights.append(h)
    total_h = int(max(col_heights + [300]) + 90)
    c = Canvas(W, total_h)
    top = c.header_band("PEEPO CHART - CONTRIBUTING FACTORS",
                        "People / Environment / Equipment / Procedures / Organisation") + 6
    y0 = top + 12
    for i, (key, label, col) in enumerate(PEEPO_META):
        x = 20 + i * (col_w + 16)
        c.rect(x, y0, col_w, 34, col, radius=6)
        c.text(x + col_w / 2, y0 + 23, label, 10.5, WHITE, True, "center")
        yy = y0 + 46
        for text, ref in _peepo_items(peepo.get(key)):
            lines = c.wrap(text, col_w - 28, 10)
            bh = max(42, 20 + len(lines) * 13)
            c.rect(x, yy, col_w, bh, PANEL, radius=5, outline=col, outline_w=1.0)
            c.rect(x, yy, 5, bh, col, radius=2)
            c.wrapped(x + 13, yy + 20, text, col_w - 26, 10, INK)
            if ref:
                c.text(x + col_w - 12, yy + bh - 12, ref, 8, GREY, True, "right")
            yy += bh + 10
    return c.save(out)


def render_timeline(data, out):
    events = data.get("timeline") or []
    W = 1500
    row_h = 46
    H = 130 + len(events) * row_h + 60
    c = Canvas(W, H)
    top = c.header_band("TIMELINE CHART", "Sequence of events") + 10
    y = top + 18
    axis_x = 150
    c.line(axis_x, y - 6, axis_x, y + len(events) * row_h - 24, GAWB_DEEPBLUE, 2)
    for ev in events:
        time = str(ev.get("time", ""))
        text = str(ev.get("event", ""))
        src = str(ev.get("source", ""))
        c.rect(axis_x - 5, y + 6, 10, 10, GAWB_GREEN, radius=5)
        c.text(20, y + 16, time, 10, GAWB_DEEPBLUE, True)
        ev_w = W - axis_x - 320
        lines = c.wrap(text, ev_w, 10.5)
        c.wrapped(axis_x + 24, y + 16, text, ev_w, 10.5, INK)
        if src:
            c.wrapped(W - 180, y + 16, src, 160, 8.5, GREY)
        y += row_h
    c.footer("GAWB WHS-TMP-0207 attachment - timeline chart")
    return c.save(out)


def render_fivewhys(data, out):
    whys = data.get("fivewhys") or []
    incident = data.get("incident") or {}
    basic = data.get("basic_cause") or ""
    W = 1200
    box_w = W - 260
    # measure
    c0 = Canvas(W, 200)
    H = 150
    H += 64 + 24  # event box
    for w in whys:
        lines = c0.wrap(str(w.get("answer", "")), box_w - 40, 10.5)
        H += max(58, 46 + len(lines) * 13) + 34
    if basic:
        lines = c0.wrap(basic, box_w - 40, 10.5)
        H += max(60, 50 + len(lines) * 13) + 20
    H += 60
    c = Canvas(W, H)
    top = c.header_band("5-WHYS ANALYSIS", "From event to basic cause") + 10
    y = top + 12
    cx = W / 2
    x0 = 130
    event_desc = incident.get("basic_event") or incident.get("description") or "Incident"
    lines = c.wrap(event_desc, box_w - 40, 10.5)
    bh = max(56, 40 + len(lines) * 13)
    c.rect(x0, y, box_w, bh, GAWB_DEEPBLUE, radius=8)
    c.text(x0 + box_w / 2, y + 26, "THE EVENT", 11, WHITE, True, "center")
    c.wrapped(x0 + box_w / 2, y + 42, event_desc, box_w - 40, 10.5, (200, 224, 236), False, "center", 1.2)
    y += bh + 30
    for i, w in enumerate(whys):
        c.line(cx, y - 26, cx, y - 6, GREY, 1.5)
        c.arrow(cx, y - 26, cx, y - 8, GREY, 1.5)
        c.text(x0 - 14, y + 18, "WHY %d" % (i + 1), 10, GAWB_ORANGE, True, "right")
        q = str(w.get("question", "")).strip()
        a = str(w.get("answer", ""))
        lines = c.wrap(a, box_w - 40, 10.5)
        bh = max(58, 46 + len(lines) * 13)
        c.rect(x0, y, box_w, bh, PANEL, radius=6, outline=GAWB_ORANGE, outline_w=1.2)
        ty = y + 22
        if q:
            c.wrapped(x0 + 20, ty, "Q: " + q, box_w - 40, 9, GREY)
            ty += 15
        c.wrapped(x0 + 20, ty + 4, "A: " + a, box_w - 40, 10.5, INK)
        y += bh + 32
    if basic:
        c.line(cx, y - 26, cx, y - 8, GREY, 1.5)
        c.arrow(cx, y - 26, cx, y - 10, GREY, 1.5)
        lines = c.wrap(basic, box_w - 40, 10.5)
        bh = max(62, 50 + len(lines) * 13)
        c.rect(x0, y, box_w, bh, GAWB_ORANGE, radius=8)
        c.text(x0 + box_w / 2, y + 24, "BASIC CAUSE", 11, WHITE, True, "center")
        c.wrapped(x0 + box_w / 2, y + 42, basic, box_w - 40, 10.5, WHITE, False, "center", 1.2)
        y += bh
    c.footer("GAWB WHS-TMP-0207 attachment - 5-Whys analysis")
    return c.save(out)


def main(argv):
    args = [a for a in argv[1:]]
    only = None
    if "--only" in args:
        i = args.index("--only")
        if i + 1 >= len(args):
            print("usage: render_charts.py <data.json> <outdir> [--only name]")
            return 2
        only = args[i + 1]
        args = args[:i] + args[i + 2:]
    if len(args) != 2:
        print(__doc__)
        return 2
    src, outdir = args
    try:
        with open(src, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(json.dumps({"error": "cannot read data file: %s" % e}))
        return 2
    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    renderers = {
        "timeline": (render_timeline, "timeline", "icam-timeline.png"),
        "fivewhys": (render_fivewhys, "fivewhys", "icam-5whys.png"),
        "icam": (render_icam, "factors", "icam-chart.png"),
        "peepo": (render_peepo, "peepo", "peepo-chart.png"),
    }
    want = [only] if only in CHARTS else CHARTS
    done, skipped = [], {}
    for name in want:
        fn, section, fname = renderers[name]
        if not data.get(section):
            skipped[name] = "missing data section '%s'" % section
            continue
        fn(data, os.path.join(outdir, fname))
        done.append(os.path.join(outdir, fname))
    report = {"rendered": done, "skipped": skipped}
    print(json.dumps(report))
    return 0 if not skipped else 3


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
