#!/usr/bin/env python3
"""Regenerate Nexus page images from the source screenshot.

  assets/gallery-1920x1080.jpg    (16:9 downscale, gallery slot)
  assets/header-1300x372.jpg      (wide crop + title overlay, banner)

The source is the cockpit view of the nearby-system warp countdown from the
Forsaken update. Two framings come out of it:

  gallery  the whole frame, downscaled. Keeps the Initiating Warp readout,
           which is the point of the mod.
  header   a band cropped off the top, so the warp glow sits right of the
           title.

Usage: python3 assets/generate.py   (or: make assets)
Requires: Pillow (pip install Pillow). Typeface is vendored (see FONT).
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src", "gallery-nearby-warp.jpg")
GAL = os.path.join(HERE, "gallery-1920x1080.jpg")
HDR = os.path.join(HERE, "header-1300x372.jpg")

# In-game heading typeface, vendored (SIL OFL 1.1):
# https://github.com/NMSCD/No-Mans-Sky-Universal-Font
FONT = os.path.join(HERE, "fonts", "GeosansLight-NMS.ttf")

TITLE = "NEARBY WARP COUNTDOWN SKIP"
SUBTITLE = "Instant Warp"

# Header crop, in source pixels.
HDR_X = 0
HDR_Y = 300
HDR_W = 2133

# Header size in output pixels.
HDR_OUT_W = 1300
HDR_OUT_H = 372

# Title placement in the header.
TITLE_X = 48
TITLE_Y = 48
TITLE_SIZE = 42
SUBTITLE_SIZE = 28


def main():
    img = Image.open(SRC).convert("RGB")
    assert img.size[0] * 9 == img.size[1] * 16, f"source is not 16:9: {img.size}"
    assert img.size[0] >= HDR_W, f"source too narrow for the header crop: {img.size}"

    img.resize((1920, 1080), Image.LANCZOS).save(GAL, quality=92)
    print(f"wrote {GAL}")

    # The band height follows from the crop width, so the crop keeps the
    # banner aspect no matter how it is retuned.
    band_h = int(HDR_W * HDR_OUT_H / HDR_OUT_W)
    band = img.crop((HDR_X, HDR_Y, HDR_X + HDR_W, HDR_Y + band_h))
    band = band.resize((HDR_OUT_W, HDR_OUT_H), Image.LANCZOS)
    d = ImageDraw.Draw(band, "RGBA")
    # top-weighted gradient: Nexus overlays its own title bottom-left
    for y in range(HDR_OUT_H):
        a = int(150 * (1 - y / (HDR_OUT_H - 1)) ** 2)
        d.rectangle([0, y, HDR_OUT_W, y + 1], fill=(0, 0, 0, a))
    band = band.convert("RGB")
    d = ImageDraw.Draw(band)
    fb = ImageFont.truetype(FONT, TITLE_SIZE)
    fs = ImageFont.truetype(FONT, SUBTITLE_SIZE)
    d.text((TITLE_X, TITLE_Y), TITLE, font=fb, fill=(255, 255, 255))
    d.text((TITLE_X + 2, TITLE_Y + 70), SUBTITLE, font=fs, fill=(255, 200, 120))
    band.save(HDR, quality=92)
    print(f"wrote {HDR}")


if __name__ == "__main__":
    main()
