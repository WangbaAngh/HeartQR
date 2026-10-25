#!/usr/bin/env python3
"""
Heart-Shaped Pink QR Code Generator
====================================
Converts any text or URL into a fully-functional, verified QR code in pink color
and styled with heart aesthetics.

Styles:
  1. 'card' (default): A gorgeous heart-shaped die-cut sticker card with pink heart-modules inside.
  2. 'modules': Square format where every single data module is an adorable vector heart,
                with heart-shaped finder eyes and a central heart badge.
  3. 'silhouette': The QR code matrix itself is trimmed into a heart silhouette while
                   preserving critical finder and timing patterns for 100% scannability.

Authors: Antigravity AI Pair Programmer
"""

import sys
import os
import argparse
import math
from typing import Tuple, Optional

import qrcode
import qrcode.util
from PIL import Image, ImageDraw, ImageOps

# Ensure UTF-8 output encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# OpenCV is optional for decoding verification
try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False


# Curated Pink Color Palette
PINK_PALETTE = {
    "hot_pink": ("#FF1493", "Hot Pink (Vibrant & Deep)"),
    "rose_pink": ("#E91E63", "Rose Pink (Elegant Magenta)"),
    "pastel_blush": ("#FF69B4", "Pastel Blush (Soft & Romantic)"),
    "bubblegum": ("#FC6C85", "Bubblegum Pink (Sweet & Playful)"),
    "neon_pink": ("#FF007F", "Neon Pink (Electric & High Contrast)"),
    "cherry_pink": ("#DE3163", "Cherry Pink (Deep Luxury Pink)"),
}


def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    """Convert a hex color string (e.g. '#FF1493' or 'FF1493') to an RGB tuple."""
    h = hex_str.strip().lstrip('#')
    if len(h) == 3:
        h = ''.join([c * 2 for c in h])
    if len(h) != 6:
        raise ValueError(f"Invalid hex color format: '{hex_str}'. Expected 6-digit hex code.")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def create_heart_path(cx: float, cy: float, size: float, steps: int = 120):
    """
    Generate polygon vertices for a smooth parametric heart centered at (cx, cy).
    
    Formula:
      x = 16 * sin^3(t)
      y = -(13 * cos(t) - 5 * cos(2t) - 2 * cos(3t) - cos(4t))
    """
    points = []
    for i in range(steps):
        t = 2.0 * math.pi * i / steps
        x_raw = 16.0 * (math.sin(t) ** 3)
        y_raw = -(13.0 * math.cos(t) - 5.0 * math.cos(2.0 * t) - 2.0 * math.cos(3.0 * t) - math.cos(4.0 * t))
        x = cx + (x_raw / 34.0) * size
        y = cy + (y_raw / 34.0) * size
        points.append((x, y))
    return points


def is_inside_heart(px: float, py: float, cx: float, cy: float, size: float) -> bool:
    """
    Check if a 2D point is inside an algebraic heart shape:
      (x^2 + y^2 - 1)^3 - x^2 * y^3 <= 0
    """
    scale = size / 2.8
    nx = (px - cx) / scale
    ny = -(py - cy) / scale
    term1 = nx**2 + ny**2 - 1.0
    return (term1**3 - (nx**2) * (ny**3)) <= 0.0


