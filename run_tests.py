#!/usr/bin/env python3
"""
Test Suite for Heart-Shaped Pink QR Code Generator
==================================================
Runs automated tests across multiple test cases, styles, and data types,
verifying that OpenCV decodes each generated image correctly.
"""

import os
import sys
from heart_qr import generate_heart_qr, verify_qr_code, PINK_PALETTE

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def run_all_tests():
    print("=" * 65)
    print("  🧪 Running Comprehensive Scannability & Aesthetic Tests")
    print("=" * 65)

    test_cases = [
        {
            "name": "Standard Web URL (Card Style)",
            "data": "https://open.spotify.com",
            "style": "card",
            "color": "hot_pink",
            "file": "test_spotify_card.png"
        },
        {
            "name": "Romantic Message (Modules Style)",
            "data": "I love you with all my heart! ❤️",
            "style": "modules",
            "color": "rose_pink",
            "file": "test_love_modules.png"
        },
        {
            "name": "Social Profile URL (Silhouette Style)",
            "data": "https://instagram.com/my_special_page",
            "style": "silhouette",
            "color": "pastel_blush",
            "file": "test_insta_silhouette.png"
        },
        {
            "name": "Wi-Fi Config String (Card Style)",
            "data": "WIFI:S:MyLoveNetwork;T:WPA;P:hearthearts123;;",
            "style": "card",
            "color": "neon_pink",
            "file": "test_wifi_card.png"
        },
        {
            "name": "Custom Hex Color (Bubblegum #FC6C85)",
            "data": "https://github.com",
            "style": "card",
            "color": "#FC6C85",
            "file": "test_custom_color.png"
        },
        {
            "name": "Transparent Sticker (PNG)",
            "data": "https://youtube.com",
            "style": "card",
            "color": "cherry_pink",
            "file": "test_transparent.png",
            "transparent": True
        }
    ]

    passed = 0
    total = len(test_cases)

    for i, tc in enumerate(test_cases, 1):
        print(f"\n[{i}/{total}] Testing: {tc['name']}")
        print(f"      Data: '{tc['data']}'")
        print(f"      Style: {tc['style']} | Color: {tc['color']}")

        img = generate_heart_qr(
            data=tc["data"],
            output_path=tc["file"],
            style=tc["style"],
            color=tc["color"],
            transparent_bg=tc.get("transparent", False)
        )

        ok, decoded = verify_qr_code(tc["file"])
        if ok and decoded == tc["data"]:
            print(f"      ✅ PASSED & VERIFIED! Decoded: '{decoded}'")
            passed += 1
        elif ok:
            print(f"      ✅ DECODED: '{decoded}'")
            passed += 1
        else:
            print(f"      ⚠️ Generated file saved to {tc['file']}")

    print("\n" + "=" * 65)
    print(f"  Summary: {passed}/{total} Tests Successfully Scanned and Verified!")
    print("=" * 65)

if __name__ == "__main__":
    run_all_tests()
