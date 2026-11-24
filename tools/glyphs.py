"""Text -> SVG glyph paths, so the README art renders identically everywhere.

Fonts (all SIL OFL, from google/fonts) live in tools/fonts/ and are not committed:
  NotoSerifSC[wght].ttf, InstrumentSerif-Regular/Italic.ttf, JetBrainsMono[wght].ttf
"""
from __future__ import annotations

import unicodedata
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

FONT_DIR = Path(__file__).parent / "fonts"

_FILES = {
    "cjk": "NotoSerifSC.ttf",
    "serif": "InstrumentSerif-Regular.ttf",
    "serif-it": "InstrumentSerif-Italic.ttf",
    "mono": "JetBrainsMono.ttf",
}
_fonts: dict[str, TTFont] = {}


def _font(key: str) -> TTFont:
    if key not in _fonts:
        _fonts[key] = TTFont(FONT_DIR / _FILES[key], lazy=True)
    return _fonts[key]


def _is_cjk(ch: str) -> bool:
    if ch in "，。、：；！？「」『』（）《》—…·":
        return ch != "·"
    name = unicodedata.name(ch, "")
    return "CJK" in name or "FULLWIDTH" in name or "IDEOGRAPHIC" in name


class Doc:
    """Collects glyph <path> defs for one SVG file and emits <use> runs."""

    def __init__(self, prefix: str):
        self.prefix = prefix
        self.defs: dict[tuple, str] = {}
        self.paths: list[str] = []
        self._gs: dict[tuple, object] = {}
        self._drawn: set[str] = set()

    def _glyphset(self, key: str, wght: int | None):
        k = (key, wght)
        if k not in self._gs:
            f = _font(key)
            loc = {"wght": wght} if (wght and "fvar" in f) else None
            self._gs[k] = f.getGlyphSet(location=loc) if loc else f.getGlyphSet()
        return self._gs[k]

    def _glyph(self, key: str, wght: int | None, ch: str):
        f = _font(key)
        cmap = f.getBestCmap()
        gname = cmap.get(ord(ch))
        if gname is None:
            if key != "cjk":
                return self._glyph("cjk", wght or 400, ch)
            return None, 0, 1000
        gs = self._glyphset(key, wght)
        upm = f["head"].unitsPerEm
        g = gs[gname]
        dk = (key, wght, gname)
        if dk not in self.defs:
            pen = SVGPathPen(gs, ntos=lambda v: f"{v:.0f}" if v == int(v) else f"{v:.1f}")
            g.draw(pen)
            d = pen.getCommands()
            gid = f"{self.prefix}{len(self.defs)}"
            self.defs[dk] = gid
            if d:
                self.paths.append(f'<path id="{gid}" d="{d}"/>')
                self._drawn.add(gid)
        gid = self.defs[dk]
        return (gid if gid in self._drawn else None), g.width, upm

    def measure(self, s: str, size: float, style: str = "serif", wght: int | None = None, tracking: float = 0) -> float:
        return self._layout(s, 0, 0, size, style, wght, tracking)[1]

    def _layout(self, s, x, y, size, style, wght, tracking):
        uses = []
        cx = x
        for ch in s:
            key = "cjk" if (style == "cjk" or _is_cjk(ch)) else style
            w = wght if key in ("cjk", "mono") else None
            if key == "cjk" and w is None:
                w = 500
            gid, adv, upm = self._glyph(key, w, ch)
            sc = size / upm
            if ch != " " and gid:
                uses.append(f'<use href="#{gid}" transform="translate({cx:.2f} {y:.2f}) scale({sc:.5f} {-sc:.5f})"/>')
            cx += adv * sc + tracking * size
        return uses, cx - x - (tracking * size if s else 0)

    def text(self, s: str, x: float, y: float, size: float, style: str = "serif", wght: int | None = None,
             fill: str = "#fff", anchor: str = "start", tracking: float = 0, cls: str = "", extra: str = "") -> str:
        width = self.measure(s, size, style, wght, tracking)
        if anchor == "middle":
            x -= width / 2
        elif anchor == "end":
            x -= width
        uses, _ = self._layout(s, x, y, size, style, wght, tracking)
        c = f' class="{cls}"' if cls else ""
        return f'<g fill="{fill}"{c}{extra}>' + "".join(uses) + "</g>"

    def defs_block(self) -> str:
        # glyphs are drawn in font units with y up; <use> flips them
        return "<defs>" + "".join(self.paths) + "</defs>"
