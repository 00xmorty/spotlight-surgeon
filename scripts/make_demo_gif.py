#!/usr/bin/env python3
"""Generate a safe, synthetic terminal demo GIF for Spotlight Surgeon.

No macOS repair commands are executed. The GIF is rendered from static transcript
frames so it is safe to regenerate on any machine with Pillow installed.
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "spotlight-surgeon-demo.gif"
W, H = 1280, 720
BG = (9, 11, 17)
PANEL = (17, 21, 32)
PANEL_2 = (25, 31, 45)
TEXT = (235, 241, 250)
MUTED = (143, 155, 179)
GREEN = (129, 201, 149)
BLUE = (138, 180, 248)
YELLOW = (253, 214, 99)
RED = (242, 139, 130)
PURPLE = (197, 138, 249)

TRANSCRIPT = [
    ("$ ./spotlight-surgeon doctor --dry-run", BLUE),
    ("Spotlight Surgeon v0.1.0 — doctor", TEXT),
    ("Spotlight Surgeon v0.1.0 — Spotlight status", TEXT),
    ("→ Check Spotlight indexing status for root volume", GREEN),
    ("DRY RUN: mdutil -s /", YELLOW),
    ("", TEXT),
    ("Spotlight Surgeon v0.1.0 — verify app search: Safari", TEXT),
    ("→ Search Spotlight application metadata for Safari", GREEN),
    ("DRY RUN: mdfind \"kMDItemKind == 'Application' && kMDItemDisplayName == '*Safari*'\"", YELLOW),
    ("", TEXT),
    ("LaunchServices tool found: /System/Library/.../lsregister", MUTED),
    ("", TEXT),
    ("$ ./spotlight-surgeon apps --dry-run", BLUE),
    ("Spotlight Surgeon v0.1.0 — LaunchServices app registry repair", TEXT),
    ("This rebuilds macOS LaunchServices app registration.", MUTED),
    ("→ Rebuild LaunchServices registry", GREEN),
    ("DRY RUN: .../lsregister -kill -r -domain local -domain system -domain user", YELLOW),
    ("", TEXT),
    ("$ ./spotlight-surgeon fix --dry-run", BLUE),
    ("Spotlight Surgeon v0.1.0 — Spotlight reindex repair", TEXT),
    ("This asks Spotlight to erase and rebuild the index for /.", MUTED),
    ("It does not delete user files.", GREEN),
    ("→ Erase/rebuild Spotlight index for root volume", GREEN),
    ("DRY RUN: mdutil -E /", YELLOW),
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/SFNSMono.ttf",
        "/System/Library/Fonts/Menlo.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for p in candidates:
        try:
            return ImageFont.truetype(p, size=size, index=0)
        except Exception:
            pass
    return ImageFont.load_default()

TITLE = font(42)
SUB = font(22)
MONO = font(25)
SMALL = font(18)


def round_rect(draw: ImageDraw.ImageDraw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def draw_frame(visible_lines: int, partial: str = "", cursor: bool = True) -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # soft background orbs
    d.ellipse((-170, -180, 410, 360), fill=(24, 54, 98))
    d.ellipse((900, -150, 1430, 300), fill=(58, 34, 91))
    d.ellipse((840, 520, 1380, 980), fill=(25, 74, 82))

    # top label
    d.text((70, 50), "Spotlight Surgeon", font=TITLE, fill=TEXT)
    d.text((72, 104), "safe macOS Spotlight app-search repair helper", font=SUB, fill=MUTED)

    # right safety stack
    round_rect(d, (890, 68, 1195, 176), 24, PANEL, (54, 64, 84), 1)
    d.text((918, 92), "Safety model", font=SUB, fill=TEXT)
    d.text((918, 128), "dry-run first · explains commands", font=SMALL, fill=GREEN)

    # terminal window
    x0, y0, x1, y1 = 70, 205, 1210, 650
    round_rect(d, (x0, y0, x1, y1), 28, PANEL, (54, 64, 84), 1)
    d.rounded_rectangle((x0, y0, x1, y0 + 54), radius=28, fill=PANEL_2)
    for i, c in enumerate([RED, YELLOW, GREEN]):
        d.ellipse((x0 + 24 + i * 28, y0 + 20, x0 + 38 + i * 28, y0 + 34), fill=c)
    d.text((x0 + 120, y0 + 18), "~/spotlight-surgeon", font=SMALL, fill=MUTED)

    y = y0 + 78
    line_h = 29
    for line, color in TRANSCRIPT[:visible_lines]:
        d.text((x0 + 28, y), line, font=MONO, fill=color)
        y += line_h
    if partial:
        d.text((x0 + 28, y), partial + ("▌" if cursor else ""), font=MONO, fill=BLUE)

    # footer badges
    badges = [("no files deleted", GREEN), ("native macOS tools", BLUE), ("transparent repair", PURPLE)]
    bx = 70
    for text, col in badges:
        tw = d.textlength(text, font=SMALL)
        round_rect(d, (bx, 664, bx + tw + 30, 700), 18, (16, 21, 31), (70, 83, 110), 1)
        d.text((bx + 15, 672), text, font=SMALL, fill=col)
        bx += int(tw) + 44

    return img


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    frames: list[Image.Image] = []
    durations: list[int] = []

    visible = 0
    # type first prompt
    first = TRANSCRIPT[0][0]
    for n in range(1, len(first) + 1, 2):
        frames.append(draw_frame(0, first[:n], cursor=True))
        durations.append(28)
    frames.append(draw_frame(1)); durations.append(650)
    visible = 1

    # reveal transcript in digestible chunks
    for i in range(1, len(TRANSCRIPT)):
        frames.append(draw_frame(i + 1)); durations.append(170 if TRANSCRIPT[i][0] else 70)
        if i in {10, 16, 23}:
            frames.append(draw_frame(i + 1)); durations.append(900)

    # final hold
    frames.append(draw_frame(len(TRANSCRIPT), cursor=False)); durations.append(1800)

    frames[0].save(
        OUT,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(OUT)
    print(f"frames={len(frames)} bytes={OUT.stat().st_size}")


if __name__ == "__main__":
    main()
