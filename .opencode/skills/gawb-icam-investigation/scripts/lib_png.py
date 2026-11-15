"""lib_png.py - stdlib-only raster renderer for GAWB ICAM chart artefacts.

Generates PNG images (timeline, 5-Whys, ICAM analysis chart, PEEPO chart)
without any third-party package and without network access. Text is drawn
from embedded Verdana glyph bitmaps (GAWB brand secondary typeface); shapes
are anti-aliased by 2x supersampling.

No secrets, no tenant data. Runs on Python 3.8+ standard library only.
"""
import struct, zlib, base64, os, sys

# ---------------------------------------------------------------- brand ----
GAWB_BLUE = (0, 124, 187)        # Pantone 7461 C  #007CBB
GAWB_GREEN = (0, 169, 143)       # Pantone 3268 C  #00A98F
GAWB_DEEPBLUE = (0, 78, 116)     # #004E74
GAWB_LIGHTBLUE = (0, 179, 240)   # #00B3F0
GAWB_LIME = (217, 226, 90)       # #D9E25A
GAWB_DEEPGREEN = (0, 58, 50)     # #003A32
GAWB_ORANGE = (251, 174, 66)     # #FBAE42
INK = (26, 43, 51)               # neutral dark text
GREY = (90, 107, 114)            # secondary text
PANEL = (240, 247, 250)          # light panel fill
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- font -----
# Embedded Verdana glyph bitmaps (regular + bold), rendered at 32px em.
# Packed struct: <BHHhhH> per glyph (code,w,h,dx,dy,adv) followed by w*h alpha
# bytes; whole payload zlib-compressed then base64-encoded.
FONT_REG_B64 = "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"
FONT_BOLD_B64 = "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"

_font_cache = {}
_glyph_cache = {}

def _load_font(kind):
    if kind in _font_cache:
        return _font_cache[kind]
    b64 = FONT_REG_B64 if kind == "reg" else FONT_BOLD_B64
    raw = zlib.decompress(base64.b64decode(b64))
    n = raw[0]
    off = 1
    glyphs = {}
    for _ in range(n):
        code, w, h, dx, dy, adv = struct.unpack_from("<BHHhhH", raw, off)
        off += 11
        px = raw[off:off + w * h]
        off += w * h
        glyphs[code] = (w, h, dx, dy, adv, px)
    _font_cache[kind] = glyphs
    return glyphs

def _scaled_glyph(code, kind, scale):
    """Bilinear-scale a glyph alpha map to float scale; cached."""
    key = (code, kind, round(scale, 2))
    if key in _glyph_cache:
        return _glyph_cache[key]
    glyphs = _load_font(kind)
    w, h, dx, dy, adv, px = glyphs[code]
    tw, th = max(1, int(round(w * scale))), max(1, int(round(h * scale)))
    if w == 0 or h == 0:
        out = (0, 0, b"")
        _glyph_cache[key] = out
        return out
    src = [px[r * w + c] for r in range(h) for c in range(w)]
    dst = bytearray(tw * th)
    x_ratio, y_ratio = (w - 1) / max(1, tw - 1), (h - 1) / max(1, th - 1)
    for r in range(th):
        sy = r * y_ratio
        y0, y1 = int(sy), min(h - 1, int(sy) + 1)
        fy = sy - y0
        for c in range(tw):
            sx = c * x_ratio
            x0, x1 = int(sx), min(w - 1, int(sx) + 1)
            fx = sx - x0
            a00, a10 = src[y0 * w + x0], src[y0 * w + x1]
            a01, a11 = src[y1 * w + x0], src[y1 * w + x1]
            a = (a00 * (1 - fx) + a10 * fx) * (1 - fy) + \
                (a01 * (1 - fx) + a11 * fx) * fy
            dst[r * tw + c] = int(a + 0.5)
    out = (tw, th, bytes(dst))
    _glyph_cache[key] = out
    return out

# ---------------------------------------------------------------- png ------
def _png_chunk(tag, data):
    c = struct.pack(">I", len(data)) + tag + data
    return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

