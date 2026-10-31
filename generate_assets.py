"""
Generate high-resolution logo.png, logo.jpg, og-image.png, og-image.jpg (1200x630), and favicon.png
Includes pure-Python Arabic Contextual Shaping & BiDi rendering and true alpha compositing.
"""

from PIL import Image, ImageDraw, ImageFont
import os

BASE_DIR = os.path.dirname(__file__)

# Unicode Arabic Presentation Forms-B table: char -> (isolated, final, initial, medial, connects_after)
ARABIC_FORMS = {
    '\u0621': ('\ufe80', '\ufe80', '\ufe80', '\ufe80', False), # ء
    '\u0622': ('\ufe81', '\ufe82', '\ufe81', '\ufe82', False), # آ
    '\u0623': ('\ufe83', '\ufe84', '\ufe83', '\ufe84', False), # أ
    '\u0624': ('\ufe85', '\ufe86', '\ufe85', '\ufe86', False), # ؤ
    '\u0625': ('\ufe87', '\ufe88', '\ufe87', '\ufe88', False), # إ
    '\u0626': ('\ufe89', '\ufe8a', '\ufe8b', '\ufe8c', True),  # ئ
    '\u0627': ('\ufe8d', '\ufe8e', '\ufe8d', '\ufe8e', False), # ا
    '\u0628': ('\ufe8f', '\ufe90', '\ufe91', '\ufe92', True),  # ب
    '\u0629': ('\ufe93', '\ufe94', '\ufe93', '\ufe94', False), # ة
    '\u062a': ('\ufe95', '\ufe96', '\ufe97', '\ufe98', True),  # ت
    '\u062b': ('\ufe99', '\ufe9a', '\ufe9b', '\ufe9c', True),  # ث
    '\u062c': ('\ufe9d', '\ufe9e', '\ufe9f', '\ufea0', True),  # ج
    '\u062d': ('\ufea1', '\ufea2', '\ufea3', '\ufea4', True),  # ح
    '\u062e': ('\ufea5', '\ufea6', '\ufea7', '\ufea8', True),  # خ
    '\u062f': ('\ufea9', '\ufeaa', '\ufea9', '\ufeaa', False), # د
    '\u0630': ('\ufeab', '\ufeac', '\ufeab', '\ufeac', False), # ذ
    '\u0631': ('\ufead', '\ufeae', '\ufead', '\ufeae', False), # ر
    '\u0632': ('\ufeaf', '\ufeb0', '\ufeaf', '\ufeb0', False), # ز
    '\u0633': ('\ufeb1', '\ufeb2', '\ufeb3', '\ufeb4', True),  # س
    '\u0634': ('\ufeb5', '\ufeb6', '\ufeb7', '\ufeb8', True),  # ش
    '\u0635': ('\ufeb9', '\ufeba', '\ufebb', '\ufebc', True),  # ص
    '\u0636': ('\ufebd', '\ufebe', '\ufebf', '\ufec0', True),  # ض
    '\u0637': ('\ufec1', '\ufec2', '\ufec3', '\ufec4', True),  # ط
    '\u0638': ('\ufec5', '\ufec6', '\ufec7', '\ufec8', True),  # ظ
    '\u0639': ('\ufec9', '\ufeca', '\ufecb', '\ufecc', True),  # ع
    '\u063a': ('\ufecd', '\ufece', '\ufecf', '\ufed0', True),  # غ
    '\u0640': ('\u0640', '\u0640', '\u0640', '\u0640', True),  # ـ
    '\u0641': ('\ufed1', '\ufed2', '\ufed3', '\ufed4', True),  # ف
    '\u0642': ('\ufed5', '\ufed6', '\ufed7', '\ufed8', True),  # ق
    '\u0643': ('\ufed9', '\ufeda', '\ufedb', '\ufedc', True),  # ك
    '\u0644': ('\ufedd', '\ufede', '\ufedf', '\ufee0', True),  # ل
    '\u0645': ('\ufee1', '\ufee2', '\ufee3', '\ufee4', True),  # م
    '\u0646': ('\ufee5', '\ufee6', '\ufee7', '\ufee8', True),  # ن
    '\u0647': ('\ufee9', '\ufeea', '\ufeeb', '\ufeec', True),  # ه
    '\u0648': ('\ufeed', '\ufeee', '\ufeed', '\ufeee', False), # و
    '\u0649': ('\ufeef', '\ufef0', '\ufeef', '\ufef0', False), # ى
    '\u064a': ('\ufef1', '\ufef2', '\ufef3', '\ufef4', True),  # ي
}

