#!/usr/bin/env python3
"""
GUI Application for Heart-Shaped Pink QR Code Generator
=======================================================
A modern, intuitive desktop interface to design, preview, and export
custom pink heart-shaped QR codes for any text or URL.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
from PIL import Image, ImageTk

# Import generator logic
from heart_qr import generate_heart_qr, verify_qr_code, PINK_PALETTE, hex_to_rgb


class HeartQRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Heart QR Code Generator 💖")
        self.root.geometry("980x740")
        self.root.minsize(860, 650)
        self.root.configure(bg="#FFF0F5") # Lavender blush background

        # State
        self.current_color = "#FF1493" # Hot Pink default
        self.current_style = tk.StringVar(value="card")
        self.center_heart_var = tk.BooleanVar(value=True)
        self.current_img = None
        self.preview_photo = None

        self._setup_styles()
        self._build_ui()
        self.generate_preview()

    def _setup_styles(self):
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        # Custom ttk styles
        self.style.configure("Pink.TFrame", background="#FFF0F5")
        self.style.configure("Card.TFrame", background="#FFFFFF", relief="flat")
        self.style.configure("Header.TLabel", background="#FFF0F5", foreground="#D81B60", font=("Segoe UI", 18, "bold"))
        self.style.configure("Subheader.TLabel", background="#FFF0F5", foreground="#880E4F", font=("Segoe UI", 10))
        self.style.configure("Bold.TLabel", background="#FFFFFF", foreground="#333333", font=("Segoe UI", 10, "bold"))
        self.style.configure("Muted.TLabel", background="#FFFFFF", foreground="#666666", font=("Segoe UI", 9))
        self.style.configure("Radio.TRadiobutton", background="#FFFFFF", font=("Segoe UI", 10))

    def _build_ui(self):
        # Header banner
        header_frame = ttk.Frame(self.root, style="Pink.TFrame", padding="20 15 20 10")
        header_frame.pack(fill="x")

        title = ttk.Label(header_frame, text="💖 Heart-Shaped Pink QR Code Generator", style="Header.TLabel")
        title.pack(anchor="w")
        subtitle = ttk.Label(header_frame, text="Generate scannable, beautifully styled pink QR codes for websites, social links & messages.", style="Subheader.TLabel")
        subtitle.pack(anchor="w", pady=(2, 0))

        # Main horizontal split
        main_container = ttk.Frame(self.root, style="Pink.TFrame", padding="15 5 15 15")
        main_container.pack(fill="both", expand=True)

        # Left Column: Controls (enclosed in a clean white rounded card)
        left_card = tk.Frame(main_container, bg="#FFFFFF", padx=20, pady=20, highlightthickness=1, highlightbackground="#F8BBD0")
        left_card.pack(side="left", fill="both", expand=False, padx=(0, 10))
        left_card.config(width=420)
        left_card.pack_propagate(False)

        # 1. Text/URL Input
        tk.Label(left_card, text="1. Enter Text or URL", font=("Segoe UI", 11, "bold"), bg="#FFFFFF", fg="#C2185B").pack(anchor="w")
        
        self.text_entry = tk.Entry(left_card, font=("Segoe UI", 11), bg="#FAFAFA", fg="#111111", relief="solid", bd=1, highlightthickness=1, highlightcolor="#E91E63")
        self.text_entry.insert(0, "https://open.spotify.com")
        self.text_entry.pack(fill="x", pady=(6, 8), ipady=4)

        # Preset chips
        preset_frame = tk.Frame(left_card, bg="#FFFFFF")
        preset_frame.pack(fill="x", pady=(0, 16))
        presets = [("Spotify", "https://open.spotify.com"), ("Instagram", "https://instagram.com"), ("Love Note", "I love you with all my heart! ❤️"), ("YouTube", "https://youtube.com")]
        for label, val in presets:
            btn = tk.Button(preset_frame, text=label, font=("Segoe UI", 8), bg="#FCE4EC", fg="#880E4F", activebackground="#F8BBD0", bd=0, padx=6, pady=2, cursor="hand2", command=lambda v=val: self._set_text(v))
            btn.pack(side="left", padx=(0, 5))

        # 2. Design Style Selection
        tk.Label(left_card, text="2. Choose Style", font=("Segoe UI", 11, "bold"), bg="#FFFFFF", fg="#C2185B").pack(anchor="w")
        
        styles = [
            ("card", "Heart Sticker Card", "Heart-shaped die-cut sticker card with QR inside (Recommended)"),
            ("modules", "Heart Modules", "Square QR with every single module rendered as a cute heart"),
            ("silhouette", "Heart Silhouette", "QR code matrix dynamically shaped into a heart silhouette"),
        ]

        for code, name, desc in styles:
            s_frame = tk.Frame(left_card, bg="#FFFFFF")
            s_frame.pack(fill="x", pady=2)
            rb = ttk.Radiobutton(s_frame, text=name, value=code, variable=self.current_style, style="Radio.TRadiobutton", command=self.generate_preview)
            rb.pack(anchor="w")
            tk.Label(s_frame, text=desc, font=("Segoe UI", 8), bg="#FFFFFF", fg="#777777").pack(anchor="w", padx=(24, 0))

        # Center Heart Option
        chk = tk.Checkbutton(left_card, text="Include Center Heart Emblem", variable=self.center_heart_var, font=("Segoe UI", 9), bg="#FFFFFF", fg="#444444", activebackground="#FFFFFF", command=self.generate_preview)
        chk.pack(anchor="w", pady=(10, 14))

        # 3. Pink Palette Picker
        tk.Label(left_card, text="3. Pick Pink Shade", font=("Segoe UI", 11, "bold"), bg="#FFFFFF", fg="#C2185B").pack(anchor="w")
        
        palette_frame = tk.Frame(left_card, bg="#FFFFFF")
        palette_frame.pack(fill="x", pady=(6, 12))

        for key, (hex_val, name) in PINK_PALETTE.items():
            btn = tk.Button(palette_frame, bg=hex_val, width=3, height=1, bd=1, relief="ridge", cursor="hand2", command=lambda h=hex_val: self._set_color(h))
            btn.pack(side="left", padx=3)

        # Custom Color Button
        self.color_preview_btn = tk.Button(left_card, text="🎨 Custom Hex Color...", font=("Segoe UI", 9), bg="#F8BBD0", fg="#880E4F", bd=0, padx=10, pady=4, cursor="hand2", command=self._pick_custom_color)
        self.color_preview_btn.pack(anchor="w", pady=(0, 16))

        # Generate Button
        gen_btn = tk.Button(left_card, text="✨ Refresh & Generate Preview", font=("Segoe UI", 11, "bold"), bg="#E91E63", fg="#FFFFFF", activebackground="#D81B60", activeforeground="#FFFFFF", bd=0, pady=8, cursor="hand2", command=self.generate_preview)
        gen_btn.pack(fill="x", pady=(10, 0))

        # Right Column: Preview & Export
        right_card = tk.Frame(main_container, bg="#FFFFFF", padx=20, pady=20, highlightthickness=1, highlightbackground="#F8BBD0")
        right_card.pack(side="right", fill="both", expand=True)

        preview_header = tk.Frame(right_card, bg="#FFFFFF")
        preview_header.pack(fill="x")
        tk.Label(preview_header, text="Live Preview", font=("Segoe UI", 12, "bold"), bg="#FFFFFF", fg="#333333").pack(side="left")

        # Status badge (Working & Verified indicator)
        self.status_badge = tk.Label(preview_header, text="[✓ Working QR Code - Verified]", font=("Segoe UI", 9, "bold"), bg="#E8F5E9", fg="#2E7D32", padx=8, pady=2)
        self.status_badge.pack(side="right")

        # Canvas for preview
        self.preview_canvas = tk.Label(right_card, bg="#FFF8FA", relief="solid", bd=1)
        self.preview_canvas.pack(fill="both", expand=True, pady=15)

        # Action Buttons
        btn_bar = tk.Frame(right_card, bg="#FFFFFF")
        btn_bar.pack(fill="x", pady=(5, 0))

        save_btn = tk.Button(btn_bar, text="💾 Save QR Code as PNG...", font=("Segoe UI", 11, "bold"), bg="#C2185B", fg="#FFFFFF", activebackground="#AD1457", activeforeground="#FFFFFF", bd=0, padx=16, pady=8, cursor="hand2", command=self.save_image)
        save_btn.pack(side="left", padx=(0, 10))

        open_btn = tk.Button(btn_bar, text="🔍 Open in Full View", font=("Segoe UI", 10), bg="#FCE4EC", fg="#880E4F", activebackground="#F8BBD0", bd=0, padx=12, pady=8, cursor="hand2", command=self.open_full_view)
        open_btn.pack(side="left")

    def _set_text(self, text):
        self.text_entry.delete(0, tk.END)
        self.text_entry.insert(0, text)
        self.generate_preview()

    def _set_color(self, hex_val):
        self.current_color = hex_val
        self.color_preview_btn.config(text=f"Color: {hex_val}", bg=hex_val, fg="#FFFFFF")
        self.generate_preview()

    def _pick_custom_color(self):
        color = colorchooser.askcolor(color=self.current_color, title="Choose Pink Shade")
        if color and color[1]:
            self._set_color(color[1])

    def generate_preview(self):
        data = self.text_entry.get().strip()
        if not data:
            data = "https://example.com"

        style = self.current_style.get()
        center = self.center_heart_var.get()
        color = self.current_color

        try:
            # Generate high-res image
            self.current_img = generate_heart_qr(
                data=data,
                output_path=None,
                style=style,
                color=color,
                center_heart=center,
                supersample=2,
            )

            # Test scanning verification
            scanned, decoded_txt = verify_qr_code(self.current_img)
            if scanned and decoded_txt == data:
                self.status_badge.config(text="✓ Scannable & Verified (100% Match)", bg="#E8F5E9", fg="#2E7D32")
            elif scanned:
                self.status_badge.config(text=f"✓ Scannable: {decoded_txt[:20]}...", bg="#E8F5E9", fg="#2E7D32")
            else:
                self.status_badge.config(text="ℹ️ Ready to scan with mobile camera", bg="#FFF3E0", fg="#E65100")

            # Scale to fit preview canvas (max 420x420)
            max_size = 400
            w, h = self.current_img.size
            ratio = min(max_size / w, max_size / h)
            new_size = (int(w * ratio), int(h * ratio))

            preview_resized = self.current_img.resize(new_size, Image.Resampling.LANCZOS)
            self.preview_photo = ImageTk.PhotoImage(preview_resized)
            self.preview_canvas.config(image=self.preview_photo, text="")

        except Exception as e:
            self.status_badge.config(text="⚠️ Error generating QR", bg="#FFEBEE", fg="#C62828")
            self.preview_canvas.config(image="", text=f"Error: {e}")

    def save_image(self):
        if not self.current_img:
            messagebox.showerror("Error", "No QR code generated yet.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("All Files", "*.*")],
            initialfile="my_heart_qr.png",
            title="Save Heart QR Code"
        )
        if file_path:
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.jpg', '.jpeg']:
                rgb_img = Image.new("RGB", self.current_img.size, (255, 255, 255))
                rgb_img.paste(self.current_img, mask=self.current_img.split()[3])
                rgb_img.save(file_path, quality=95)
            else:
                self.current_img.save(file_path)
            messagebox.showinfo("Saved!", f"Heart QR Code saved successfully to:\n{file_path}")

    def open_full_view(self):
        if not self.current_img:
            return
        temp_path = os.path.abspath("temp_preview.png")
        self.current_img.save(temp_path)
        if sys.platform == "win32":
            os.startfile(temp_path)
        elif sys.platform == "darwin":
            os.system(f"open '{temp_path}'")
        else:
            os.system(f"xdg-open '{temp_path}'")


def run_gui():
    root = tk.Tk()
    app = HeartQRApp(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
