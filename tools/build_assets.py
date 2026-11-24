"""Build the animated SVG art for the profile README.

Run:  python -I tools/build_assets.py   (needs fonttools + tools/fonts/*)
Writes assets/*.svg. All text is converted to glyph paths, so it looks the same
for every viewer regardless of installed fonts.
"""
from __future__ import annotations

import math
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from glyphs import Doc  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "assets"
W = 1300
BG = "#0D0E12"
INK = "#F4F1EA"
MUTED = "#8F97A4"
DIM = "#5D6470"
LINE = "rgba(255,255,255,.09)"
REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def svg(doc: Doc, w: int, h: int, title: str, style: str, body: str, defs: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-labelledby="t"><title id="t">{escape(title)}</title>'
        f"<style>{style}{REDUCED}</style>{doc.defs_block()}<defs>{defs}</defs>{body}</svg>"
    )


def panel(h: int, accent: str, gx: float, gy: float, glow_r: float = 520, glow_o: float = 0.16) -> tuple[str, str]:
    defs = (
        f'<clipPath id="pc"><rect x="1" y="1" width="{W-2}" height="{h-2}" rx="18"/></clipPath>'
        '<pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">'
        '<circle cx="2" cy="2" r="1" fill="rgba(255,255,255,.055)"/></pattern>'
        f'<radialGradient id="glow" cx="{gx}" cy="{gy}" r="{glow_r}" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="{accent}" stop-opacity="{glow_o}"/>'
        f'<stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>'
    )
    body = (
        f'<g clip-path="url(#pc)"><rect width="{W}" height="{h}" fill="{BG}"/>'
        f'<rect width="{W}" height="{h}" fill="url(#dots)"/>'
        f'<rect width="{W}" height="{h}" fill="url(#glow)"/></g>'
        f'<rect x="1" y="1" width="{W-2}" height="{h-2}" rx="18" fill="none" stroke="{LINE}" stroke-width="1.5"/>'
    )
    return defs, body


def write(name: str, content: str) -> None:
    OUT.mkdir(exist_ok=True)
    (OUT / name).write_text(content, encoding="utf-8")
    print(f"{name:28s} {len(content.encode())/1024:7.1f} KB")


# ---------------------------------------------------------------- header
PROJECTS = [
    ("01", "PLUSH", "#FF9F6E"),
    ("02", "MEMORY", "#FF7A93"),
    ("03", "AGENTS", "#8B7CFF"),
    ("04", "BAZI", "#E2553D"),
]
GOLD = "#E8C07A"


def header() -> None:
    h = 236
    d = Doc("h")
    defs, body = panel(h, GOLD, 180, 40, 560, 0.13)
    style = (
        "@keyframes hl{0%,8%{transform:scaleX(0)}24%,86%{transform:scaleX(1)}100%{transform:scaleX(0)}}"
        ".hl{transform-box:fill-box;transform-origin:left center;animation:hl 7s cubic-bezier(.6,0,.2,1) infinite}"
        "@keyframes cur{0%,49.9%{opacity:1}50%,100%{opacity:0}}.cur{animation:cur 1.1s steps(1) infinite}"
        "@keyframes u{0%,24.9%{opacity:1}25%,100%{opacity:0}}.u{opacity:0;animation:u 8s steps(1) infinite}"
        "@keyframes pulse{0%{transform:scale(1);opacity:.7}100%{transform:scale(3.2);opacity:0}}"
        ".pulse{transform-box:fill-box;transform-origin:center;animation:pulse 2s ease-out infinite}"
    )
    b = [body]
    # left identity block
    b.append(d.text("S-Xiao", 62, 124, 88, "serif", fill=INK))
    b.append(d.text("@ShmilyXI", 66, 158, 15, "mono", 400, fill=MUTED))
    b.append(d.text("BUILD SOLO · AI × HARDWARE · SINCE 2018", 66, 200, 11.5, "mono", 500, fill=DIM, tracking=0.18))
    b.append(f'<path d="M476 52V184" stroke="{LINE}" stroke-width="1.5"/>')
    # right tagline
    x0, y0, size = 526, 92, 33
    pre, hi, post = "让 AI ", "有温度", "，住进身边的小东西里。"
    wpre = d.measure(pre, size, "cjk", 600)
    whi = d.measure(hi, size, "cjk", 600)
    b.append(f'<rect class="hl" x="{x0+wpre-2:.1f}" y="{y0-9}" width="{whi+4:.1f}" height="12" rx="2" fill="{GOLD}" opacity=".32"/>')
    b.append(d.text(pre + hi + post, x0, y0, size, "cjk", 600, fill=INK))
    wall = d.measure(pre + hi + post, size, "cjk", 600)
    b.append(f'<rect class="cur" x="{x0+wall+6:.1f}" y="{y0-28}" width="13" height="32" fill="{GOLD}"/>')
    b.append(d.text("Giving AI a little warmth, and a home inside everyday things.", x0, 130, 21, "serif-it", fill="#A7AEBA"))
    # project index with rotating underline
    x = x0
    for i, (num, name, col) in enumerate(PROJECTS):
        label = f"{num} {name}"
        wl = d.measure(label, 11.5, "mono", 500, 0.16)
        b.append(f'<circle cx="{x+4}" cy="{191}" r="3.5" fill="{col}"/>')
        b.append(d.text(label, x + 14, 195, 11.5, "mono", 500, fill="#C9CED6", tracking=0.16))
        delay = [0, -6, -4, -2][i]
        b.append(f'<rect class="u" style="animation-delay:{delay}s" x="{x+14}" y="203" width="{wl:.1f}" height="2" rx="1" fill="{col}"/>')
        x += 14 + wl + 34
    # live badge
    lab = "BUILDING NOW"
    wl = d.measure(lab, 10.5, "mono", 500, 0.18)
    bx = W - 48 - wl
    b.append(f'<circle class="pulse" cx="{bx-12}" cy="40" r="4" fill="#3DDC97"/><circle cx="{bx-12}" cy="40" r="4" fill="#3DDC97"/>')
    b.append(d.text(lab, bx, 44, 10.5, "mono", 500, fill=MUTED, tracking=0.18))
    write("header.svg", svg(d, W, h, "S-Xiao · 让 AI 有温度，住进身边的小东西里。Giving AI a little warmth, and a home inside everyday things.", style, "".join(b), defs))


