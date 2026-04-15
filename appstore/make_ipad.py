#!/usr/bin/env python3
"""
Convert iPhone App Store screenshots to iPad Pro 12.9"/13" format.
Target: 2048 × 2732 px
"""

from PIL import Image, ImageDraw, ImageFilter
import os

CANVAS_W, CANVAS_H = 2048, 2732

# App-content crop inside the iPhone mockup (detected by pixel scan)
PHONE_CROP = (200, 660, 1084, 2547)   # (x1, y1, x2, y2) → 884 × 1887 px

# iPad Pro body
PAD_W, PAD_H = 1860, 2600
PAD_X = (CANVAS_W - PAD_W) // 2      # 94
PAD_Y = (CANVAS_H - PAD_H) // 2      # 66
PAD_CORNER = 90

BEZEL = 54                             # aluminum bezel width

SCREEN_X1 = PAD_X + BEZEL
SCREEN_Y1 = PAD_Y + BEZEL
SCREEN_X2 = PAD_X + PAD_W - BEZEL
SCREEN_Y2 = PAD_Y + PAD_H - BEZEL
SCREEN_W  = SCREEN_X2 - SCREEN_X1    # 1752
SCREEN_H  = SCREEN_Y2 - SCREEN_Y1    # 2492
SCREEN_CORNER = 24

IPAD_BODY_HI = (205, 205, 212)
IPAD_BODY_LO = (175, 175, 183)
IPAD_EDGE    = (140, 140, 148)
SCREEN_RING  = ( 45,  45,  50)

BG_GRADIENTS = [
    ((255, 126,  95), (255, 179, 129)),
    ((130,  87, 229), (174, 129, 251)),
    (( 56, 190, 172), ( 89, 214, 199)),
    ((255, 173,  44), (255, 210,  80)),
    ((233,  80, 120), (254, 139, 169)),
    (( 71, 170, 246), (119, 201, 254)),
]


def gradient_image(w, h, top, bot):
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(h - 1, 1)
        r = round(top[0] + t * (bot[0] - top[0]))
        g = round(top[1] + t * (bot[1] - top[1]))
        b = round(top[2] + t * (bot[2] - top[2]))
        draw.line([(0, y), (w - 1, y)], fill=(r, g, b))
    return img