LAM_ALEF_MAP = {
    '\u0622': ('\ufef5', '\ufef6'), # لآ
    '\u0623': ('\ufef7', '\ufef8'), # لأ
    '\u0625': ('\ufef9', '\ufefa'), # لإ
    '\u0627': ('\ufefb', '\ufefc'), # لا
}

DIACRITICS = set('\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652')

def shape_arabic_word(text):
    # Strip diacritics for clean shaping
    chars = [c for c in text if c not in DIACRITICS]
    # Combine Lam + Alef into token tuples
    tokens = []
    i = 0
    while i < len(chars):
        if chars[i] == '\u0644' and i + 1 < len(chars) and chars[i + 1] in LAM_ALEF_MAP:
            tokens.append(('LAM_ALEF', chars[i + 1]))
            i += 2
        else:
            tokens.append(('CHAR', chars[i]))
            i += 1

    shaped = []
    for idx, (kind, val) in enumerate(tokens):
        prev_connects = False
        if idx > 0:
            p_kind, p_val = tokens[idx - 1]
            if p_kind == 'CHAR' and p_val in ARABIC_FORMS and ARABIC_FORMS[p_val][4]:
                prev_connects = True

        next_connects = False
        if idx + 1 < len(tokens):
            n_kind, n_val = tokens[idx + 1]
            if n_kind == 'LAM_ALEF' or (n_kind == 'CHAR' and n_val in ARABIC_FORMS):
                next_connects = True

        if kind == 'LAM_ALEF':
            iso_form, fin_form = LAM_ALEF_MAP[val]
            shaped.append(fin_form if prev_connects else iso_form)
        elif val in ARABIC_FORMS:
            iso_f, fin_f, ini_f, med_f, can_conn_after = ARABIC_FORMS[val]
            if prev_connects and next_connects and can_conn_after:
                shaped.append(med_f)
            elif prev_connects:
                shaped.append(fin_f)
            elif next_connects and can_conn_after:
                shaped.append(ini_f)
            else:
                shaped.append(iso_f)
        else:
            shaped.append(val)

    # BiDi visual ordering for RTL line containing Arabic and LTR words
    # Split into runs of RTL vs LTR (ASCII letters/numbers)
    runs = []
    cur_run = []
    cur_is_ltr = None
    for ch in shaped:
        if ('a' <= ch.lower() <= 'z') or ('0' <= ch <= '9'):
            is_ltr = True
        elif ch == ' ' and cur_is_ltr is not None:
            is_ltr = cur_is_ltr
        else:
            is_ltr = False

        if cur_is_ltr is None or is_ltr == cur_is_ltr:
            cur_run.append(ch)
            cur_is_ltr = is_ltr
        else:
            runs.append((cur_is_ltr, ''.join(cur_run)))
            cur_run = [ch]
            cur_is_ltr = is_ltr
    if cur_run:
        runs.append((cur_is_ltr, ''.join(cur_run)))

    visual_parts = []
    for is_ltr, segment in reversed(runs):
        if is_ltr:
            # Keep trailing/leading spaces on right side properly
            visual_parts.append(segment)
        else:
            visual_parts.append(segment[::-1])

    return ''.join(visual_parts)