# ---------------------------------------------------------------- dividers
def divider(name: str, accent: str, glyph: str) -> None:
    h = 48
    d = Doc("d")
    cy = 24
    style = (
        "@keyframes sw{0%{transform:translateX(0)}70%,100%{transform:translateX(1700px)}}"
        ".sw{animation:sw 5s cubic-bezier(.45,0,.25,1) infinite}"
        "@keyframes beat{0%,60%,100%{transform:scale(1)}10%{transform:scale(1.22)}22%{transform:scale(.96)}32%{transform:scale(1.12)}}"
        ".beat{transform-box:fill-box;transform-origin:center;animation:beat 1.6s ease-in-out infinite}"
        "@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}"
        ".bob{animation:bob 1.8s ease-in-out infinite}"
        "@keyframes spin{to{transform:rotate(360deg)}}"
        ".spin{transform-box:fill-box;transform-origin:center;animation:spin 6s linear infinite}"
        "@keyframes tw{0%,100%{transform:scale(.7) rotate(0);opacity:.6}50%{transform:scale(1.15) rotate(45deg);opacity:1}}"
        ".tw{transform-box:fill-box;transform-origin:center;animation:tw 2.4s ease-in-out infinite}"
        "@keyframes blip{0%,100%{opacity:.35}50%{opacity:1}}.blip{animation:blip 1.5s ease-in-out infinite}"
    )
    defs = (
        f'<linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{accent}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{accent}"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></linearGradient>'
        f'<clipPath id="ln"><rect x="0" y="{cy-3}" width="612" height="6"/><rect x="688" y="{cy-3}" width="612" height="6"/></clipPath>'
    )
    b = [
        f'<path d="M0 {cy}H612M688 {cy}H1300" stroke="rgba(140,148,158,.4)" stroke-width="1.5"/>',
        f'<g clip-path="url(#ln)"><rect class="sw" x="-340" y="{cy-1.5}" width="340" height="3" rx="1.5" fill="url(#g)"/></g>',
        f'<circle cx="620" cy="{cy}" r="2.2" fill="rgba(140,148,158,.45)"/><circle cx="680" cy="{cy}" r="2.2" fill="rgba(140,148,158,.45)"/>',
    ]
    c = 650
    if glyph == "heart":
        b.append(f'<path class="beat" d="M{c} {cy+9}C{c-15} {cy} {c-14} {cy-10} {c-7} {cy-10}C{c-3} {cy-10} {c} {cy-6} {c} {cy-4}C{c} {cy-6} {c+3} {cy-10} {c+7} {cy-10}C{c+14} {cy-10} {c+15} {cy} {c} {cy+9}Z" fill="{accent}"/>')
    elif glyph == "pin":
        b.append(f'<g class="bob"><path d="M{c} {cy+12}C{c-8} {cy+2} {c-10} {cy-2} {c-10} {cy-5}A10 10 0 0 1 {c+10} {cy-5}C{c+10} {cy-2} {c+8} {cy+2} {c} {cy+12}Z" fill="none" stroke="{accent}" stroke-width="2"/>'
                 f'<circle cx="{c}" cy="{cy-5}" r="3.4" fill="{accent}"/></g>')
    elif glyph == "nodes":
        pts = [(c, cy - 9), (c - 10, cy + 8), (c + 10, cy + 8)]
        b.append(f'<path d="M{pts[0][0]} {pts[0][1]}L{pts[1][0]} {pts[1][1]}M{pts[0][0]} {pts[0][1]}L{pts[2][0]} {pts[2][1]}" stroke="{accent}" stroke-width="1.6"/>')
        for i, (px, py) in enumerate(pts):
            b.append(f'<circle class="blip" style="animation-delay:{-i*0.5}s" cx="{px}" cy="{py}" r="4" fill="{accent}"/>')
    elif glyph == "taiji":
        r = 11
        b.append(
            f'<g class="spin"><circle cx="{c}" cy="{cy}" r="{r}" fill="none" stroke="{accent}" stroke-width="1.6"/>'
            f'<path d="M{c} {cy-r}A{r} {r} 0 0 1 {c} {cy+r}A{r/2} {r/2} 0 0 1 {c} {cy}A{r/2} {r/2} 0 0 0 {c} {cy-r}Z" fill="{accent}"/>'
            f'<circle cx="{c}" cy="{cy-r/2}" r="2" fill="{accent}"/><circle cx="{c}" cy="{cy+r/2}" r="2" fill="{BG}"/></g>'
        )
    elif glyph == "star":
        s = 11
        b.append(f'<path class="tw" d="M{c} {cy-s}Q{c+1.6} {cy-1.6} {c+s} {cy}Q{c+1.6} {cy+1.6} {c} {cy+s}Q{c-1.6} {cy+1.6} {c-s} {cy}Q{c-1.6} {cy-1.6} {c} {cy-s}Z" fill="{accent}"/>')
    write(f"divider-{name}.svg", svg(d, W, h, "", style, "".join(b), defs))


