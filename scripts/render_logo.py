#!/usr/bin/env python3
"""
Regenerate /public/brand/logo.png from the current <CafeLogo> React component.
Uses Playwright to render the component standalone, then crops tightly.

Output: a transparent PNG showing 🪶☕🪶 (two feathers flanking a coffee cup,
rotated outward like wings) — the design defined in CafeLogo.jsx.
"""
import asyncio
import numpy as np
from PIL import Image

OUT = '/home/z/my-project/cafe-miniapp/public/brand/logo.png'

HTML = """<!doctype html>
<html><head><meta charset="utf-8">
<style>
  html, body { margin: 0; padding: 0; background: transparent; }
  body { display: inline-block; padding: 40px; }
  /* Wide enough so the rotated feathers don't get clipped */
  #logo { width: 320px; height: 240px; display: flex; align-items: center; justify-content: center; }
</style></head>
<body>
  <div id="logo">
    <!-- Outer wrapper is wide; inner is naturally-sized flex content -->
    <div style="display:flex;align-items:center;justify-content:center;position:relative;">
      <span style="font-size:96px;line-height:1;transform:rotate(-32deg) translateY(2px);display:inline-block;filter:drop-shadow(0 1px 1px rgba(0,0,0,0.15));margin-right:-12px;">🪶</span>
      <span style="font-size:128px;line-height:1;transform:translateY(2px);display:inline-block;filter:drop-shadow(0 1px 2px rgba(0,0,0,0.2));z-index:2;">☕</span>
      <span style="font-size:96px;line-height:1;transform:rotate(32deg) scaleX(-1) translateY(2px);display:inline-block;filter:drop-shadow(0 1px 1px rgba(0,0,0,0.15));margin-left:-12px;">🪶</span>
    </div>
  </div>
</body></html>
"""

async def render():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 480, 'height': 360}, device_scale_factor=2)
        page = await ctx.new_page()
        await page.set_content(HTML)
        # Wait for emoji font to render
        await page.wait_for_timeout(500)
        # Screenshot the inner flex container (which sizes itself to content)
        el = await page.query_selector('#logo > div')
        png = await el.screenshot(omit_background=True)
        await browser.close()
    return png

def crop_tight(img):
    """Crop transparent borders so the logo fills the canvas."""
    arr = np.array(img.convert('RGBA'))
    alpha = arr[:, :, 3]
    # Rows/cols with any non-transparent pixel
    rows = np.where((alpha > 30).any(axis=1))[0]
    cols = np.where((alpha > 30).any(axis=0))[0]
    if len(rows) == 0 or len(cols) == 0:
        return img
    top, bottom = rows[0], rows[-1]
    left, right = cols[0], cols[-1]
    # Add 8px padding
    pad = 8
    top = max(0, top - pad)
    left = max(0, left - pad)
    bottom = min(img.height, bottom + pad)
    right = min(img.width, right + pad)
    return img.crop((left, top, right, bottom))

def make_white_transparent(img, threshold=245):
    """Make near-white pixels transparent (in case background isn't fully transparent)."""
    arr = np.array(img.convert('RGBA')).astype(np.int16)
    r, g, b, a = arr[:,:,0], arr[:,:,1], arr[:,:,2], arr[:,:,3]
    # Near-white = high RGB AND currently opaque
    is_white = (r > threshold) & (g > threshold) & (b > threshold) & (a > 200)
    arr[is_white, 3] = 0
    return Image.fromarray(arr.astype('uint8'), 'RGBA')

async def main():
    png_bytes = await render()
    from io import BytesIO
    img = Image.open(BytesIO(png_bytes))
    print(f"Raw render: {img.size}")
    img = make_white_transparent(img)
    img = crop_tight(img)
    # Make it square by padding the shorter edge
    w, h = img.size
    side = max(w, h)
    canvas = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    canvas.paste(img, ((side - w) // 2, (side - h) // 2), img)
    canvas.save(OUT, 'PNG', optimize=True)
    print(f"Saved: {OUT} ({canvas.size})")
    # Verify alpha
    arr = np.array(canvas)
    a = arr[:,:,3]
    print(f"Alpha: min={a.min()}, max={a.max()}, mean={a.mean():.1f}, transparent%={((a<50).sum()/a.size*100):.1f}")

asyncio.run(main())
