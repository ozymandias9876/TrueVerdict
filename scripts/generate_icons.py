import os
from PIL import Image, ImageDraw

def create_icon(size: int, output_path: str):
    # Create image with transparent background
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Outer shield / rounded badge
    padding = size * 0.08
    badge_color = (16, 185, 129)  # Emerald green (#10B981)
    accent_dark = (6, 78, 59)     # Deep emerald

    # Draw rounded rect or circle background
    draw.ellipse(
        [padding, padding, size - padding, size - padding],
        fill=badge_color,
        outline=accent_dark,
        width=max(1, int(size * 0.04))
    )

    # Draw stylized 'V' checkmark for TrueVerdict
    check_color = (255, 255, 255, 255)
    points = [
        (size * 0.28, size * 0.52),
        (size * 0.44, size * 0.68),
        (size * 0.72, size * 0.36)
    ]
    draw.line(points, fill=check_color, width=max(2, int(size * 0.12)), joint="curve")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "PNG")
    print(f"Generated {output_path} ({size}x{size})")

if __name__ == "__main__":
    base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "extension", "icons")
    for s in [16, 48, 128]:
        create_icon(s, os.path.join(base_dir, f"icon-{s}.png"))