# ---------------------------------------------------------------- cards
def chips(d: Doc, items: list[str], x: float, y: float, accent: str) -> str:
    out = []
    for it in items:
        w = d.measure(it, 12, "mono", 500) + 26
        out.append(f'<rect x="{x}" y="{y}" width="{w:.1f}" height="30" rx="15" fill="rgba(255,255,255,.03)" stroke="rgba(255,255,255,.14)"/>')
        out.append(d.text(it, x + 13, y + 19.5, 12, "mono", 500, fill="#C9CED6"))
        x += w + 8
    return "".join(out)


def card(name: str, idx: str, kicker: str, title: str, zh: str, en: str, tech: list[str], accent: str,
         art: str, art_style: str, art_defs: str = "", d: Doc | None = None) -> None:
    h = 380
    d = d or Doc("c")
    defs, body = panel(h, accent, 1010, 190, 560, 0.17)
    b = [body]
    b.append(d.text(f"{idx} · {kicker}", 58, 74, 12, "mono", 600, fill=accent, tracking=0.2))
    b.append(d.text(title, 56, 146, 60, "serif", fill=INK))
    b.append(d.text(zh, 58, 206, 26, "cjk", 600, fill=INK))
    b.append(d.text(en, 58, 244, 19, "serif-it", fill="#A7AEBA"))
    b.append(chips(d, tech, 58, 280, accent))
    b.append(d.text(f"github.com/ShmilyXI/{title}  →", 58, 346, 11, "mono", 400, fill=DIM, tracking=0.06))
    # art frame
    b.append('<rect x="716" y="28" width="548" height="324" rx="14" fill="rgba(255,255,255,.018)" stroke="rgba(255,255,255,.07)"/>')
    b.append(f'<g transform="translate(725 30)">{art}</g>')
    write(f"card-{name}.svg", svg(d, W, h, f"{title}：{zh}", art_style, "".join(b), defs + art_defs))