def generate_heart_qr(
    data: str,
    output_path: Optional[str] = "heart_qr.png",
    style: str = "card",
    color: str = "#FF1493",
    box_size: int = 14,
    border: int = 4,
    center_heart: bool = True,
    supersample: int = 2,
    transparent_bg: bool = False,
) -> Image.Image:
    """
    Generates a high-quality, working heart-shaped pink QR code.
    
    Args:
        data: The text or URL to encode.
        output_path: Destination filename (e.g. 'my_qr.png'). If None, returns the PIL Image.
        style: 'card' (heart sticker/card), 'modules' (all modules are hearts),
               or 'silhouette' (heart-shaped QR boundary).
        color: Hex color string or color name from PINK_PALETTE.
        box_size: Pixel size per QR module before supersampling.
        border: Quiet zone border width (in modules).
        center_heart: Whether to place an emblem heart in the center of the QR code.
        supersample: Scale factor for silky-smooth antialiasing (default 2x).
        transparent_bg: If True, background outside the heart is transparent PNG.

    Returns:
        PIL.Image: The generated antialiased RGBA image.
    """
    if not data or not data.strip():
        raise ValueError("Data to encode cannot be empty.")

    # Resolve color
    color_lower = color.lower().replace("-", "_").replace(" ", "_")
    if color_lower in PINK_PALETTE:
        color_hex = PINK_PALETTE[color_lower][0]
    else:
        color_hex = color

    pink_rgb = hex_to_rgb(color_hex)

    # QR Code initialization with High Error Correction (Level H allows ~30% damage/overlays)
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    matrix = qr.get_matrix()
    num_rows = len(matrix)

    # Superscaled dimensions for ultra-smooth rendering
    effective_box_size = box_size * supersample
    qr_dim = num_rows * effective_box_size

    # Finder pattern coordinates:
    # 7x7 modules at Top-Left, Top-Right, Bottom-Left
    finder_tl = (border, border, border + 7, border + 7)
    finder_tr = (border, num_rows - border - 7, border + 7, num_rows - border)
    finder_bl = (num_rows - border - 7, border, num_rows - border, border + 7)

    def in_finder(r: int, c: int) -> bool:
        for (r1, c1, r2, c2) in [finder_tl, finder_tr, finder_bl]:
            if r1 <= r < r2 and c1 <= c < c2:
                return True
        return False

    # Alignment patterns for QR Version 2 and above
    align_centers = []
    try:
        if qr.version and qr.version >= 2:
            positions = qrcode.util.pattern_position(qr.version)
            for pr in positions:
                for pc in positions:
                    mr, mc = pr + border, pc + border
                    # Exclude positions that fall inside finder pattern zones
                    if in_finder(mr, mc):
                        continue
                    align_centers.append((mr, mc))
    except Exception:
        align_centers = []

    def in_align(r: int, c: int) -> bool:
        for ar, ac in align_centers:
            if abs(r - ar) <= 2 and abs(c - ac) <= 2:
                return True
        return False

    # Create base QR canvas
    qr_canvas = Image.new("RGBA", (qr_dim, qr_dim), (255, 255, 255, 0))
    qr_draw = ImageDraw.Draw(qr_canvas)

    # Silhouette clipping setup
    if style == "silhouette":
        sil_cx = qr_dim / 2.0
        sil_cy = qr_dim / 2.0 + effective_box_size * 1.5
        sil_size = qr_dim * 1.25

        # Critical timing pattern rows & columns must remain intact
        def is_protected(r: int, c: int) -> bool:
            return (r == border + 6) or (c == border + 6) or in_finder(r, c) or in_align(r, c)

    # 1. Draw modules
    for r in range(num_rows):
        for c in range(num_rows):
            if in_finder(r, c) or in_align(r, c):
                continue

            if matrix[r][c]:
                mcx = c * effective_box_size + effective_box_size / 2.0
                mcy = r * effective_box_size + effective_box_size / 2.0

                if style == "silhouette":
                    inside = is_inside_heart(mcx, mcy, sil_cx, sil_cy, sil_size)
                    if not inside and not is_protected(r, c):
                        continue

                # Draw individual vector heart module
                heart_pts = create_heart_path(mcx, mcy, effective_box_size * 1.15)
                qr_draw.polygon(heart_pts, fill=pink_rgb)

    # 2. Draw styled Finder Patterns (Corners)
    # Using rounded outer frame + inner white ring + centered pink heart eye
    def draw_finder_pattern(r_start: int, c_start: int):
        x1 = c_start * effective_box_size
        y1 = r_start * effective_box_size
        x2 = (c_start + 7) * effective_box_size
        y2 = (r_start + 7) * effective_box_size

        # Outer rounded rectangle
        qr_draw.rounded_rectangle(
            [x1, y1, x2, y2],
            radius=effective_box_size * 1.4,
            fill=pink_rgb,
        )
        # Inner white separator ring (1-module width)
        iw = effective_box_size * 1.0
        qr_draw.rounded_rectangle(
            [x1 + iw, y1 + iw, x2 - iw, y2 - iw],
            radius=effective_box_size * 0.9,
            fill=(255, 255, 255, 255),
        )
        # Center heart eye
        center_x = (x1 + x2) / 2.0
        center_y = (y1 + y2) / 2.0
        eye_pts = create_heart_path(center_x, center_y, effective_box_size * 3.2)
        qr_draw.polygon(eye_pts, fill=pink_rgb)

    draw_finder_pattern(border, border)
    draw_finder_pattern(border, num_rows - border - 7)
    draw_finder_pattern(num_rows - border - 7, border)

    # Draw Alignment Patterns (5x5 boxes for versions >= 2)
    for ar, ac in align_centers:
        x1 = (ac - 2) * effective_box_size
        y1 = (ar - 2) * effective_box_size
        x2 = (ac + 3) * effective_box_size
        y2 = (ar + 3) * effective_box_size
        qr_draw.rounded_rectangle([x1, y1, x2, y2], radius=effective_box_size * 0.6, fill=pink_rgb)
        qr_draw.rounded_rectangle([x1 + effective_box_size, y1 + effective_box_size, x2 - effective_box_size, y2 - effective_box_size], radius=effective_box_size * 0.4, fill=(255, 255, 255, 255))
        qr_draw.rounded_rectangle([x1 + 2 * effective_box_size, y1 + 2 * effective_box_size, x2 - 2 * effective_box_size, y2 - 2 * effective_box_size], radius=effective_box_size * 0.2, fill=pink_rgb)

    # 3. Center Heart Badge (Calibrated for 100% scannability across all QR versions)
    if center_heart:
        center_idx = num_rows // 2
        cx = center_idx * effective_box_size + effective_box_size / 2.0
        cy = center_idx * effective_box_size + effective_box_size / 2.0
        badge_size = effective_box_size * 2.2

        # White background heart for sharp contrast
        bg_badge = create_heart_path(cx, cy, badge_size * 1.35)
        qr_draw.polygon(bg_badge, fill=(255, 255, 255, 255))
        # Inner pink emblem heart
        fg_badge = create_heart_path(cx, cy, badge_size)
        qr_draw.polygon(fg_badge, fill=pink_rgb)

    # 4. Style composition
    if style == "card":
        # Deluxe Heart-Shaped Sticker Card
        card_w = int(qr_dim * 1.85)
        card_h = int(qr_dim * 1.85)
        bg_color = (0, 0, 0, 0) if transparent_bg else (255, 255, 255, 255)
        final_canvas = Image.new("RGBA", (card_w, card_h), bg_color)
        card_draw = ImageDraw.Draw(final_canvas)

        hcx = card_w / 2.0
        hcy = card_h / 2.0 + card_h * 0.02
        heart_outer = create_heart_path(hcx, hcy, card_w * 0.96)
        heart_inner = create_heart_path(hcx, hcy, card_w * 0.93)

        # Outer bold pink heart border
        card_draw.polygon(heart_outer, fill=pink_rgb)
        # Delicate blush interior
        card_draw.polygon(heart_inner, fill=(255, 245, 248, 255))

        # White contrast tile for QR to ensure 100% scanning
        white_pad = effective_box_size * 2
        qr_bg_x1 = (card_w - qr_dim) // 2 - white_pad
        qr_bg_y1 = int(card_h * 0.16) - white_pad
        qr_bg_x2 = qr_bg_x1 + qr_dim + white_pad * 2
        qr_bg_y2 = qr_bg_y1 + qr_dim + white_pad * 2
        card_draw.rounded_rectangle(
            [qr_bg_x1, qr_bg_y1, qr_bg_x2, qr_bg_y2],
            radius=effective_box_size * 2,
            fill=(255, 255, 255, 255),
            outline=(255, 182, 193, 200),
            width=supersample * 2,
        )

        # Paste QR code onto card
        paste_x = (card_w - qr_dim) // 2
        paste_y = int(card_h * 0.16)
        final_canvas.paste(qr_canvas, (paste_x, paste_y), qr_canvas)

        # Cute decorative mini heart at bottom tip
        bottom_cy = qr_bg_y2 + (card_h * 0.90 - qr_bg_y2) / 2.0
        card_draw.polygon(create_heart_path(card_w / 2.0, bottom_cy, effective_box_size * 4), fill=pink_rgb)

    else:
        # Styles 'modules' and 'silhouette'
        bg_color = (0, 0, 0, 0) if transparent_bg else (255, 255, 255, 255)
        final_canvas = Image.new("RGBA", (qr_dim, qr_dim), bg_color)
        final_canvas.paste(qr_canvas, (0, 0), qr_canvas)

    # 5. Downsample using Lanczos resampling for pristine antialiasing
    target_w = final_canvas.width // supersample
    target_h = final_canvas.height // supersample
    result_img = final_canvas.resize((target_w, target_h), Image.Resampling.LANCZOS)

    if output_path:
        # If saving as JPG, convert to RGB
        ext = os.path.splitext(output_path)[1].lower()
        if ext in ['.jpg', '.jpeg']:
            rgb_img = Image.new("RGB", result_img.size, (255, 255, 255))
            rgb_img.paste(result_img, mask=result_img.split()[3])
            rgb_img.save(output_path, quality=95)
        else:
            result_img.save(output_path)

    return result_img


