#!/usr/bin/env python3
"""The World in One Page -- 22 November 2026.

Draws a one-page newspaper front page summing up the world's news of
Sunday 22 November 2026, and writes it to /output/entry.png
(or $MAKEFUN_OUTPUT_DIR/entry.png).

Deterministic: no network, no randomness, no timestamps in the image.
If Pillow is unavailable, falls back to copying the bundled artwork.png
(byte-identical to what this program draws with Pillow).

Stories (all reported 21-22 November 2026, AP / Reuters / BBC / CNN /
The Economist):
  Hero. Iran strikes a U.S. air base in Kuwait and targets Bahrain; a
    tanker burns in the Strait of Hormuz -- one ADNOC crewman missing,
    11 hurt. Trump says he wants a "permanent" deal to stop Iran ever
    getting a nuclear weapon.
  1. Tech rout deepens: Nasdaq -5.28%, S&P -3.7% into correction;
     Nvidia -14%, Anthropic -8.5% on its second day.
  2. M6.9 earthquake shakes Peru's Andes (Junin), felt in Lima; no
     casualties reported.
  3. Zelensky calls the Crimea bridge strikes a "fair response" to
     109 Russian attacks on Ukrainian bridges.
  4. FBI most-wanted cartel boss "El Chapo Isidro" captured in
     Sinaloa; 11 dead, incl. 4 soldiers.
  5. Ex-president Bolsonaro in intensive care with an acute bowel
     obstruction; stable and conscious.
  6. COP31 climate talks spill into overtime, deadlocked over
     fossil fuels and finance.
"""

import math
import os
import shutil
import sys

W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (26, 26, 26)
NAVY = (22, 40, 63)
NAVY2 = (31, 55, 84)
RED = (179, 39, 30)
RED_LT = (255, 120, 100)
GOLD = (201, 162, 39)
GOLD_LT = (232, 193, 90)
GREY = (90, 90, 86)
WHITE = (255, 255, 255)
BLUE = (43, 96, 158)
SAND = (214, 196, 150)
SEA = (74, 116, 158)
DARK_ON_SAND = (60, 60, 60)


def _fonts_dir():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "fonts")


def load_font(name, size):
    """Load a bundled DejaVu font, else a system copy, else default."""
    from PIL import ImageFont

    cands = [
        os.path.join(_fonts_dir(), name),
        os.path.join("/usr/share/fonts/truetype/dejavu", name),
    ]
    for path in cands:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()


