#!/usr/bin/env python3
"""
Optimize all large images in /public/backgrounds and /public/brand to WebP.
Skips files that already have a .webp version.
"""
from PIL import Image
import os
import sys

DIRS = [
    '/home/z/my-project/cafe-miniapp/public/backgrounds',
    '/home/z/my-project/cafe-miniapp/public/brand',
    '/home/z/my-project/cafe-miniapp/public/owner',
]

total_saved = 0
total_original = 0

for d in DIRS:
    if not os.path.isdir(d):
        continue
    for fname in os.listdir(d):
        if not fname.lower().endswith('.png'):
            continue
        fpath = os.path.join(d, fname)
        webp_path = fpath.rsplit('.', 1)[0] + '.webp'
        if os.path.exists(webp_path):
            print(f"SKIP (already webp): {fname}")
            continue
        try:
            im = Image.open(fpath)
            orig_size = os.path.getsize(fpath)
            # Use lossy q=90 for backgrounds (visually identical, much smaller)
            # Use lossy q=95 for owner/logo (more detail)
            if 'owner' in d or 'brand' in d:
                quality = 95
            else:
                quality = 88
            im.save(webp_path, 'WEBP', lossless=False, quality=quality, method=6)
            new_size = os.path.getsize(webp_path)
            saved = orig_size - new_size
            pct = (new_size / orig_size) * 100
            print(f"{fname}: {orig_size//1024}KB → {new_size//1024}KB ({pct:.0f}%, saved {saved//1024}KB)")
            total_saved += saved
            total_original += orig_size
        except Exception as e:
            print(f"ERROR {fname}: {e}")

print(f"\nTotal: {total_original//1024}KB → {(total_original-total_saved)//1024}KB (saved {total_saved//1024}KB, {(total_saved/total_original)*100:.0f}% reduction)")