def card_plush() -> None:
    d = Doc("c")
    acc = "#FF9F6E"
    st = (
        "@keyframes br{0%,100%{transform:scale(1)}50%{transform:scale(1.022)}}"
        ".br{transform-box:fill-box;transform-origin:50% 100%;animation:br 4s ease-in-out infinite}"
        "@keyframes bl{0%,92%,100%{transform:scaleY(1)}95%{transform:scaleY(.1)}}"
        ".bl{transform-box:fill-box;transform-origin:center;animation:bl 5s infinite}"
        "@keyframes wv{0%,100%{transform:scaleY(.25)}50%{transform:scaleY(1)}}"
        ".wv{transform-box:fill-box;transform-origin:center;animation:wv 1.1s ease-in-out infinite}"
        "@keyframes hb{0%,100%{opacity:.55;transform:scale(1)}15%{opacity:1;transform:scale(1.25)}30%{opacity:.8;transform:scale(1)}}"
        ".hb{transform-box:fill-box;transform-origin:center;animation:hb 1.6s ease-in-out infinite}"
        "@keyframes fl{to{stroke-dashoffset:-24}}.fl{animation:fl 1s linear infinite}"
        "@keyframes pop{0%,30%{opacity:0;transform:translateY(6px)}40%,92%{opacity:1;transform:translateY(0)}100%{opacity:0}}"
        ".pop{animation:pop 6s ease-out infinite}"
    )
    a = []
    bx, by = 150, 0
    a.append('<g class="br">')
    a.append(f'<circle cx="{bx-56}" cy="88" r="29" fill="#EDAA80"/><circle cx="{bx-56}" cy="88" r="15" fill="#D98A62"/>')
    a.append(f'<circle cx="{bx+56}" cy="88" r="29" fill="#EDAA80"/><circle cx="{bx+56}" cy="88" r="15" fill="#D98A62"/>')
    a.append(f'<ellipse cx="{bx}" cy="258" rx="66" ry="56" fill="#EDAA80"/><ellipse cx="{bx}" cy="266" rx="38" ry="32" fill="#FBE3CF"/>')
    a.append(f'<ellipse cx="{bx-62}" cy="236" rx="18" ry="24" fill="#E39C72" transform="rotate(28 {bx-62} 236)"/>')
    a.append(f'<ellipse cx="{bx+62}" cy="236" rx="18" ry="24" fill="#E39C72" transform="rotate(-28 {bx+62} 236)"/>')
    a.append(f'<circle cx="{bx}" cy="142" r="74" fill="#F5C09A"/>')
    a.append(f'<ellipse cx="{bx}" cy="170" rx="32" ry="24" fill="#FBE3CF"/>')
    a.append(f'<ellipse cx="{bx}" cy="159" rx="9.5" ry="6.5" fill="#4A2A1C"/>')
    a.append(f'<path d="M{bx-9} 176Q{bx} 184 {bx+9} 176" stroke="#4A2A1C" stroke-width="2.4" fill="none" stroke-linecap="round"/>')
    a.append(f'<circle class="bl" cx="{bx-27}" cy="132" r="6.5" fill="#2A1810"/><circle class="bl" cx="{bx+27}" cy="132" r="6.5" fill="#2A1810"/>')
    a.append(f'<circle cx="{bx-46}" cy="160" r="10" fill="#FF8A78" opacity=".45"/><circle cx="{bx+46}" cy="160" r="10" fill="#FF8A78" opacity=".45"/>')
    hx, hy = bx, 262
    a.append(f'<path class="hb" d="M{hx} {hy+9}C{hx-15} {hy} {hx-14} {hy-10} {hx-7} {hy-10}C{hx-3} {hy-10} {hx} {hy-6} {hx} {hy-4}C{hx} {hy-6} {hx+3} {hy-10} {hx+7} {hy-10}C{hx+14} {hy-10} {hx+15} {hy} {hx} {hy+9}Z" fill="{acc}"/>')
    a.append("</g>")
    # listening bubble
    x0, y0 = 288, 62
    a.append(d.text("● LISTENING", x0 + 2, y0 - 12, 10.5, "mono", 600, fill=acc, tracking=0.16))
    a.append(f'<rect x="{x0}" y="{y0}" width="226" height="78" rx="18" fill="rgba(255,255,255,.05)" stroke="{acc}" stroke-opacity=".45"/>')
    a.append(f'<path d="M{x0+2} {y0+52}L{x0-14} {y0+66}L{x0+10} {y0+60}" fill="rgba(255,255,255,.05)" stroke="{acc}" stroke-opacity=".45"/>')
    for i in range(19):
        hgt = 10 + 26 * abs(math.sin(i * 0.9 + 0.4))
        a.append(f'<rect class="wv" style="animation-delay:{-i*0.11:.2f}s" x="{x0+22+i*10.2:.1f}" y="{y0+39-hgt/2:.1f}" width="4.4" height="{hgt:.1f}" rx="2.2" fill="{acc}"/>')
    # reply bubble
    y1 = 166
    a.append('<g class="pop">')
    a.append(f'<rect x="{x0+30}" y="{y1}" width="196" height="50" rx="16" fill="{acc}" fill-opacity=".14" stroke="{acc}" stroke-opacity=".35"/>')
    a.append(d.text("今天也辛苦啦，抱一下？", x0 + 46, y1 + 31, 16, "serif", 500, fill=INK))
    a.append("</g>")
    # pipeline
    py = 262
    xs = [(x0 - 4, "ESP32"), (x0 + 84, "MQTT"), (x0 + 166, "LLM")]
    for i, (px, lab) in enumerate(xs):
        w = 64
        a.append(f'<rect x="{px}" y="{py}" width="{w}" height="28" rx="7" fill="rgba(255,255,255,.04)" stroke="rgba(255,255,255,.16)"/>')
        a.append(d.text(lab, px + w / 2, py + 18.5, 11, "mono", 600, fill="#D5D9DF", anchor="middle"))
        if i < 2:
            a.append(f'<path class="fl" d="M{px+w+3} {py+14}H{xs[i+1][0]-3}" stroke="{acc}" stroke-width="2" stroke-dasharray="4 8" stroke-linecap="round"/>')
    a.append(d.text("voice · skills · MCP", x0 - 2, py + 54, 10.5, "mono", 400, fill=DIM, tracking=0.08))
    card("plush", "01", "AI HARDWARE", "ai-plush-companion",
         "把会听、会说、会记得你的心，缝进毛绒玩具。",
         "Sewing a heart that listens, talks and remembers into a plush toy.",
         ["ESP32", "Java", "Python", "MQTT", "MCP"], acc, "".join(a), st, d=d)


