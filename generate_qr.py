"""
Generate QR Code (qr.png) and Printable Luxury QR Card (qr-card.png) for Barber SaaS Poll
"""

import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
from generate_assets import shape_arabic_word, draw_centered

BASE_DIR = os.path.dirname(__file__)
TARGET_URL = "https://ashrafnsali-bit.github.io/Poll/"

def generate_qr_codes():
    # 1. Create High-Error-Correction QR Code
    qr = qrcode.QRCode(
        version=4,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=14,
        border=3,
    )
    qr.add_data(TARGET_URL)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="#0b0f19", back_color="#ffffff").convert("RGBA")
    qr_w, qr_h = qr_img.size

    # Embed small logo in the center of the QR code
    logo_path = os.path.join(BASE_DIR, "logo.png")
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        logo_size = int(qr_w * 0.21)
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

        # White circular pad behind logo
        pad_size = logo_size + 16
        pad = Image.new("RGBA", (pad_size, pad_size), (0, 0, 0, 0))
        pad_draw = ImageDraw.Draw(pad)
        pad_draw.ellipse([0, 0, pad_size, pad_size], fill=(255, 255, 255, 255))

        pos_pad = ((qr_w - pad_size) // 2, (qr_h - pad_size) // 2)
        pos_logo = ((qr_w - logo_size) // 2, (qr_h - logo_size) // 2)
        qr_img.paste(pad, pos_pad, pad)
        qr_img.paste(logo, pos_logo, logo)

    qr_out = os.path.join(BASE_DIR, "qr.png")
    qr_img.save(qr_out, "PNG")
    print("[SUCCESS] qr.png saved at", qr_out)

    # 2. Create Luxury Shareable / Printable QR Card (800 x 1040)
    card_w, card_h = 800, 1040
    card = Image.new("RGBA", (card_w, card_h), (11, 15, 25, 255))

    # Subtle ambient glow
    glow = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glow)
    for step in range(30, 0, -1):
        r = step * 12
        g_draw.ellipse([400 - r, 500 - r, 400 + r, 500 + r], fill=(37, 99, 235, 3))
    card = Image.alpha_composite(card, glow)
    draw = ImageDraw.Draw(card)

    # Outer border
    draw.rounded_rectangle([24, 24, card_w - 24, card_h - 24], radius=28, outline=(245, 158, 11, 220), width=3)
    draw.rounded_rectangle([34, 34, card_w - 34, card_h - 34], radius=22, outline=(45, 59, 91, 255), width=2)

    # Top Logo
    if os.path.exists(logo_path):
        top_logo = Image.open(logo_path).convert("RGBA").resize((130, 130), Image.Resampling.LANCZOS)
        card.paste(top_logo, ((card_w - 130) // 2, 65), top_logo)

    font_title = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 42)
    font_sub = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 28)
    font_cta = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 25)
    font_url = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 20)

    # Titles
    draw_centered(draw, 50, card_w - 50, 215, "منصة حِلاق | Barber SaaS", font_title, (255, 255, 255, 255))
    draw_centered(draw, 50, card_w - 50, 275, "استبيان دراسة السوق لصالونات الحلاقة", font_sub, (56, 189, 248, 255))

    # White rounded container for QR Code
    qr_box_size = 460
    qr_resized = qr_img.resize((qr_box_size - 40, qr_box_size - 40), Image.Resampling.LANCZOS)
    box_x = (card_w - qr_box_size) // 2
    box_y = 345
    draw.rounded_rectangle([box_x, box_y, box_x + qr_box_size, box_y + qr_box_size],
                           radius=28, fill=(255, 255, 255, 255), outline=(245, 158, 11, 255), width=4)
    card.paste(qr_resized, (box_x + 20, box_y + 20), qr_resized)

    # Bottom Call-To-Action pill
    pill_y = 835
    draw.rounded_rectangle([95, pill_y, card_w - 95, pill_y + 62], radius=31, fill=(30, 41, 59, 255), outline=(245, 158, 11, 200), width=2)
    draw_centered(draw, 95, card_w - 95, pill_y + 13, "امسح الرمز بكاميرا الجوال للمشاركة في أقل من دقيقة", font_cta, (251, 191, 36, 255))

    # URL at bottom
    url_bbox = draw.textbbox((0, 0), TARGET_URL, font=font_url)
    url_w = url_bbox[2] - url_bbox[0]
    draw.text(((card_w - url_w) // 2, 928), TARGET_URL, font=font_url, fill=(148, 163, 184, 255))

    card_out = os.path.join(BASE_DIR, "qr-card.png")
    card.save(card_out, "PNG")
    print("[SUCCESS] qr-card.png saved at", card_out)

if __name__ == "__main__":
    generate_qr_codes()