def wrap(draw, text, font, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_text_block(draw, x, y, lines, font, fill, leading=None):
    """Draw lines; returns y after the last line."""
    if leading is None:
        leading = int(font.size * 1.22)
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def draw_gulf_map(draw, box):
    """Schematic Persian Gulf: Iran north, Arabia south, Hormuz east."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=NAVY2, outline=INK, width=2)
    bw, bh = x1 - x0, y1 - y0
    # Land: Iran (top band) and Arabia (bottom band) in sand.
    draw.polygon([(x0, y0), (x1, y0), (x1, y0 + bh * 0.22),
                  (x0 + bw * 0.55, y0 + bh * 0.30),
                  (x0, y0 + bh * 0.34)], fill=SAND)
    draw.polygon([(x0, y0 + bh * 0.66), (x0 + bw * 0.42, y0 + bh * 0.58),
                  (x1, y0 + bh * 0.72), (x1, y1), (x0, y1)], fill=SAND)
    # The Gulf: diagonal sea channel.
    gulf = [(x0 + bw * 0.06, y0 + bh * 0.36),
            (x0 + bw * 0.55, y0 + bh * 0.30),
            (x1 - 6, y0 + bh * 0.24),
            (x1 - 6, y0 + bh * 0.52),
            (x0 + bw * 0.60, y0 + bh * 0.55),
            (x0 + bw * 0.42, y0 + bh * 0.62),
            (x0 + bw * 0.10, y0 + bh * 0.58)]
    draw.polygon(gulf, fill=SEA)
    # Strait of Hormuz pinch, far right.
    draw.polygon([(x1 - 60, y0 + bh * 0.24), (x1 - 6, y0 + bh * 0.24),
                  (x1 - 6, y0 + bh * 0.52), (x1 - 60, y0 + bh * 0.44)],
                 fill=(52, 88, 128))
    draw.text((x0 + 12, y0 + 8), "IRAN", font=FONT_SMB, fill=DARK_ON_SAND)
    draw.text((x0 + 12, y1 - 26), "SAUDI ARABIA", font=FONT_SMB,
              fill=DARK_ON_SAND)
    # Markers: Kuwait, Bahrain, Qeshm, Hormuz. Labels sit inside the box.
    marks = [
        (0.20, 0.44, "KUWAIT", RED, 1),
        (0.38, 0.50, "BAHRAIN", RED, 1),
        (0.74, 0.34, "QESHM", GOLD_LT, 1),
        (0.88, 0.44, "HORMUZ", GOLD_LT, -1),
    ]
    for fx, fy, label, col, side in marks:
        px, py = x0 + fx * bw, y0 + fy * bh
        draw.ellipse([px - 7, py - 7, px + 7, py + 7], fill=col,
                     outline=WHITE, width=2)
        lw = draw.textlength(label, font=FONT_SM)
        if side > 0:
            draw.text((px + 10, py - 8), label, font=FONT_SM, fill=WHITE)
        else:
            draw.text((px - 10 - lw, py - 8), label, font=FONT_SM,
                      fill=WHITE)
    # Tanker glyph near Hormuz.
    tx, ty = x0 + bw * 0.60, y0 + bh * 0.46
    draw.rectangle([tx - 16, ty - 5, tx + 16, ty + 5],
                   fill=(200, 200, 200), outline=INK)
    draw.rectangle([tx + 6, ty - 11, tx + 12, ty - 5],
                   fill=(200, 200, 200), outline=INK)
    draw.text((tx - 24, ty + 10), "TANKER HIT", font=FONT_SM, fill=RED_LT)
    draw.text((x0 + 12, y0 + bh * 0.50), "PERSIAN GULF", font=FONT_SMB,
              fill=(190, 205, 220))
    draw.text((x0 + 12, y1 - 48), "1 CREW MISSING \u00b7 11 HURT",
              font=FONT_SM, fill=DARK_ON_SAND)


def draw_market_chart(draw, box):
    """Small red plunging line chart inside a panel box."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=WHITE, outline=(200, 200, 195))
    pts = [(0.06, 0.62), (0.16, 0.66), (0.26, 0.60), (0.36, 0.72),
           (0.46, 0.68), (0.56, 0.82), (0.66, 0.78), (0.76, 0.90),
           (0.86, 0.88), (0.95, 0.97)]
    xy = [(x0 + px * (x1 - x0), y0 + py * (y1 - y0)) for px, py in pts]
    draw.line(xy, fill=RED, width=3, joint="curve")
    draw.ellipse([xy[-1][0] - 4, xy[-1][1] - 4, xy[-1][0] + 4, xy[-1][1] + 4],
                 fill=RED)
    label = "NASDAQ -5.28%  \u00b7  NVIDIA -14%"
    lw = draw.textlength(label, font=FONT_SMB)
    draw.rectangle([x0 + 4, y0 + 3, x0 + lw + 12, y0 + 22], fill=WHITE)
    draw.text((x0 + 8, y0 + 4), label, font=FONT_SMB, fill=RED)


def draw_quake(draw, cx, cy, r):
    """Epicentre dot with radiating arcs and a ground line."""
    for rr in (r * 0.4, r * 0.7, r * 1.0):
        draw.arc([cx - rr, cy - rr, cx + rr, cy + rr], start=-50, end=50,
                 fill=RED, width=3)
    draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=RED)
    draw.line([(cx - r - 14, cy + r * 0.55), (cx + r + 14, cy + r * 0.55)],
              fill=INK, width=3)


def draw_bridge(draw, x, y, w, h):
    """Collapsed bridge: two piers, broken deck, gap in the middle."""
    draw.line([(x, y + h), (x, y + h * 0.3)], fill=NAVY, width=5)
    draw.line([(x + w, y + h), (x + w, y + h * 0.3)], fill=NAVY, width=5)
    draw.line([(x, y + h * 0.3), (x + w * 0.42, y + h * 0.3)], fill=NAVY,
              width=4)
    draw.line([(x + w * 0.58, y + h * 0.3), (x + w, y + h * 0.3)],
              fill=NAVY, width=4)
    draw.line([(x + w * 0.42, y + h * 0.3), (x + w * 0.50, y + h * 0.75)],
              fill=RED, width=4)
    draw.line([(x + w * 0.58, y + h * 0.3), (x + w * 0.50, y + h * 0.75)],
              fill=RED, width=4)