def catmull(pts: list[tuple[float, float]]) -> str:
    p = [pts[0]] + pts + [pts[-1]]
    s = f"M{p[1][0]} {p[1][1]}"
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        s += f"C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]} {p2[1]}"
    return s


def card_memory() -> None:
    d = Doc("c")
    acc = "#FF7A93"
    st = (
        "@keyframes ring{0%{transform:scale(1);opacity:.9}70%,100%{transform:scale(3);opacity:0}}"
        ".ring{transform-box:fill-box;transform-origin:center;opacity:0;animation:ring 8s ease-out infinite}"
        "@keyframes draw{0%{stroke-dashoffset:620}85%,100%{stroke-dashoffset:0}}"
        ".draw{stroke-dasharray:620;animation:draw 8s linear infinite}"
        "@keyframes sway{0%,100%{transform:rotate(var(--r))}50%{transform:rotate(calc(var(--r) + 2deg))}}"
        ".sway{transform-box:fill-box;transform-origin:50% 0;animation:sway 5s ease-in-out infinite}"
    )
    pts = [(6, 280), (92, 244), (208, 286), (326, 238), (444, 278), (530, 236)]
    path = catmull(pts)
    defs = (
        '<linearGradient id="ph0" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFB37A"/><stop offset="1" stop-color="#E4577B"/></linearGradient>'
        '<linearGradient id="ph1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8FD3FF"/><stop offset="1" stop-color="#2D6FB8"/></linearGradient>'
        '<linearGradient id="ph2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E9F1F7"/><stop offset="1" stop-color="#8AA3B8"/></linearGradient>'
        '<linearGradient id="ph3" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2B2A5A"/><stop offset="1" stop-color="#7A4C9C"/></linearGradient>'
        f'<radialGradient id="dg"><stop offset="0" stop-color="{acc}"/><stop offset="1" stop-color="{acc}" stop-opacity="0"/></radialGradient>'
    )
    a = [f'<path d="{path}" fill="none" stroke="rgba(255,255,255,.2)" stroke-width="2" stroke-dasharray="2 7" stroke-linecap="round"/>',
         f'<path class="draw" d="{path}" fill="none" stroke="{acc}" stroke-width="2.4" stroke-linecap="round" opacity=".85"/>']
    caps = [("2019.05", "初遇"), ("2021.10", "海边"), ("2023.02", "雪山"), ("2026.11", "现在")]
    rots = [-5, 3, -3, 5]
    for i, (px, py) in enumerate(pts[1:5]):
        top = 34 + (i % 2) * 18
        a.append(f'<path d="M{px} {top+112}V{py-8}" stroke="rgba(255,255,255,.22)" stroke-dasharray="2 4"/>')
        a.append(f'<g class="sway" style="--r:{rots[i]}deg;animation-delay:{-i*1.2}s"><g transform="translate({px-48} {top})">')
        a.append('<rect width="96" height="112" rx="4" fill="#F5F0E8"/>')
        a.append(f'<rect x="7" y="7" width="82" height="72" rx="2" fill="url(#ph{i})"/>')
        if i == 0:
            a.append('<circle cx="60" cy="34" r="11" fill="#FFE3A3"/><path d="M7 79L30 56L46 68L66 50L89 70V79Z" fill="#8E3B57" opacity=".7"/>')
        elif i == 1:
            a.append('<path d="M7 58Q27 52 48 58T89 58V79H7Z" fill="#1E4E86"/><circle cx="30" cy="28" r="8" fill="#FFF6D6"/>')
        elif i == 2:
            a.append('<path d="M7 79L34 38L50 58L64 42L89 79Z" fill="#5E7890"/><path d="M34 38L42 50L30 52Z M64 42L70 52L59 51Z" fill="#fff"/>')
        else:
            for sx, sy in [(20, 20), (44, 14), (70, 26), (30, 40), (78, 46), (56, 36)]:
                a.append(f'<circle cx="{sx}" cy="{sy}" r="1.4" fill="#fff"/>')
            a.append('<path d="M38 79Q48 56 58 79Z" fill="#20193F"/>')
        a.append(d.text(caps[i][0], 9, 98, 10, "mono", 600, fill="#3A3330"))
        a.append(d.text(caps[i][1], 87, 99, 11, "serif", 600, fill="#3A3330", anchor="end"))
        a.append("</g></g>")
        a.append(f'<circle cx="{px}" cy="{py}" r="5" fill="{BG}" stroke="{acc}" stroke-width="2"/>')
        a.append(f'<circle class="ring" style="animation-delay:{0.9 + i*1.6:.1f}s" cx="{px}" cy="{py}" r="5" fill="none" stroke="{acc}" stroke-width="1.5"/>')
    a.append(f'<g><circle r="14" fill="url(#dg)"/><circle r="4.5" fill="#fff"/>'
             f'<animateMotion dur="8s" repeatCount="indefinite" keyPoints="0;1;1" keyTimes="0;.85;1" calcMode="linear" path="{path}"/></g>')
    card("memory", "02", "CLAUDE SKILL", "memory-website-builder",
         "把相册里散落的日子，串成一条能走回去的路。",
         "Stringing the days in your camera roll into a path you can walk back along.",
         ["Claude Skill", "JavaScript", "Static site"], acc, "".join(a), st, defs, d=d)


