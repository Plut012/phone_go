#!/usr/bin/env python3
"""Generate app icons for Flow"""

from PIL import Image, ImageDraw, ImageFont

def create_icon(size, filename):
    # Create image with dark background
    bg_color = (26, 18, 16)  # #1a1210
    stone_color = (201, 168, 104)  # #c9a868

    img = Image.new('RGB', (size, size), bg_color)
    draw = ImageDraw.Draw(img)

    # Draw a simple Go board grid (3x3)
    margin = size // 6
    cell = (size - 2 * margin) // 2
    grid_color = (125, 92, 74)  # #7d5c4a

    # Draw grid lines
    line_width = max(2, size // 100)
    for i in range(3):
        pos = margin + i * cell
        # Horizontal
        draw.line([(margin, pos), (size - margin, pos)], fill=grid_color, width=line_width)
        # Vertical
        draw.line([(pos, margin), (pos, size - margin)], fill=grid_color, width=line_width)

    # Draw star point in center
    center = size // 2
    star_r = max(3, size // 40)
    draw.ellipse([center - star_r, center - star_r, center + star_r, center + star_r],
                 fill=stone_color)

    # Draw a black and white stone
    stone_r = max(10, size // 10)

    # Black stone (top-left area)
    bx, by = margin + cell // 2, margin + cell // 2
    draw.ellipse([bx - stone_r, by - stone_r, bx + stone_r, by + stone_r],
                 fill=(74, 30, 40))  # #4a1e28

    # White stone (bottom-right area)
    wx, wy = margin + cell + cell // 2, margin + cell + cell // 2
    draw.ellipse([wx - stone_r, wy - stone_r, wx + stone_r, wy + stone_r],
                 fill=(224, 168, 112))  # #e0a870

    img.save(filename)
    print(f"Created {filename}")

if __name__ == '__main__':
    create_icon(192, 'icon-192.png')
    create_icon(512, 'icon-512.png')
    print("Icons generated successfully!")
