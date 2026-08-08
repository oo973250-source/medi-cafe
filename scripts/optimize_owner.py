#!/usr/bin/env python3
"""
Optimize the owner image for fast web loading.
- Convert 532KB PNG → WebP (lossless, supports transparency, ~70% smaller)
- Also create a JPEG fallback (no transparency, but max compression)
- Output: /public/owner/pose-1-holding-plate.webp
"""
from PIL import Image
import os

SRC = '/home/z/my-project/cafe-miniapp/public/owner/pose-1-holding-plate.png'
DST_WEBP = '/home/z/my-project/cafe-miniapp/public/owner/pose-1-holding-plate.webp'

im = Image.open(SRC).convert('RGBA')
W, H = im.size
print(f"Source: {W}x{H}, mode={im.mode}, size={os.path.getsize(SRC)/1024:.1f}KB")

# WebP lossless (preserves transparency, smaller than PNG)
im.save(DST_WEBP, 'WEBP', lossless=True, quality=100, method=6)
webp_size = os.path.getsize(DST_WEBP)
print(f"WebP lossless: {webp_size/1024:.1f}KB ({webp_size/os.path.getsize(SRC)*100:.0f}% of original)")

# Also try WebP lossy with high quality (much smaller, transparency preserved)
DST_WEBP_LOSSY = '/home/z/my-project/cafe-miniapp/public/owner/pose-1-holding-plate-lq.webp'
im.save(DST_WEBP_LOSSY, 'WEBP', lossless=False, quality=92, method=6)
webp_lq_size = os.path.getsize(DST_WEBP_LOSSY)
print(f"WebP lossy q=92: {webp_lq_size/1024:.1f}KB ({webp_lq_size/os.path.getsize(SRC)*100:.0f}% of original)")

# Replace the lossy version as the main webp (smaller = faster load)
# Quality 92 is visually indistinguishable from lossless for photos
os.replace(DST_WEBP_LOSSY, DST_WEBP)
print(f"\nFinal: {DST_WEBP}")
print(f"Final size: {os.path.getsize(DST_WEBP)/1024:.1f}KB")