def card_agents() -> None:
    d = Doc("c")
    acc = "#8B7CFF"
    st = (
        "@keyframes pl{from{stroke-dashoffset:0}to{stroke-dashoffset:-260}}"
        ".pl{stroke-dasharray:14 246;animation:pl 2.6s linear infinite}"
        "@keyframes on{0%,100%{opacity:.35}50%{opacity:1}}.on{animation:on 1.6s ease-in-out infinite}"
        "@keyframes tk{0%,30%{transform:translateY(0)}33%,63%{transform:translateY(-22px)}66%,96%{transform:translateY(-44px)}100%{transform:translateY(-66px)}}"
        ".tk{animation:tk 9s cubic-bezier(.6,0,.2,1) infinite}"
    )
    def pill(cx, cy, w, label, main=False):
        h = 34 if main else 30
        x, y = cx - w / 2, cy - h / 2
        fill = f'{acc}" fill-opacity=".18' if main else "rgba(255,255,255,.04)"
        s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="{fill}" stroke="{acc if main else "rgba(255,255,255,.16)"}" stroke-opacity="{.7 if main else 1}"/>'
        s += f'<circle class="on" style="animation-delay:{-(cx % 7)/5:.2f}s" cx="{x+15}" cy="{cy}" r="3.5" fill="#3DDC97"/>'
        s += d.text(label, x + 26, cy + 4, 11.5 if not main else 12.5, "mono", 600, fill=INK if main else "#C9CED6")
        return s
    root = (265, 50)
    mids = [(100, 132, "cto"), (265, 132, "growth"), (430, 132, "design")]
    leaves = [(40, 212, "coder", 0), (150, 212, "qa", 0), (265, 212, "writer", 1), (380, 212, "ads", 1), (490, 212, "ui", 2)]
    a = []
    edges = []
    for mx, my, _ in mids:
        edges.append(f"M{root[0]} {root[1]+17}V91H{mx}V{my-15}")
    for lx, ly, _, p in leaves:
        mx, my, _ = mids[p]
        edges.append(f"M{mx} {my+15}V172H{lx}V{ly-15}")
    for i, e in enumerate(edges):
        a.append(f'<path d="{e}" fill="none" stroke="rgba(255,255,255,.16)" stroke-width="1.5"/>')
        a.append(f'<path class="pl" style="animation-delay:{-i*0.37:.2f}s" d="{e}" fill="none" stroke="{acc}" stroke-width="2.4" stroke-linecap="round"/>')
    a.append(pill(root[0], root[1], 150, "you · CEO", True))
    for mx, my, lab in mids:
        a.append(pill(mx, my, 118, lab + " agent"))
    for lx, ly, lab, _ in leaves:
        a.append(pill(lx, ly, 86, lab))
    # ticker
    a.append('<clipPath id="tc"><rect x="0" y="262" width="530" height="22"/></clipPath>')
    lines = ["> heartbeat ok · agents on duty", "> ticket assigned → coder agent", "> review passed · shipping", "> heartbeat ok · agents on duty"]
    a.append('<g clip-path="url(#tc)"><g class="tk">')
    for i, ln in enumerate(lines):
        a.append(d.text(ln, 10, 278 + i * 22, 12, "mono", 500, fill="#9AA1AD"))
    a.append("</g></g>")
    a.append(f'<rect x="0" y="263" width="2" height="20" fill="{acc}"/>')
    card("agents", "03", "ONE-PERSON COMPANY", "paperclip",
         "一个人的公司，一支不下班的 AI 团队。",
         "A one-person company, run by an AI team that never clocks out.",
         ["TypeScript", "AI Agents", "Fork · 300+ commits"], acc, "".join(a), st, d=d)