def _write_png(path, w, h, rgb):
    raw = bytearray()
    stride = w * 3
    for r in range(h):
        raw.append(0)
        raw += rgb[r * stride:(r + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(_png_chunk(b"IHDR", ihdr))
        f.write(_png_chunk(b"IDAT", zlib.compress(bytes(raw), 6)))
        f.write(_png_chunk(b"IEND", b""))

# ---------------------------------------------------------------- canvas ---
class Canvas:
    SS = 2  # supersample factor

    def __init__(self, w, h, bg=WHITE):
        self.w, self.h = w, h
        self.W, self.H = w * self.SS, h * self.SS
        self.buf = bytearray(self.W * self.H * 3)
        if bg != WHITE:
            self.rect(0, 0, w, h, bg)
        else:
            self._fill(0, 0, self.W, self.H, WHITE)

    # -- primitives (user coordinates are final-resolution px) -------------
    def rect(self, x, y, w, h, color, radius=0, outline=None, outline_w=1):
        S = self.SS
        x0, y0 = int(x * S), int(y * S)
        x1, y1 = int((x + w) * S), int((y + h) * S)
        if radius > 0:
            self._rrect_fill(x0, y0, x1, y1, int(radius * S), color)
        else:
            self._fill(x0, y0, x1, y1, color)
        if outline is not None:
            self._outline(x0, y0, x1, y1, int(outline_w * S), outline)

    def _fill(self, x0, y0, x1, y1, color):
        W3 = self.W * 3
        r, g, b = color
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(self.W, x1), min(self.H, y1)
        for yy in range(y0, y1):
            base = yy * W3 + x0 * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.buf[i] = r
                self.buf[i + 1] = g
                self.buf[i + 2] = b

    def _rrect_fill(self, x0, y0, x1, y1, rad, color):
        cx0, cy0, cx1, cy1 = x0 + rad, y0 + rad, x1 - rad, y1 - rad
        r2 = rad * rad
        for yy in range(max(0, y0), min(self.H, y1)):
            for xx in range(max(0, x0), min(self.W, x1)):
                if cx0 <= xx < cx1 or cy0 <= yy < cy1:
                    self._px(xx, yy, color)
                else:
                    dx = (xx - cx0) if xx < cx0 else ((xx - cx1 + 1) if xx >= cx1 else 0)
                    dy = (yy - cy0) if yy < cy0 else ((yy - cy1 + 1) if yy >= cy1 else 0)
                    if dx * dx + dy * dy <= r2:
                        self._px(xx, yy, color)

    def _outline(self, x0, y0, x1, y1, t, color):
        self._fill(x0, y0, x1, y0 + t, color)
        self._fill(x0, y1 - t, x1, y1, color)
        self._fill(x0, y0 + t, x0 + t, y1 - t, color)
        self._fill(x1 - t, y0 + t, x1, y1 - t, color)

    def _px(self, x, y, color):
        if 0 <= x < self.W and 0 <= y < self.H:
            i = (y * self.W + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = color

    def line(self, x0, y0, x1, y1, color, width=1.5, dash=None):
        S = self.SS
        x0, y0, x1, y1 = x0 * S, y0 * S, x1 * S, y1 * S
        t = max(1, int(width * S))
        half = (t - 1) / 2.0
        dx, dy = x1 - x0, y1 - y0
        dist = max(1e-6, (dx * dx + dy * dy) ** 0.5)
        steps = int(dist * 2) + 2
        for i in range(steps + 1):
            f = i / steps
            if dash:
                pos = f * dist / S  # user-space distance
                cycle = dash[0] + dash[1]
                if pos % cycle > dash[0]:
                    continue
            cx, cy = x0 + dx * f, y0 + dy * f
            self._fill(int(cx - half), int(cy - half), int(cx + half) + 1,
                       int(cy + half) + 1, color)

    def arrow(self, x0, y0, x1, y1, color, width=1.5, head=8):
        self.line(x0, y0, x1, y1, color, width)
        S = self.SS
        dx, dy = x1 - x0, y1 - y0
        dist = max(1e-6, (dx * dx + dy * dy) ** 0.5)
        ux, uy = dx / dist, dy / dist
        px, py = -uy, ux
        hs = head * S
        tip = (x1 * S, y1 * S)
        b1 = (x1 * S - ux * hs + px * hs * 0.5, y1 * S - uy * hs + py * hs * 0.5)
        b2 = (x1 * S - ux * hs - px * hs * 0.5, y1 * S - uy * hs - py * hs * 0.5)
        self._tri(tip, b1, b2, color)

    def _tri(self, p0, p1, p2, color):
        minx = int(min(p0[0], p1[0], p2[0])); maxx = int(max(p0[0], p1[0], p2[0])) + 1
        miny = int(min(p0[1], p1[1], p2[1])); maxy = int(max(p0[1], p1[1], p2[1])) + 1
        d = (p1[0] - p0[0]) * (p2[1] - p0[1]) - (p2[0] - p0[0]) * (p1[1] - p0[1])
        if abs(d) < 1e-9:
            return
        for yy in range(max(0, miny), min(self.H, maxy)):
            for xx in range(max(0, minx), min(self.W, maxx)):
                w0 = ((p1[0] - xx) * (p2[1] - yy) - (p2[0] - xx) * (p1[1] - yy))
                w1 = ((p2[0] - xx) * (p0[1] - yy) - (p0[0] - xx) * (p2[1] - yy))
                w2 = ((p0[0] - xx) * (p1[1] - yy) - (p1[0] - xx) * (p0[1] - yy))
                if (d < 0 and w0 <= 0 and w1 <= 0 and w2 <= 0) or \
                   (d > 0 and w0 >= 0 and w1 >= 0 and w2 >= 0):
                    self._px(xx, yy, color)

    # -- text ----------------------------------------------------------------
    def text(self, x, y, s, size, color=INK, bold=False, align="left"):
        """Draw string with baseline at y (final px). align: left|center|right."""
        scale = size * self.SS / 32.0
        glyphs = _load_font("bold" if bold else "reg")
        widths = []
        for ch in s:
            g = glyphs.get(ord(ch)) or glyphs.get(63)
            widths.append(g[4] * scale if g else 0)
        total = sum(widths) / self.SS  # final-resolution px
        if align == "center":
            x -= total / 2.0
        elif align == "right":
            x -= total
        cx = x * self.SS
        for ch, wch in zip(s, widths):
            code = ord(ch)
            g = glyphs.get(code) or glyphs.get(63)
            if not g:
                cx += wch
                continue
            w, h, dx, dy, adv, px = g
            if w and h:
                tw, th, alpha = _scaled_glyph(code, "bold" if bold else "reg", scale)
                self._stamp(int(cx + dx * scale), int(y * self.SS + dy * scale),
                            tw, th, alpha, color)
            cx += wch
        return total / self.SS

    def _stamp(self, x0, y0, w, h, alpha, color):
        r, g, b = color
        W3 = self.W * 3
        for row in range(h):
            yy = y0 + row
            if yy < 0 or yy >= self.H:
                continue
            base = yy * W3
            arow = alpha[row * w:(row + 1) * w]
            for col in range(w):
                a = arow[col]
                if a == 0:
                    continue
                xx = x0 + col
                if xx < 0 or xx >= self.W:
                    continue
                i = base + xx * 3
                if a == 255:
                    self.buf[i], self.buf[i + 1], self.buf[i + 2] = r, g, b
                else:
                    inv = 255 - a
                    self.buf[i] = (self.buf[i] * inv + r * a) >> 8
                    self.buf[i + 1] = (self.buf[i + 1] * inv + g * a) >> 8
                    self.buf[i + 2] = (self.buf[i + 2] * inv + b * a) >> 8

    def text_w(self, s, size, bold=False):
        glyphs = _load_font("bold" if bold else "reg")
        scale = size * self.SS / 32.0
        return sum((glyphs.get(ord(c)) or glyphs.get(63) or (0, 0, 0, 0, 0, b""))[4]
                   for c in s) * scale / self.SS

    def wrap(self, s, width_px, size, bold=False):
        words = s.split()
        lines, cur = [], ""
        for wd in words:
            t = (cur + " " + wd).strip()
            if self.text_w(t, size, bold) <= width_px or not cur:
                cur = t
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    def wrapped(self, x, y, s, width_px, size, color=INK, bold=False,
                align="left", line_gap=1.25):
        lines = self.wrap(s, width_px, size, bold)
        step = size * line_gap
        for i, ln in enumerate(lines):
            self.text(x, y + i * step, ln, size, color, bold, align)
        return len(lines) * step

    # -- output ----------------------------------------------------------
    def save(self, path):
        S = self.SS
        out = bytearray(self.w * self.h * 3)
        for r in range(self.h):
            for c in range(self.w):
                i0 = ((r * S) * self.W + c * S) * 3
                i1 = i0 + 3
                i2 = i0 + self.W * 3
                i3 = i2 + 3
                for k in range(3):
                    out[(r * self.w + c) * 3 + k] = \
                        (self.buf[i0 + k] + self.buf[i1 + k] +
                         self.buf[i2 + k] + self.buf[i3 + k]) >> 2
        d = os.path.dirname(os.path.abspath(path))
        if d and not os.path.isdir(d):
            os.makedirs(d)
        _write_png(path, self.w, self.h, bytes(out))
        return path

    # -- brand furniture ---------------------------------------------------
    def header_band(self, title, subtitle=None, w=None):
        """GAWB header: deep blue band + light-blue brand strip."""
        h = 46 if subtitle else 34
        self.rect(0, 0, self.w, h, GAWB_DEEPBLUE)
        self.rect(0, h, self.w, 3, GAWB_LIGHTBLUE)
        ty = 15 if subtitle else 21
        self.text(16, ty + 8, title, 15, WHITE, True)
        if subtitle:
            self.text(16, ty + 24, subtitle, 10, (200, 224, 236))
        return h + 16

    def footer(self, text):
        y = self.h - 14
        self.line(16, y - 12, self.w - 16, y - 12, PANEL, 1)
        self.text(16, y, text, 8, GREY)