def draw_badge(draw, cx, cy, r):
    """Gold star badge for the cartel-boss capture."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD, outline=NAVY,
                 width=2)
    pts = []
    for i in range(10):
        ang = math.pi * i / 5 - math.pi / 2
        rr = r * 0.55 if i % 2 else r * 0.85
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    draw.polygon(pts, fill=WHITE)


def draw_cross(draw, cx, cy, s):
    """Red cross in a ring for the ICU story."""
    draw.ellipse([cx - s, cy - s, cx + s, cy + s], fill=WHITE,
                 outline=NAVY, width=2)
    draw.rectangle([cx - s * 0.18, cy - s * 0.6, cx + s * 0.18,
                    cy + s * 0.6], fill=RED)
    draw.rectangle([cx - s * 0.6, cy - s * 0.18, cx + s * 0.6,
                    cy + s * 0.18], fill=RED)


def draw_globe(draw, cx, cy, r):
    """Small globe with a red deadlock slash."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 180, 210),
                 outline=NAVY, width=2)
    draw.ellipse([cx - r * 0.55, cy - r * 0.6, cx - r * 0.05, cy - r * 0.1],
                 fill=(90, 160, 90))
    draw.ellipse([cx + r * 0.1, cy + r * 0.15, cx + r * 0.6, cy + r * 0.6],
                 fill=(90, 160, 90))
    draw.line([(cx - r, cy + r), (cx + r, cy - r)], fill=RED, width=4)


# (kicker, headline lines, body, glyph kind)
PANELS = [
    ("MARKETS", ["TECH ROUT", "DEEPENS"],
     "Nasdaq -5.28%, S&P -3.7% into correction.",
     "chart"),
    ("EARTHQUAKE  \u00b7  PERU", ["ANDES", "SHAKEN"],
     "M6.9 quake strikes Junin, felt in Lima. No casualties reported.",
     "quake"),
    ("UKRAINE", ["BRIDGE 'FAIR", "RESPONSE'"],
     "Zelensky defends Crimea bridge strikes as 'fair response' to "
     "109 Russian attacks.",
     "bridge"),
    ("MEXICO", ["'CHAPO ISIDRO'", "SEIZED"],
     "FBI most-wanted cartel boss seized in Sinaloa; 11 dead, 4 soldiers.",
     "badge"),
    ("BRAZIL", ["BOLSONARO", "IN ICU"],
     "Ex-president in ICU with acute bowel obstruction. Stable, conscious.",
     "cross"),
    ("CLIMATE  \u00b7  COP31", ["TALKS", "DEADLOCKED"],
     "Climate talks spill into overtime over fossil fuels and finance.",
     "globe"),
]


