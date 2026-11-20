#!/usr/bin/env python3
"""Compose the 1024x1024 front-page image for news-image-20261119.
Deterministic: same inputs -> same PNG bytes (PIL, no timestamps in PNG
beyond what PIL writes deterministically for a given image).
All text is drawn with vector fonts, so no garbled AI text.
Hero: assets/media-generation-hero-shenzhen-*.png (generated illustration).
"""
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
HERO = next((HERE / "assets").glob("media-generation-hero-shenzhen-*.png"))
OUT = HERE / "entry.png"

W = H = 1024
PAPER = (247, 243, 232)
INK = (20, 20, 20)
NAVY = (20, 33, 61)
RED = (178, 34, 34)
GOLD = (200, 160, 60)
CARD_BG = (255, 255, 255)
LINE = (200, 195, 180)

def font(name, size):
    return ImageFont.truetype(f"/usr/share/fonts/truetype/{name}", size)

F_MAST = font("liberation/LiberationSerif-Bold.ttf", 46)
F_DATE = font("liberation/LiberationSans-Bold.ttf", 20)
F_HEAD = font("liberation/LiberationSerif-Bold.ttf", 40)
F_SUB = font("liberation/LiberationSerif-Regular.ttf", 21)
F_TAG = font("liberation/LiberationSans-Bold.ttf", 15)
F_TITLE = font("liberation/LiberationSans-Bold.ttf", 20)
F_BODY = font("liberation/LiberationSans-Regular.ttf", 16)
F_FOOT = font("liberation/LiberationSans-Regular.ttf", 15)
F_FOOTB = font("liberation/LiberationSans-Bold.ttf", 15)

def wrap(draw, text, f, width):
    lines, cur = [], ""
    for word in text.split():
        t = f"{cur} {word}".strip()
        if draw.textlength(t, font=f) <= width:
            cur = t
        else:
            lines.append(cur); cur = word
    if cur:
        lines.append(cur)
    return lines

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# Masthead
d.rectangle([0, 0, W, 86], fill=NAVY)
d.text((32, 14), "THE WORLD IN ONE DAY", font=F_MAST, fill=(255, 255, 255))
d.text((32, 60), "THURSDAY, 19 NOVEMBER 2026", font=F_DATE, fill=GOLD)
d.text((W - 32, 60), "ONE IMAGE  •  WORLD NEWS", font=F_DATE, fill=(255, 255, 255), anchor="ra")

# Hero: centre-crop to 1024 x 300
hero = Image.open(HERO).convert("RGB")
hw, hh = hero.size
target = 1024 / 300
if hw / hh > target:
    nw = int(hh * target); x0 = (hw - nw) // 2; hero = hero.crop((x0, 0, x0 + nw, hh))
else:
    nh = int(hw / target); y0 = (hh - nh) // 2; hero = hero.crop((0, y0, hw, y0 + nh))
hero = hero.resize((1024, 300))
img.paste(hero, (0, 86))
d.rectangle([0, 386, W, 390], fill=RED)

# Headline
y = 404
for line in wrap(d, "Three leaders, one table in Shenzhen", F_HEAD, W - 64):
    d.text((32, y), line, font=F_HEAD, fill=INK); y += 46
d.text((32, y + 4), "Trump, Xi and Putin issue a peace declaration —",
       font=F_SUB, fill=INK)
d.text((32, y + 30), "but it says nothing on Ukraine or Iran.",
       font=F_SUB, fill=INK)

# Cards: 2 cols x 3 rows
cards = [
    ("COURT", RED, "Myanmar guilty of Rohingya genocide",
     "UN court rules in the Gambia case.",
     "Judgment delivered on Thursday."),
    ("ENERGY", (150, 90, 0), "Tankers burn in the Strait of Hormuz",
     "Mines hit ships; 11 hurt, 1 missing.",
     "IEA: gravest threat yet to energy."),
    ("GAMES", (0, 110, 70), "GTA VI is out after 13 years",
     "Vice City returns; reviews 99 / 100.",
     "PS5 and Xbox; midnight launch."),
    ("MARKETS", (0, 80, 140), "Anthropic IPO raises $81bn",
     "Shares at $83 in a record debut.",
     "Nasdaq listing starts today."),
    ("CLIMATE", (0, 120, 120), "COP31 talks stall in Antalya",
     "Fossil fuels cut from draft deal.",
     "Ministers meet to unblock text."),
    ("ASIA", (120, 40, 140), "Bangladesh unrest spreads",
     "Yunus home burned; 28 districts hit.",
     "Paramilitary deployed amid unrest."),
]
cx0, cy0 = 32, 540
cw, ch, gap = 472, 128, 16
for i, (tag, colour, title, body, body2) in enumerate(cards):
    x = cx0 + (i % 2) * (cw + gap)
    yy = cy0 + (i // 2) * (ch + gap)
    d.rounded_rectangle([x, yy, x + cw, yy + ch], radius=8, fill=CARD_BG, outline=LINE, width=1)
    d.rectangle([x, yy, x + 6, yy + ch], fill=colour)
    d.text((x + 20, yy + 10), tag, font=F_TAG, fill=colour)
    ty = yy + 32
    for line in wrap(d, title, F_TITLE, cw - 36):
        d.text((x + 20, ty), line, font=F_TITLE, fill=INK); ty += 24
    d.text((x + 20, ty + 4), body, font=F_BODY, fill=(70, 70, 70))
    d.text((x + 20, ty + 26), body2, font=F_BODY, fill=(70, 70, 70))

# Footer strip: cards end at 540 + 3*128 + 2*16 = 956; 68 px left
fy = 956
d.rectangle([0, fy, W, H], fill=NAVY)
d.text((32, fy + 8), "ALSO:  Voyager 1 reaches one light-day  •  Van Gogh sells for $190.4m",
       font=F_FOOTB, fill=(255, 255, 255))
d.text((32, fy + 34), "Cyclone Akvan: 80,000 flee in Odisha  •  Crimea bridge hit again",
       font=F_FOOT, fill=(220, 220, 220))

img.save(OUT, format="PNG", optimize=True)
print(f"wrote {OUT} {img.size} {OUT.stat().st_size} bytes")
