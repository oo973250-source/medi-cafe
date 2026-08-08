#!/usr/bin/env python3
"""
Detect the vertical position of the plate the owner is holding.
Strategy:
  - For each row, find the horizontal span of "golden" pixels (high R, mid G, low B)
  - The plate corresponds to the widest such span
  - Return the y-coordinate (in % of image height) of the plate center
"""
from PIL import Image
import numpy as np

SRC = '/home/z/my-project/cafe-miniapp/public/owner/pose-1-holding-plate.png'

im = Image.open(SRC).convert('RGBA')
W, H = im.size
arr = np.array(im).astype(np.float32)
rgb = arr[:, :, :3]
alpha = arr[:, :, 3]

# Golden/warm pixels: R high, G medium, B low (yellow/orange tones)
R, G, B = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
is_gold = (R > 150) & (G > 100) & (G < 220) & (B < 130) & (alpha > 100)

# Per-row count of golden pixels
row_counts = is_gold.sum(axis=1)

# Find the row with the maximum golden pixel count
max_row = int(np.argmax(row_counts))
max_count = int(row_counts[max_row])
plate_y_pct = (max_row / H) * 100

# Also find the "plate region" — contiguous rows with >50% of max count
threshold = max_count * 0.5
in_plate = row_counts > threshold

# Find the longest contiguous run
plate_start = max_row
plate_end = max_row
i = max_row
while i >= 0 and in_plate[i]:
    plate_start = i
    i -= 1
i = max_row
while i < H and in_plate[i]:
    plate_end = i
    i += 1

plate_center_y = (plate_start + plate_end) / 2
plate_center_pct = (plate_center_y / H) * 100

# Horizontal span at plate center
plate_row_gold = is_gold[plate_start:plate_end+1]
if plate_row_gold.any():
    cols_with_gold = np.where(plate_row_gold.any(axis=0))[0]
    plate_left = int(cols_with_gold.min())
    plate_right = int(cols_with_gold.max())
else:
    plate_left = plate_right = W // 2

print(f"Image size: {W}x{H}")
print(f"Max golden row: y={max_row} ({max_row/H*100:.1f}% from top), count={max_count}")
print(f"Plate region: y={plate_start} to y={plate_end} ({plate_start/H*100:.1f}% to {plate_end/H*100:.1f}%)")
print(f"Plate center: y={plate_center_y:.1f} ({plate_center_pct:.1f}% from top)")
print(f"Plate horizontal: x={plate_left} to x={plate_right} (width={plate_right-plate_left}px, {((plate_right-plate_left)/W)*100:.1f}% of width)")
print()
print(f"=== For CSS: plate is at ~{plate_center_pct:.1f}% from top of image ===")