def create_logo():
    size = (512, 512)
    img = Image.new("RGBA", size, (11, 15, 25, 255))
    draw = ImageDraw.Draw(img)

    center = (256, 256)
    radius = 220

    # Main circle background
    draw.ellipse([center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius],
                 fill=(19, 27, 46, 255), outline=(245, 158, 11, 255), width=8)

    # Inner cyan ring
    draw.ellipse([center[0] - (radius - 14), center[1] - (radius - 14), center[0] + (radius - 14), center[1] + (radius - 14)],
                 outline=(56, 189, 248, 200), width=2)

    # Stylized Barber Pole in the center
    pole_w = 64
    pole_h = 220
    top_y = 130
    pole_left = 256 - pole_w // 2
    pole_right = 256 + pole_w // 2

    # Top Cap
    draw.ellipse([pole_left - 10, top_y - 25, pole_right + 10, top_y + 15], fill=(245, 158, 11, 255))
    draw.ellipse([256 - 15, top_y - 45, 256 + 15, top_y - 15], fill=(251, 191, 36, 255))

    # Bottom Cap
    draw.ellipse([pole_left - 10, top_y + pole_h - 15, pole_right + 10, top_y + pole_h + 25], fill=(245, 158, 11, 255))
    draw.rectangle([256 - 15, top_y + pole_h + 20, 256 + 15, top_y + pole_h + 40], fill=(217, 119, 6, 255))

    # Pole Cylinder body
    draw.rectangle([pole_left, top_y, pole_right, top_y + pole_h], fill=(241, 245, 249, 255))

    # Diagonal stripes
    mask = Image.new("L", size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rectangle([pole_left, top_y, pole_right, top_y + pole_h], fill=255)

    stripe_img = Image.new("RGBA", size, (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(stripe_img)

    stripe_w = 32
    for y in range(top_y - 100, top_y + pole_h + 100, stripe_w * 3):
        s_draw.polygon([
            (pole_left, y), (pole_right, y + 40),
            (pole_right, y + 40 + stripe_w), (pole_left, y + stripe_w)
        ], fill=(239, 68, 68, 255))
        s_draw.polygon([
            (pole_left, y + stripe_w * 2), (pole_right, y + 40 + stripe_w * 2),
            (pole_right, y + 40 + stripe_w * 3), (pole_left, y + stripe_w * 3)
        ], fill=(37, 99, 235, 255))

    img.paste(stripe_img, (0, 0), mask)

    # Glass reflection
    draw.line([pole_left + 10, top_y + 10, pole_left + 10, top_y + pole_h - 10], fill=(255, 255, 255, 200), width=4)

    # Crossed Scissors
    draw.line([155, 315, 355, 185], fill=(226, 232, 240, 255), width=8)
    draw.ellipse([135, 298, 172, 335], outline=(226, 232, 240, 255), width=6)
    draw.line([355, 315, 155, 185], fill=(226, 232, 240, 255), width=8)
    draw.ellipse([338, 298, 375, 335], outline=(226, 232, 240, 255), width=6)

    # Center screw
    draw.ellipse([250, 244, 262, 256], fill=(245, 158, 11, 255))

    # Stars
    for sx, sy in [(165, 240), (347, 240)]:
        draw.polygon([(sx, sy-9), (sx+3, sy-3), (sx+9, sy), (sx+4, sy+4), (sx+6, sy+10), (sx, sy+6), (sx-6, sy+10), (sx-4, sy+4), (sx-9, sy), (sx-3, sy-3)], fill=(251, 191, 36, 255))

    logo_path = os.path.join(BASE_DIR, "logo.png")
    img.save(logo_path, "PNG")

    logo_jpg = os.path.join(BASE_DIR, "logo.jpg")
    img.convert("RGB").save(logo_jpg, "JPEG", quality=90, optimize=True)

    fav = img.resize((64, 64), Image.Resampling.LANCZOS)
    fav.save(os.path.join(BASE_DIR, "favicon.png"), "PNG")
    print("[SUCCESS] logo.png, logo.jpg, favicon.png generated")


def draw_right_aligned(draw, right_x, y, text, font, fill):
    shaped = shape_arabic_word(text)
    bbox = draw.textbbox((0, 0), shaped, font=font)
    w = bbox[2] - bbox[0]
    draw.text((right_x - w, y), shaped, font=font, fill=fill)


def draw_centered(draw, box_left, box_right, y, text, font, fill):
    shaped = shape_arabic_word(text)
    bbox = draw.textbbox((0, 0), shaped, font=font)
    w = bbox[2] - bbox[0]
    x = box_left + (box_right - box_left - w) // 2
    draw.text((x, y), shaped, font=font, fill=fill)


def create_og_image():
    w, h = 1200, 630
    # Base dark obsidian background (RGB, no alpha overwrite bug!)
    base = Image.new("RGBA", (w, h), (11, 15, 25, 255))

    # Create soft radial glow overlay using proper alpha_composite
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glow)
    for step in range(35, 0, -1):
        r = step * 11
        # Soft blue glow on right
        g_draw.ellipse([930 - r, 315 - r, 930 + r, 315 + r], fill=(37, 99, 235, 3))
        # Soft gold glow on left
        g_draw.ellipse([260 - r, 315 - r, 260 + r, 315 + r], fill=(245, 158, 11, 2))
    base = Image.alpha_composite(base, glow)

    draw = ImageDraw.Draw(base)

    # Card frame border
    draw.rounded_rectangle([24, 24, w - 24, h - 24], radius=24, outline=(45, 59, 91, 255), width=3)

    # Top gradient accent bar
    for x in range(40, w - 40):
        ratio = (x - 40) / (w - 80)
        r_c = int(37 + ratio * (245 - 37))
        g_c = int(99 + ratio * (158 - 99))
        b_c = int(235 + ratio * (11 - 235))
        draw.line([x, 24, x, 31], fill=(r_c, g_c, b_c, 255))

    # Paste Logo on the Left side (since Arabic text is Right-aligned!)
    logo = Image.open(os.path.join(BASE_DIR, "logo.png"))
    logo_resized = logo.resize((350, 350), Image.Resampling.LANCZOS)
    base.paste(logo_resized, (85, 140), logo_resized)

    # Load clean Arabic-supporting Windows font (Segoe UI Bold / Tahoma Bold / Arial Bold)
    font_title = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 58)
    font_sub1 = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 34)
    font_sub2 = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 32)
    font_desc = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 23)
    font_badge = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 21)
    font_feat = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 21)

    right_edge = 1120

    # Top Pill Badge (Right-aligned)
    badge_left, badge_right = 760, right_edge
    draw.rounded_rectangle([badge_left, 78, badge_right, 130], radius=26, fill=(30, 41, 59, 255), outline=(245, 158, 11, 220), width=2)
    draw_centered(draw, badge_left, badge_right, 88, "استبيان دراسة السوق الأولي", font_badge, (251, 191, 36, 255))

    # Main Headlines (Right-aligned for authentic Arabic layout)
    draw_right_aligned(draw, right_edge, 152, "منصة حِلاق | Barber SaaS", font_title, (255, 255, 255, 255))
    draw_right_aligned(draw, right_edge, 238, "النظام الذكي لإدارة صالونات الحلاقة", font_sub1, (56, 189, 248, 255))
    draw_right_aligned(draw, right_edge, 290, "والعناية بالرجل في المملكة", font_sub2, (245, 158, 11, 255))

    # Description lines
    draw_right_aligned(draw, right_edge, 362, "شاركنا رأيك في دقيقة واحدة كصاحب صالون أو مستثمر", font_desc, (203, 213, 225, 255))
    draw_right_aligned(draw, right_edge, 400, "واحصل على أسبقية التجربة المجانية فور الإطلاق الرسمي", font_desc, (148, 163, 184, 255))

    # 3 Feature Pills at the bottom right
    feats = [
        ("تنظيم المواعيد", 930, 1120),
        ("إدارة الحلاقين", 725, 915),
        ("بطاقات الولاء", 520, 710),
    ]
    for label, b_left, b_right in feats:
        draw.rounded_rectangle([b_left, 480, b_right, 542], radius=14, fill=(19, 27, 46, 255), outline=(56, 189, 248, 140), width=2)
        draw_centered(draw, b_left, b_right, 496, label, font_feat, (248, 250, 252, 255))

    og_png = os.path.join(BASE_DIR, "og-image.png")
    base.save(og_png, "PNG")

    og_jpg = os.path.join(BASE_DIR, "og-image.jpg")
    base.convert("RGB").save(og_jpg, "JPEG", quality=88, optimize=True)
    print("[SUCCESS] og-image.png and og-image.jpg generated, JPG size:", os.path.getsize(og_jpg))


if __name__ == "__main__":
    create_logo()
    create_og_image()