def build_image():
    from PIL import Image, ImageDraw

    global FONT_SM, FONT_SMB, FONT_MD, FONT_BODY, FONT_HEAD, FONT_TITLE
    global FONT_KICK, FONT_DATE, FONT_HEADSM

    FONT_SM = load_font("DejaVuSans.ttf", 15)
    FONT_SMB = load_font("DejaVuSans-Bold.ttf", 16)
    FONT_MD = load_font("DejaVuSans-Bold.ttf", 20)
    FONT_BODY = load_font("DejaVuSans.ttf", 18)
    FONT_HEAD = load_font("DejaVuSerif-Bold.ttf", 34)
    FONT_HEADSM = load_font("DejaVuSerif-Bold.ttf", 28)
    FONT_TITLE = load_font("DejaVuSerif-Bold.ttf", 52)
    FONT_KICK = load_font("DejaVuSans-Bold.ttf", 17)
    FONT_DATE = load_font("DejaVuSans-Bold.ttf", 20)

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 28  # margin

    # ---- Masthead ----
    d.rectangle([0, 0, W, 118], fill=NAVY)
    title = "THE WORLD IN ONE PAGE"
    tw = d.textlength(title, font=FONT_TITLE)
    d.text(((W - tw) / 2, 14), title, font=FONT_TITLE, fill=WHITE)
    d.rectangle([M, 82, W - M, 84], fill=GOLD)
    date_line = ("SUNDAY, 22 NOVEMBER 2026  \u00b7  THE DAY'S WORLD NEWS "
                 "IN ONE IMAGE")
    tw = d.textlength(date_line, font=FONT_DATE)
    d.text(((W - tw) / 2, 90), date_line, font=FONT_DATE, fill=GOLD_LT)

    # ---- Hero: headline-dominant, Gulf map strip below ----
    y = 132
    d.rectangle([M, y, W - M, y + 338], fill=NAVY, outline=INK, width=2)
    d.text((M + 14, y + 16), "LEAD  \u00b7  WAR IN THE GULF", font=FONT_KICK,
           fill=RED_LT)
    d.text((M + 14, y + 44), "GULF WAR WIDENS: IRAN HITS U.S. BASES",
           font=FONT_HEAD, fill=WHITE)
    d.text((M + 14, y + 86),
           "TRUMP SEEKS \u201cPERMANENT\u201d IRAN DEAL",
           font=FONT_HEAD, fill=WHITE)
    draw_gulf_map(d, (M + 14, y + 136, 560, y + 324))
    deck = ("Iran strikes a U.S. air base in Kuwait and targets Bahrain; "
            "a tanker burns in the Strait of Hormuz \u2014 one ADNOC "
            "crewman missing, 11 hurt. Trump says he wants a "
            "\u201cpermanent\u201d deal to stop Iran ever getting a "
            "nuclear weapon.")
    lines = wrap(d, deck, FONT_BODY, 400)
    draw_text_block(d, 584, y + 140, lines, FONT_BODY, (225, 232, 240))

    # ---- Panels: 3 x 2 ----
    y = 484
    pw, gap = 312, 16
    for i, (kick, head, body, glyph) in enumerate(PANELS):
        row, col = divmod(i, 3)
        x = M + col * (pw + gap)
        yy = y + row * 222
        d.rectangle([x, yy, x + pw, yy + 212], fill=WHITE, outline=INK,
                    width=2)
        d.text((x + 14, yy + 12), kick, font=FONT_KICK, fill=RED)
        hy = yy + 40
        for ln in head:
            d.text((x + 14, hy), ln, font=FONT_HEADSM, fill=INK)
            hy += 32
        by = yy + 40 + 32 * len(head) + 8
        if glyph == "chart":
            lines = wrap(d, body, FONT_BODY, pw - 28)
            draw_text_block(d, x + 14, by, lines, FONT_BODY, INK)
            draw_market_chart(d, (x + 14, yy + 162, x + pw - 14, yy + 200))
        elif glyph == "bridge":
            lines = wrap(d, body, FONT_BODY, pw - 28)
            draw_text_block(d, x + 14, by, lines, FONT_BODY, INK)
            draw_bridge(d, x + pw - 96, yy + 172, 82, 30)
        else:
            lines = wrap(d, body, FONT_BODY, pw - 100)
            draw_text_block(d, x + 14, by, lines, FONT_BODY, INK)
            gx, gy = x + pw - 48, yy + 132
            if glyph == "quake":
                draw_quake(d, gx, gy, 26)
            elif glyph == "badge":
                draw_badge(d, gx, gy, 26)
            elif glyph == "cross":
                draw_cross(d, gx, gy, 26)
            else:
                draw_globe(d, gx, gy, 26)

    # ---- Footer ticker ----
    y = 924
    d.rectangle([M, y, W - M, y + 46], fill=NAVY)
    tick = ("ALSO TODAY:  Estonia to shut its Russia border from 1 Dec  "
            "\u00b7  Drones hit a Russian cargo ship in the Baltic  \u00b7  "
            "Cyclone Akvan cancels flights in Ranchi  \u00b7  Modi opens "
            "Nitish Setu")
    tfont = FONT_SM
    while d.textlength(tick, font=tfont) > W - 2 * M - 16 and tfont.size > 11:
        tfont = load_font("DejaVuSans.ttf", tfont.size - 1)
    tw = d.textlength(tick, font=tfont)
    d.text(((W - tw) / 2, y + 14), tick, font=tfont, fill=WHITE)
    src = ("Reported 21\u201322 November 2026  \u00b7  Sources: AP, Reuters, "
           "BBC, CNN, The Economist")
    tw = d.textlength(src, font=FONT_SM)
    d.text(((W - tw) / 2, 984), src, font=FONT_SM, fill=GREY)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    try:
        from PIL import Image  # noqa: F401

        img = build_image()
        img.save(out_path, "PNG")
    except ImportError:
        here = os.path.dirname(os.path.abspath(__file__))
        bundled = os.path.join(here, "artwork.png")
        if not os.path.exists(bundled):
            sys.stderr.write("Pillow missing and no bundled artwork.png\n")
            raise
        shutil.copyfile(bundled, out_path)


if __name__ == "__main__":
    main()