def make_ipad_screenshot(app_content: Image.Image, bg_top, bg_bot) -> Image.Image:
    """Composite app_content (RGB) into an iPad Pro frame on a gradient background."""

    # ── 1. Scale app content to fill iPad screen (width-fit, centre-crop height) ──
    phone_w, phone_h = app_content.size
    scale  = SCREEN_W / phone_w
    new_w  = SCREEN_W
    new_h  = round(phone_h * scale)
    scaled = app_content.resize((new_w, new_h), Image.LANCZOS)
    crop_y = (new_h - SCREEN_H) // 2
    screen_img = scaled.crop((0, crop_y, SCREEN_W, crop_y + SCREEN_H))

    # ── 2. Gradient background ────────────────────────────────────────────────
    canvas = gradient_image(CANVAS_W, CANVAS_H, bg_top, bg_bot).convert("RGBA")

    # ── 3. Drop shadow ────────────────────────────────────────────────────────
    shadow = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    SO = 20
    sd.rounded_rectangle(
        (PAD_X + SO, PAD_Y + SO, PAD_X + PAD_W + SO, PAD_Y + PAD_H + SO),
        radius=PAD_CORNER, fill=(0, 0, 0, 100)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(30))
    canvas = Image.alpha_composite(canvas, shadow)

    # ── 4. iPad body (silver, rounded rect) ───────────────────────────────────
    body_grad = gradient_image(PAD_W, PAD_H, IPAD_BODY_HI, IPAD_BODY_LO).convert("RGBA")
    body_mask = Image.new("L", (PAD_W, PAD_H), 0)
    ImageDraw.Draw(body_mask).rounded_rectangle(
        (0, 0, PAD_W, PAD_H), radius=PAD_CORNER, fill=255
    )
    body_layer = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    body_layer.paste(body_grad, (PAD_X, PAD_Y), mask=body_mask)
    canvas = Image.alpha_composite(canvas, body_layer)

    # ── 5. App content pasted INTO the screen area (over the silver body) ─────
    screen_mask = Image.new("L", (SCREEN_W, SCREEN_H), 0)
    ImageDraw.Draw(screen_mask).rounded_rectangle(
        (0, 0, SCREEN_W, SCREEN_H), radius=SCREEN_CORNER, fill=255
    )
    canvas_rgb = canvas.convert("RGB")
    canvas_rgb.paste(screen_img, (SCREEN_X1, SCREEN_Y1), mask=screen_mask)
    canvas = canvas_rgb.convert("RGBA")

    # ── 6. Thin dark ring around the screen (outline only, not fill) ──────────
    ring_layer = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    ImageDraw.Draw(ring_layer).rounded_rectangle(
        (SCREEN_X1, SCREEN_Y1, SCREEN_X2, SCREEN_Y2),
        radius=SCREEN_CORNER,
        outline=SCREEN_RING + (255,),
        width=5
    )
    canvas = Image.alpha_composite(canvas, ring_layer)

    # ── 7. Outer edge line ────────────────────────────────────────────────────
    edge_layer = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    ImageDraw.Draw(edge_layer).rounded_rectangle(
        (PAD_X, PAD_Y, PAD_X + PAD_W, PAD_Y + PAD_H),
        radius=PAD_CORNER,
        outline=IPAD_EDGE + (200,),
        width=3
    )
    canvas = Image.alpha_composite(canvas, edge_layer)

    # ── 8. Front camera dot ───────────────────────────────────────────────────
    cam_layer = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cam_layer)
    cx, cy, cr = CANVAS_W // 2, PAD_Y + BEZEL // 2, 10
    cd.ellipse((cx - cr, cy - cr, cx + cr, cy + cr), fill=(28, 28, 33, 255))
    cd.ellipse((cx - 5,  cy - 5,  cx + 5,  cy + 5),  fill=(55, 55, 65, 255))
    canvas = Image.alpha_composite(canvas, cam_layer)

    # ── 9. Side buttons ───────────────────────────────────────────────────────
    btn_layer = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(btn_layer)
    bc = (155, 155, 163, 255)
    # Power – right edge top
    bd.rounded_rectangle((PAD_X + PAD_W - 6, PAD_Y + 300,
                           PAD_X + PAD_W + 6, PAD_Y + 400), radius=4, fill=bc)
    # Volume – right edge
    for vy in (PAD_Y + 520, PAD_Y + 640):
        bd.rounded_rectangle((PAD_X + PAD_W - 6, vy,
                               PAD_X + PAD_W + 6, vy + 100), radius=4, fill=bc)
    canvas = Image.alpha_composite(canvas, btn_layer)

    return canvas.convert("RGB")


# ── Run ───────────────────────────────────────────────────────────────────────
INPUT_DIR  = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(INPUT_DIR, "ipad")
os.makedirs(OUTPUT_DIR, exist_ok=True)

sources = sorted(
    f for f in os.listdir(INPUT_DIR)
    if f.startswith("appstore_") and f.endswith(".png")
)

px1, py1, px2, py2 = PHONE_CROP

for idx, fname in enumerate(sources):
    src = Image.open(os.path.join(INPUT_DIR, fname)).convert("RGB")
    app_crop = src.crop(PHONE_CROP)   # 884 × 1887 – just the screen content

    top_col, bot_col = BG_GRADIENTS[idx]
    result = make_ipad_screenshot(app_crop, top_col, bot_col)

    out_name = fname.replace("appstore_", "ipad_")
    result.save(os.path.join(OUTPUT_DIR, out_name), "PNG", optimize=True)
    print(f"{fname} → {out_name}")

print(f"\nDone — saved to {OUTPUT_DIR}/")
