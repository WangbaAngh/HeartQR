# 💖 Heart-Shaped Pink QR Code Generator

A Python application that converts any text, URL, Wi-Fi configuration, or romantic note into **working, scannable QR codes** styled in **pink** with **heart geometry**.

Unlike naive QR masking tools that break corner markers and fail to scan, this generator adheres strictly to the **ISO/IEC 18004 QR specification** with **Error Correction Level H (30%)**, preserving critical finder patterns, alignment grids, and timing tracks so standard smartphone cameras and barcode readers can scan them instantly.

---

## ✨ Features

- **100% Working & Scannable**: Built-in computer vision verification powered by OpenCV ensures every generated QR code is verified before export.
- **3 Unique Heart Styles**:
  - `card` *(Default)*: A die-cut heart sticker card with smooth borders and a pink QR code inside.
  - `modules`: A square QR matrix where **every single data module is an individual pink vector heart**, finder pattern eyes are hearts, and an optional center heart charm is embedded.
  - `silhouette`: The QR code matrix boundary dynamically curves into a heart silhouette while keeping finder patterns and timing lines 100% intact.
- **Curated Pink Palette**:
  - `hot_pink` (`#FF1493`): Deep, vibrant, romantic pink
  - `rose_pink` (`#E91E63`): Elegant rose magenta
  - `pastel_blush` (`#FF69B4`): Soft pastel pink
  - `bubblegum` (`#FC6C85`): Sweet and playful
  - `neon_pink` (`#FF007F`): High contrast electric pink
  - `cherry_pink` (`#DE3163`): Deep luxury pink
  - Custom Hex (`#RRGGBB`): Use any shade you love!
- **Multiple Interfaces**:
  - 🖥️ **Desktop GUI**: Visual real-time preview with color picker and save dialog.
  - 💻 **Interactive CLI**: Friendly prompt-driven terminal interface.
  - ⚡ **Command-Line Flags**: Fast one-liner generation for scripts and batch jobs.
  - 🐍 **Python API**: Import `generate_heart_qr()` into your own apps.

---

## 🚀 Quick Start

### 1. Requirements

Install dependencies:
```bash
pip install -r requirements.txt
```
*(Dependencies: `qrcode[pil]`, `pillow`, `opencv-python`, `numpy`)*

---

### 2. Usage Options

#### Option A: Interactive Mode (Easiest)
Simply run the script with no arguments:
```bash
python heart_qr.py
```
It will ask for your text/URL, style preference, and pink shade, then automatically save and open your QR code!

---

#### Option B: Graphical Desktop Interface (GUI)
Launch the graphical app with live preview and save buttons:
```bash
python heart_qr.py --gui
# or
python gui.py
```

---

#### Option C: Command-Line One-Liners

**Generate a Spotify Heart Card:**
```bash
python heart_qr.py "https://open.spotify.com" -s card -c hot_pink -o spotify_heart.png
```

**Generate a Love Note with Heart Modules:**
```bash
python heart_qr.py "I love you with all my heart!" -s modules -c rose_pink -o love.png
```

**Generate an Instagram Profile Heart Silhouette:**
```bash
python heart_qr.py "https://instagram.com/yourprofile" -s silhouette -c pastel_blush -o insta.png
```

**Generate a Transparent PNG Sticker:**
```bash
python heart_qr.py "https://example.com" -s card -c neon_pink --transparent -o sticker.png
```

---

### 3. Python API Usage

You can also use this library directly in your Python code:

```python
from heart_qr import generate_heart_qr, verify_qr_code

# Generate the QR image
img = generate_heart_qr(
    data="https://open.spotify.com",
    output_path="my_qr.png",
    style="card",          # 'card', 'modules', or 'silhouette'
    color="#FF1493",       # Any hex code or preset name
    center_heart=True,     # Include center heart badge
    transparent_bg=False,  # Transparent background outside heart
)

# Verify scannability with computer vision
is_valid, decoded_text = verify_qr_code("my_qr.png")
print("Scannable:", is_valid, "Decoded:", decoded_text)
```

---

## 🧪 Automated Test Suite

To verify that all styles, colors, and data types (short messages, long URLs, Wi-Fi configurations) scan accurately:
```bash
python run_tests.py
```
Results: `6/6 Tests Successfully Scanned and Verified!`

---

## 📁 Project Structure

```text
heart-qr-code/
├── heart_qr.py           # Core generator engine & CLI
├── gui.py                # Desktop GUI with live real-time preview
├── run_tests.py          # Automated verification test suite
├── requirements.txt      # Python dependencies
└── README.md             # Documentation & Guide
```