def card_bazi() -> None:
    d = Doc("c")
    acc = "#E2553D"
    gold = "#D9B36C"
    st = (
        "@keyframes rot{to{transform:rotate(360deg)}}"
        ".rot{transform-box:fill-box;transform-origin:center;animation:rot 80s linear infinite}"
        ".rot2{transform-box:fill-box;transform-origin:center;animation:rot 12s linear infinite reverse}"
        "@keyframes gl{0%,100%{opacity:.78}50%{opacity:1}}.gl{animation:gl 3s ease-in-out infinite}"
        "@keyframes ln{0%{stroke-dashoffset:420}60%,100%{stroke-dashoffset:0}}.ln{stroke-dasharray:420;animation:ln 6s ease-out infinite}"
    )
    cx, cy, R = 135, 160, 118
    a = [f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="rgba(255,255,255,.1)"/>',
         f'<circle cx="{cx}" cy="{cy}" r="{R-34}" fill="none" stroke="rgba(255,255,255,.08)"/>']
    ring = ['<g class="rot">']
    for k in range(60):
        ang = k * 6 * math.pi / 180
        r1, r2 = (R - 6, R) if k % 5 else (R - 12, R)
        ring.append(f'<path d="M{cx+r1*math.sin(ang):.1f} {cy-r1*math.cos(ang):.1f}L{cx+r2*math.sin(ang):.1f} {cy-r2*math.cos(ang):.1f}" stroke="{gold}" stroke-opacity="{.6 if k%5==0 else .25}"/>')
    for k, ch in enumerate("甲乙丙丁戊己庚辛壬癸"):
        ang = k * 36 * math.pi / 180
        rr = R - 25
        tx, ty = cx + rr * math.sin(ang), cy - rr * math.cos(ang)
        ring.append(f'<g transform="rotate({k*36} {tx:.1f} {ty:.1f})">' + d.text(ch, tx, ty + 5.5, 15, "serif", 500, fill=gold, anchor="middle") + "</g>")
    ring.append("</g>")
    a += ring
    r = 30
    a.append(f'<g class="rot2"><circle cx="{cx}" cy="{cy}" r="{r}" fill="#1A1B21" stroke="{gold}" stroke-opacity=".6"/>'
             f'<path d="M{cx} {cy-r}A{r} {r} 0 0 1 {cx} {cy+r}A{r/2} {r/2} 0 0 1 {cx} {cy}A{r/2} {r/2} 0 0 0 {cx} {cy-r}Z" fill="{gold}" fill-opacity=".85"/>'
             f'<circle cx="{cx}" cy="{cy-r/2}" r="4.5" fill="{gold}"/><circle cx="{cx}" cy="{cy+r/2}" r="4.5" fill="#1A1B21"/></g>')
    # four pillars
    el = {"木": "#5FBF7F", "火": "#E8604A", "土": "#C9A063", "金": "#EFE2B8", "水": "#5AA9E6"}
    pillars = [("年", "甲", "木", "辰", "土"), ("月", "丙", "火", "子", "水"), ("日", "庚", "金", "午", "火"), ("时", "壬", "水", "寅", "木")]
    px0 = 296
    for i, (lab, s1, e1, s2, e2) in enumerate(pillars):
        x = px0 + i * 58
        a.append(d.text(lab + "柱", x + 24, 30, 12, "serif", 500, fill=MUTED, anchor="middle"))
        a.append(f'<rect x="{x}" y="42" width="48" height="128" rx="10" fill="rgba(255,255,255,.035)" stroke="rgba(255,255,255,.08)"/>')
        a.append(f'<g class="gl" style="animation-delay:{-i*0.7:.1f}s">' + d.text(s1, x + 24, 92, 32, "serif", 700, fill=el[e1], anchor="middle")
                 + d.text(s2, x + 24, 150, 32, "serif", 700, fill=el[e2], anchor="middle") + "</g>")
    # trend line
    ys = [262, 248, 254, 226, 236, 214, 222, 200, 210, 194]
    pts = [(px0 + i * 24.5, y) for i, y in enumerate(ys)]
    pl = "M" + "L".join(f"{x:.1f} {y}" for x, y in pts)
    a.append(f'<path d="M{px0} 278H{px0+226}" stroke="rgba(255,255,255,.12)"/>')
    a.append(f'<path class="ln" d="{pl}" fill="none" stroke="{acc}" stroke-width="2.2" stroke-linejoin="round"/>')
    for x, y in pts:
        a.append(f'<circle cx="{x:.1f}" cy="{y}" r="2.6" fill="{BG}" stroke="{acc}" stroke-width="1.6"/>')
    a.append(d.text("大运 · 流年", px0, 300, 11, "serif", 500, fill=DIM))
    card("bazi", "04", "FULL-STACK", "ai-links",
         "把出生那一刻的天干地支，排成看得懂的命盘。",
         "Turning the stems and branches of a birth moment into a chart you can read.",
         ["React", "ECharts", "Express", "tyme4ts", "Alipay"], acc, "".join(a), st, d=d)