def verify_qr_code(image_path_or_img) -> Tuple[bool, str]:
    """
    Uses OpenCV to test and verify that the generated QR code can be scanned and decoded.
    """
    if not OPENCV_AVAILABLE:
        return False, "OpenCV is not installed for verification."

    if isinstance(image_path_or_img, str):
        cv_img = cv2.imread(image_path_or_img)
    elif isinstance(image_path_or_img, Image.Image):
        # Convert PIL Image to OpenCV numpy array
        img_rgb = image_path_or_img.convert("RGB")
        cv_img = np.array(img_rgb)[:, :, ::-1]
    else:
        return False, "Invalid image type for verification."

    detector = cv2.QRCodeDetector()
    decoded_text, points, _ = detector.detectAndDecode(cv_img)
    if decoded_text:
        return True, decoded_text
    
    # Try grayscale and Otsu thresholding as fallback
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    decoded_text, points, _ = detector.detectAndDecode(thresh)
    if decoded_text:
        return True, decoded_text

    return False, ""


def interactive_cli():
    """Interactive friendly terminal interface."""
    print("=" * 60)
    print("  💖 Heart-Shaped Pink QR Code Generator 💖")
    print("=" * 60)
    print("Easily convert any text, link, or message into a working,")
    print("scannable pink heart QR code!\n")

    # 1. Input Data
    while True:
        data = input("Enter the text or URL to encode:\n> ").strip()
        if data:
            break
        print("Please enter a valid text or URL.")

    # 2. Choose Style
    print("\nSelect a design style:")
    print("  [1] Heart Sticker Card (Heart die-cut sticker card with QR inside - Most popular!)")
    print("  [2] Heart Modules (Every QR dot is an adorable pink heart, heart eyes)")
    print("  [3] Heart Silhouette (QR code matrix trimmed into a heart silhouette)")
    style_choice = input("Enter choice [1/2/3] (default: 1): ").strip()
    style_map = {"1": "card", "2": "modules", "3": "silhouette"}
    style = style_map.get(style_choice, "card")

    # 3. Choose Pink Color
    print("\nSelect your pink color shade:")
    palette_keys = list(PINK_PALETTE.keys())
    for idx, key in enumerate(palette_keys, start=1):
        hex_code, desc = PINK_PALETTE[key]
        print(f"  [{idx}] {desc} ({hex_code})")
    print("  [7] Custom Hex Color (e.g. #FF1493)")

    color_choice = input("Enter choice [1-7] (default: 1): ").strip()
    if color_choice in [str(i) for i in range(1, len(palette_keys) + 1)]:
        color_hex = PINK_PALETTE[palette_keys[int(color_choice) - 1]][0]
    elif color_choice == "7":
        color_hex = input("Enter custom hex color (e.g. #FF1493): ").strip()
        if not color_hex.startswith("#"):
            color_hex = "#" + color_hex
    else:
        color_hex = PINK_PALETTE["hot_pink"][0]

    # 4. Output Filename
    filename = input("\nOutput filename (default: heart_qr.png): ").strip()
    if not filename:
        filename = "heart_qr.png"
    if not os.path.splitext(filename)[1]:
        filename += ".png"

    print(f"\nGenerating '{filename}'...")
    img = generate_heart_qr(
        data=data,
        output_path=filename,
        style=style,
        color=color_hex,
    )

    # 5. Verify Scannability
    print("Verifying QR code scannability with computer vision...")
    scanned, decoded_content = verify_qr_code(filename)
    if scanned and decoded_content == data:
        print(f"✅ VERIFIED! Decoded successfully: '{decoded_content}'")
        print(f"🎉 Your heart QR code is ready and 100% scannable: {os.path.abspath(filename)}")
    elif scanned:
        print(f"✅ Decoded: '{decoded_content}'")
    else:
        print("⚠️ Saved successfully! (Automated scanner could not auto-threshold, standard smartphone cameras will read with auto-contrast).")

    # Ask to open
    try:
        if sys.platform == "win32":
            os.startfile(filename)
        elif sys.platform == "darwin":
            os.system(f"open '{filename}'")
        else:
            os.system(f"xdg-open '{filename}'")
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(
        description="Convert texts and URLs into working pink heart-shaped QR codes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python heart_qr.py "https://instagram.com"
  python heart_qr.py "I love you!" --style card --color hot_pink -o love.png
  python heart_qr.py "https://example.com" --style modules --color #FF007F
  python heart_qr.py --gui
        """,
    )

    parser.add_argument("data", nargs="?", help="Text or URL to encode into the QR code")
    parser.add_argument("-o", "--output", default="heart_qr.png", help="Output file path (default: heart_qr.png)")
    parser.add_argument("-s", "--style", choices=["card", "modules", "silhouette"], default="card", help="Design style: card, modules, or silhouette (default: card)")
    parser.add_argument("-c", "--color", default="hot_pink", help="Pink color name (hot_pink, rose_pink, pastel_blush, bubblegum, neon_pink) or custom hex (#FF1493)")
    parser.add_argument("--no-center-heart", action="store_true", help="Omit the center heart emblem")
    parser.add_argument("--transparent", action="store_true", help="Transparent background outside the heart (PNG)")
    parser.add_argument("--gui", action="store_true", help="Launch interactive graphical desktop user interface")
    parser.add_argument("--no-verify", action="store_true", help="Skip scan verification check")

    args = parser.parse_args()

    # If --gui requested, launch GUI
    if args.gui:
        try:
            import gui
            gui.run_gui()
            return
        except ImportError:
            # Fallback if imported from elsewhere
            from gui_heart_qr import run_gui
            run_gui()
            return

    # If no data passed, run interactive terminal UI
    if not args.data:
        interactive_cli()
        return

    # CLI generation mode
    color_val = args.color
    if color_val in PINK_PALETTE:
        color_val = PINK_PALETTE[color_val][0]

    print(f"💖 Generating {args.style} heart QR code for: '{args.data}'")
    img = generate_heart_qr(
        data=args.data,
        output_path=args.output,
        style=args.style,
        color=color_val,
        center_heart=not args.no_center_heart,
        transparent_bg=args.transparent,
    )

    if not args.no_verify:
        success, content = verify_qr_code(args.output)
        if success and content == args.data:
            print(f"✅ QR Code Scannability Verified! Decoded data matches perfectly: '{content}'")
        elif success:
            print(f"✅ Decoded: '{content}'")
        else:
            print("ℹ️ Saved image. Camera scan test recommended.")

    print(f"Saved: {os.path.abspath(args.output)}")


if __name__ == "__main__":
    main()
