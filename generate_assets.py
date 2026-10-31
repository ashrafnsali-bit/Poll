"""
Generate high-resolution logo.png, og-image.png (1200x630 for WhatsApp/social previews), and favicon.png
"""

from PIL import Image, ImageDraw, ImageFont
import os
import math

BASE_DIR = os.path.dirname(__file__)

def create_logo():
    size = (512, 512)
    img = Image.new("RGBA", size, (11, 15, 25, 255)) # Dark navy
    draw = ImageDraw.Draw(img)

    # Gradient background circle
    center = (256, 256)
    radius = 220
    
    # Outer glow
    for r in range(radius + 20, radius, -1):
        alpha = int(30 * (1 - (r - radius) / 20))
        draw.ellipse([center[0] - r, center[1] - r, center[0] + r, center[1] + r], outline=(37, 99, 235, alpha), width=2)

    # Main circle background
    draw.ellipse([center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius], 
                 fill=(19, 27, 46, 255), outline=(245, 158, 11, 255), width=6)
    
    # Inner gold ring
    draw.ellipse([center[0] - (radius - 12), center[1] - (radius - 12), center[0] + (radius - 12), center[1] + (radius - 12)], 
                 outline=(56, 189, 248, 180), width=2)

    # Stylized Barber Pole in the center
    pole_w = 60
    pole_h = 220
    top_y = 130
    pole_left = 256 - pole_w // 2
    pole_right = 256 + pole_w // 2

    # Pole Caps (Gold brass)
    # Top Cap
    draw.ellipse([pole_left - 10, top_y - 25, pole_right + 10, top_y + 15], fill=(245, 158, 11, 255))
    draw.ellipse([256 - 15, top_y - 45, 256 + 15, top_y - 15], fill=(251, 191, 36, 255))
    
    # Bottom Cap
    draw.ellipse([pole_left - 10, top_y + pole_h - 15, pole_right + 10, top_y + pole_h + 25], fill=(245, 158, 11, 255))
    draw.rectangle([256 - 15, top_y + pole_h + 20, 256 + 15, top_y + pole_h + 40], fill=(217, 119, 6, 255))

    # Pole Cylinder body
    draw.rectangle([pole_left, top_y, pole_right, top_y + pole_h], fill=(240, 240, 245, 255))

    # Diagonal stripes (Barber red/blue/white)
    # Clip to pole rect
    mask = Image.new("L", size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rectangle([pole_left, top_y, pole_right, top_y + pole_h], fill=255)

    stripe_img = Image.new("RGBA", size, (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(stripe_img)

    stripe_w = 32
    for y in range(top_y - 100, top_y + pole_h + 100, stripe_w * 3):
        # Red stripe
        s_draw.polygon([
            (pole_left, y), (pole_right, y + 40),
            (pole_right, y + 40 + stripe_w), (pole_left, y + stripe_w)
        ], fill=(239, 68, 68, 255))
        # Blue stripe
        s_draw.polygon([
            (pole_left, y + stripe_w * 2), (pole_right, y + 40 + stripe_w * 2),
            (pole_right, y + 40 + stripe_w * 3), (pole_left, y + stripe_w * 3)
        ], fill=(37, 99, 235, 255))

    img.paste(stripe_img, (0, 0), mask)

    # Pole glass gloss/reflection
    draw.line([pole_left + 8, top_y + 10, pole_left + 8, top_y + pole_h - 10], fill=(255, 255, 255, 160), width=4)
    draw.line([pole_left + 16, top_y + 15, pole_left + 16, top_y + pole_h - 15], fill=(255, 255, 255, 80), width=2)

    # Crossed Scissors Silhouette behind or in front
    # Left blade
    draw.line([160, 310, 350, 190], fill=(203, 213, 225, 230), width=8)
    draw.ellipse([140, 295, 175, 330], outline=(203, 213, 225, 230), width=6)
    # Right blade
    draw.line([350, 310, 160, 190], fill=(203, 213, 225, 230), width=8)
    draw.ellipse([335, 295, 370, 330], outline=(203, 213, 225, 230), width=6)

    # Center screw
    draw.ellipse([251, 245, 261, 255], fill=(245, 158, 11, 255))

    # Stars
    for sx, sy in [(170, 240), (340, 240)]:
        draw.polygon([(sx, sy-8), (sx+3, sy-2), (sx+9, sy), (sx+4, sy+4), (sx+6, sy+10), (sx, sy+6), (sx-6, sy+10), (sx-4, sy+4), (sx-9, sy), (sx-3, sy-2)], fill=(251, 191, 36, 255))

    logo_path = os.path.join(BASE_DIR, "logo.png")
    img.save(logo_path, "PNG")
    print("[SUCCESS] logo.png created at", logo_path)

    # Favicon
    fav = img.resize((64, 64), Image.Resampling.LANCZOS)
    fav_path = os.path.join(BASE_DIR, "favicon.png")
    fav.save(fav_path, "PNG")
    print("[SUCCESS] favicon.png created at", fav_path)


def create_og_image():
    # 1200 x 630 pixels - Standard Open Graph format for WhatsApp, Facebook, Twitter, Telegram
    w, h = 1200, 630
    img = Image.new("RGBA", (w, h), (11, 15, 25, 255))
    draw = ImageDraw.Draw(img)

    # Background ambient lighting
    for r in range(400, 0, -10):
        alpha = int(45 * (1 - r / 400))
        draw.ellipse([250 - r, 315 - r, 250 + r, 315 + r], fill=(37, 99, 235, alpha))
        draw.ellipse([950 - r, 315 - r, 950 + r, 315 + r], fill=(245, 158, 11, int(alpha * 0.6)))

    # Outer border
    draw.rectangle([10, 10, w - 10, h - 10], outline=(45, 59, 91, 255), width=3)
    # Inner accent top bar
    for x in range(10, w - 10):
        ratio = (x - 10) / (w - 20)
        # Gradient blue to gold
        r_c = int(37 + ratio * (245 - 37))
        g_c = int(99 + ratio * (158 - 99))
        b_c = int(235 + ratio * (11 - 235))
        draw.line([x, 10, x, 18], fill=(r_c, g_c, b_c, 255))

    # Paste Logo on the right / center
    logo = Image.open(os.path.join(BASE_DIR, "logo.png"))
    logo_resized = logo.resize((360, 360), Image.Resampling.LANCZOS)
    img.paste(logo_resized, (760, 135), logo_resized)

    # Left content box (Card style)
    # Pill badge
    draw.rounded_rectangle([80, 85, 420, 135], radius=25, fill=(245, 158, 11, 35), outline=(245, 158, 11, 180), width=2)

    # Feature boxes at bottom
    feats = [
        ("📅 تنظيم المواعيد", 80),
        ("✂️ إدارة الحلاقين", 280),
        ("🎁 بطاقات الولاء", 475)
    ]
    for text, bx in feats:
        draw.rounded_rectangle([bx, 480, bx + 180, 545], radius=12, fill=(19, 27, 46, 255), outline=(45, 59, 91, 255), width=1)

    # Load system Arabic / English fonts if available, otherwise fallback to default
    font_large = None
    font_med = None
    font_small = None

    font_paths = [
        "C:\\Windows\\Fonts\\tahoma.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\segoeui.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                font_large = ImageFont.truetype(fp, 56)
                font_med = ImageFont.truetype(fp, 32)
                font_small = ImageFont.truetype(fp, 22)
                font_badge = ImageFont.truetype(fp, 20)
                break
            except Exception:
                pass

    if not font_large:
        font_large = ImageFont.load_default()
        font_med = font_large
        font_small = font_large
        font_badge = font_large

    # Texts
    draw.text((105, 96), "★ استبيان دراسة السوق الأولي", fill=(251, 191, 36, 255), font=font_badge)
    draw.text((80, 160), "منصة Barber SaaS", fill=(255, 255, 255, 255), font=font_large)
    draw.text((80, 235), "النظام الذكي لإدارة صالونات الحلاقة", fill=(56, 189, 248, 255), font=font_med)
    draw.text((80, 290), "والعناية بالرجل في المملكة", fill=(245, 158, 11, 255), font=font_med)

    desc_lines = [
        "شاركنا رأيك في دقيقة واحدة لنقيس اهتمامك كمستثمر أو صاحب صالون",
        "واحصل على أسبقية التجربة المجانية فور الإطلاق الرسمي."
    ]
    y_off = 360
    for l in desc_lines:
        draw.text((80, y_off), l, fill=(148, 163, 184, 255), font=font_small)
        y_off += 34

    # Feature texts
    draw.text((95, 502), "📅 تنظيم المواعيد", fill=(255, 255, 255, 255), font=font_small)
    draw.text((295, 502), "✂️ إدارة الحلاقين", fill=(255, 255, 255, 255), font=font_small)
    draw.text((490, 502), "🎁 بطاقات الولاء", fill=(255, 255, 255, 255), font=font_small)

    og_path = os.path.join(BASE_DIR, "og-image.png")
    img.save(og_path, "PNG")
    print("[SUCCESS] og-image.png created at", og_path)

if __name__ == "__main__":
    create_logo()
    create_og_image()