def footer() -> None:
    h = 176
    d = Doc("f")
    defs, body = panel(h, GOLD, 650, 0, 600, 0.12)
    st = ("@keyframes tw{0%,100%{transform:scale(.7) rotate(0);opacity:.6}50%{transform:scale(1.15) rotate(45deg);opacity:1}}"
          ".tw{transform-box:fill-box;transform-origin:center;animation:tw 2.4s ease-in-out infinite}")
    b = [body]
    zh = "做东西的人最开心的，是知道有人在看。"
    b.append(d.text(zh, 650, 78, 26, "serif", 600, fill=INK, anchor="middle"))
    b.append(d.text("Makers are happiest knowing someone is watching. Leave a star, so I know you stopped by.", 650, 114, 19, "serif-it", fill="#A7AEBA", anchor="middle"))
    lab = "S-XIAO  ·  @SHMILYXI  ·  2026"
    b.append(d.text(lab, 650, 150, 11, "mono", 500, fill=DIM, anchor="middle", tracking=0.2))
    wl = d.measure(lab, 11, "mono", 500, 0.2)
    for sx, delay in [(650 - wl / 2 - 24, 0), (650 + wl / 2 + 24, -1.2)]:
        s = 7
        b.append(f'<path class="tw" style="animation-delay:{delay}s" d="M{sx} {146-s}Q{sx+1.2} {146-1.2} {sx+s} 146Q{sx+1.2} {146+1.2} {sx} {146+s}Q{sx-1.2} {146+1.2} {sx-s} 146Q{sx-1.2} {146-1.2} {sx} {146-s}Z" fill="{GOLD}"/>')
    write("footer.svg", svg(d, W, h, "做东西的人最开心的，是知道有人在看。Leave a star, so I know you stopped by.", st, "".join(b), defs))


if __name__ == "__main__":
    header()
    for n, acc, g in [("plush", "#FF9F6E", "heart"), ("memory", "#FF7A93", "pin"), ("agents", "#8B7CFF", "nodes"),
                      ("bazi", "#E2553D", "taiji"), ("end", GOLD, "star")]:
        divider(n, acc, g)
    card_plush()
    card_memory()
    card_agents()
    card_bazi()
    footer()
