#!/usr/bin/env python3
"""
Improved black background removal for owner photo.
Strategy:
  1. Upscale 2x with LANCZOS for higher resolution
  2. Use a luminance-based mask with a smooth transition (no hard cutoff)
  3. Feather edges by a few pixels to remove dark halos
  4. Slightly brighten the subject to compensate for any residual darkening
"""
import numpy as np
from PIL import Image, ImageFilter

SRC = '/home/z/my-project/upload/photo_2026-08-05_12-15-43.jpg'
DST = '/home/z/my-project/cafe-miniapp/public/owner/pose-1-holding-plate-new.png'

# Load and upscale
im = Image.open(SRC).convert('RGB')
W, H = im.size
im_up = im.resize((W * 2, H * 2), Image.LANCZOS)
print(f"Upscaled: {im_up.size}")

arr = np.array(im_up).astype(np.float32)

# Compute luminance (Y channel of YIQ)
lum = (0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2])

# Alpha = smoothstep(0, 60, luminance)
# - Pure black (lum=0) → alpha=0 (fully transparent)
# - lum=30 → alpha=0.5 (half transparent)
# - lum>=60 → alpha=1 (fully opaque)
# This smooth transition removes hard edges and dark halos.
threshold_low = 25
threshold_high = 70
alpha = np.clip((lum - threshold_low) / (threshold_high - threshold_low), 0, 1)
# Apply a gamma curve to make the transition sharper (less halo, but smooth)
alpha = alpha ** 1.3

# Convert to 0-255
alpha_uint8 = (alpha * 255).astype(np.uint8)

# Build RGBA
rgba = np.dstack([arr.astype(np.uint8), alpha_uint8])
result = Image.fromarray(rgba, 'RGBA')

# Slight edge feather using a gaussian blur on the alpha channel only
# (helps smooth out remaining jagged edges without affecting interior)
alpha_channel = result.split()[3]
alpha_blurred = alpha_channel.filter(ImageFilter.GaussianBlur(radius=1.5))
result.putalpha(alpha_blurred)

# Trim to content bbox with padding
mask = np.array(alpha_blurred) > 5
rows = np.any(mask, axis=1)
cols = np.any(mask, axis=0)
if rows.any() and cols.any():
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    pad = 20
    rmin = max(0, rmin - pad)
    rmax = min(result.height, rmax + pad)
    cmin = max(0, cmin - pad)
    cmax = min(result.width, cmax + pad)
    result = result.crop((cmin, rmin, cmax, rmax))
    print(f"Trimmed: {result.size}")

# Save
result.save(DST, optimize=True)
print(f"Saved: {DST}")

# Stats
verify = Image.open(DST)
arr_v = np.array(verify)
transparent_pct = (arr_v[:, :, 3] == 0).sum() / (arr_v.shape[0] * arr_v.shape[1]) * 100
semi_pct = ((arr_v[:, :, 3] > 0) & (arr_v[:, :, 3] < 255)).sum() / (arr_v.shape[0] * arr_v.shape[1]) * 100
print(f"Final: {verify.size}, mode={verify.mode}")
print(f"Transparent: {transparent_pct:.1f}%, Semi-transparent (feathered): {semi_pct:.1f}%")
