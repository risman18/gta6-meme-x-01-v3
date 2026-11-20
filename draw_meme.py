#!/usr/bin/env python3
"""Draw the v3 meme for make.fun bounty gta6-meme-x-01.

Concept: "TIME SERVED" -- a Leonida State Prison release form.
Every GTA fan just finished a 13-year sentence waiting for GTA 6
(GTA V: 17 Sep 2013 -> GTA VI: 19 Nov 2026). The make.fun ghost
mascot appears as a fellow inmate in an orange jumpsuit, holding
its magenta star coin. All artwork is drawn programmatically with
Pillow; no stock images, no copied assets.
"""
import math
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
OUT = "meme.png"

BLACK = "/usr/share/fonts/truetype/noto/NotoSans-Black.ttf"
BOLD = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

CREAM = (255, 243, 214)
INK = (38, 32, 28)
RED = (210, 31, 43)
MAGENTA = (226, 0, 122)
ORANGE = (255, 122, 26)
DARK = (36, 16, 64)
WHITE = (255, 255, 255)


def font(path, size):
    return ImageFont.truetype(path, size)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient(size, stops):
    """Vertical gradient through (position, color) stops."""
    img = Image.new("RGB", size)
    d = ImageDraw.Draw(img)
    for y in range(size[1]):
        t = y / (size[1] - 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                f = 0 if p1 == p0 else (t - p0) / (p1 - p0)
                d.line([(0, y), (size[0], y)], fill=lerp(c0, c1, f))
                break
    return img


def text_center(d, cx, y, s, fnt, fill, stroke=0, stroke_fill=(0, 0, 0)):
    w = d.textlength(s, font=fnt)
    d.text((cx - w / 2, y), s, font=fnt, fill=fill,
           stroke_width=stroke, stroke_fill=stroke_fill)
    return w


def text_tracked(d, cx, y, s, fnt, fill, tracking=6):
    """Centered text with extra letter spacing."""
    widths = [d.textlength(ch, font=fnt) for ch in s]
    total = sum(widths) + tracking * (len(s) - 1)
    x = cx - total / 2
    for ch, w in zip(s, widths):
        d.text((x, y), ch, font=fnt, fill=fill)
        x += w + tracking


def sparkle_points(cx, cy, r, inner=0.30):
    pts = []
    for i in range(8):
        ang = math.pi / 2 + i * math.pi / 4
        rr = r if i % 2 == 0 else r * inner
        pts.append((cx + rr * math.cos(ang), cy - rr * math.sin(ang)))
    return pts


def star_points(cx, cy, r_out, r_in, rot=-math.pi / 2):
    pts = []
    for i in range(10):
        ang = rot + i * math.pi / 5
        rr = r_out if i % 2 == 0 else r_in
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    return pts


def ghost_layer():
    """The make.fun ghost: white body, black outline, sparkle eyes,
    little round hand holding a magenta coin with a white star,
    wearing an orange prison jumpsuit stencilled 013."""
    gw, gh = 300, 320
    layer = Image.new("RGBA", (gw, gh), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # --- body silhouette (dome top, wavy hem) ---
    cx = 150
    top, bot = 18, 292
    r = 92  # half-width of the dome
    # dome arc from left to right over the top
    pts = []
    for deg in range(180, -1, -4):
        a = math.radians(deg)
        pts.append((cx + r * math.cos(a), 108 - r * math.sin(a)))
    # sides down to the hem
    pts.append((cx + r, bot - 14))
    # wavy hem: three scallops back to the left side
    for x in range(cx + r, cx - r - 1, -6):
        t = (x - (cx - r)) / (2 * r)  # 0..1 across
        wave = 12 * abs(math.sin(t * math.pi * 3))
        pts.append((x, bot - wave))
    pts.append((cx - r, bot - 14))
    d.polygon(pts, fill=WHITE + (255,), outline=(0, 0, 0, 255), width=6)
    # re-fill without the outline eating the interior edge
    d.polygon(pts, fill=WHITE + (255,))
    d.line(pts, fill=(0, 0, 0, 255), width=6, joint="curve")

    # --- orange prison jumpsuit over the lower half ---
    suit = Image.new("RGBA", (gw, gh), (0, 0, 0, 0))
    sd = ImageDraw.Draw(suit)
    sd.rectangle([cx - r + 4, 205, cx + r - 4, bot], fill=ORANGE + (255,))
    sd.rectangle([cx - r + 4, 205, cx + r - 4, 222], fill=(230, 90, 10, 255))
    # stencil number
    num = font(MONO, 34)
    sd.text((cx - 26, 238), "013", font=num, fill=(255, 255, 255, 255))
    # clip the suit to the body silhouette
    mask = Image.new("L", (gw, gh), 0)
    md = ImageDraw.Draw(mask)
    md.polygon(pts, fill=255)
    layer.paste(suit, (0, 0), Image.composite(suit, Image.new("RGBA", (gw, gh), (0, 0, 0, 0)), mask))
    d = ImageDraw.Draw(layer)
    # re-draw the body outline so the suit edge is clean
    d.line(pts, fill=(0, 0, 0, 255), width=6, joint="curve")

    # --- sparkle eyes ---
    d.polygon(sparkle_points(cx - 38, 108, 17), fill=(0, 0, 0, 255))
    d.polygon(sparkle_points(cx + 38, 108, 17), fill=(0, 0, 0, 255))
    # --- little smile ---
    d.arc([cx - 16, 138, cx + 16, 162], start=15, end=165,
          fill=(0, 0, 0, 255), width=5)

    # --- arm + round hand holding the magenta coin (left side,
    # held out toward the release form so it reads on cream) ---
    # arm from the body's left edge to the coin
    d.line([(cx - 84, 196), (cx - 104, 168)], fill=(0, 0, 0, 255), width=12)
    d.line([(cx - 84, 196), (cx - 104, 168)], fill=WHITE + (255,), width=6)
    # coin
    coin_c = (cx - 112, 146)
    d.ellipse([coin_c[0] - 28, coin_c[1] - 28, coin_c[0] + 28, coin_c[1] + 28],
              fill=MAGENTA + (255,), outline=(0, 0, 0, 255), width=5)
    d.polygon(star_points(coin_c[0], coin_c[1], 18, 8), fill=WHITE + (255,))
    # hand: small white circle over the coin's lower edge
    d.ellipse([coin_c[0] - 12, coin_c[1] + 8, coin_c[0] + 12, coin_c[1] + 32],
              fill=WHITE + (255,), outline=(0, 0, 0, 255), width=4)
    return layer


def palm(d, x, y_top, h, lean, color):
    """A simple palm-tree silhouette: curved trunk + drooping fronds."""
    x0, y0 = x, y_top + h
    x1 = x + lean
    # trunk as a tapering polygon along a quadratic curve
    pts_l, pts_r = [], []
    for i in range(13):
        t = i / 12
        bx = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * (x0 + lean * 0.3) + t * t * x1
        by = y0 - t * h
        wdt = 13 * (1 - t) + 5
        pts_l.append((bx - wdt, by))
        pts_r.append((bx + wdt, by))
    d.polygon(pts_l + pts_r[::-1], fill=color)
    # fronds: bent two-segment drooping leaves, longer and thicker
    for ang in (-165, -140, -115, -90, -65, -40, -15):
        a = math.radians(ang)
        mx = x1 + 62 * math.cos(a)
        my = y_top + 30 * math.sin(a) + 4
        ex = x1 + 138 * math.cos(a)
        ey = y_top + 62 * math.sin(a) + 58
        d.line([(x1, y_top), (mx, my)], fill=color, width=14)
        d.line([(mx, my), (ex, ey)], fill=color, width=11)
    # coconuts
    d.ellipse([x1 - 12, y_top + 2, x1 + 2, y_top + 16], fill=color)
    d.ellipse([x1 + 2, y_top + 6, x1 + 16, y_top + 20], fill=color)


def stamp_layer():
    """Red 'TIME SERVED' rubber stamp, rotated, semi-transparent."""
    sw, sh = 460, 130
    layer = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    fnt = font(BLACK, 64)
    d.rectangle([10, 10, sw - 10, sh - 10], outline=RED + (225,), width=7)
    d.rectangle([22, 22, sw - 22, sh - 22], outline=RED + (225,), width=3)
    d.text((sw / 2, 32), "TIME SERVED", font=fnt, fill=RED + (228,),
           anchor="ma")
    return layer.rotate(-10, expand=True, resample=Image.BICUBIC)


def main():
    img = gradient((W, H), [
        (0.00, (24, 8, 54)),
        (0.30, (94, 27, 106)),
        (0.55, (214, 48, 120)),
        (0.75, (255, 110, 61)),
        (0.88, (64, 20, 66)),
        (1.00, (22, 8, 48)),
    ])
    d = ImageDraw.Draw(img, "RGBA")

    # sun with glow, top right
    sx, sy, sr = 838, 158, 88
    for rr, alpha in ((150, 40), (125, 70), (105, 110)):
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.ellipse([sx - rr, sy - rr, sx + rr, sy + rr],
                   fill=(255, 214, 120, alpha))
        img.paste(glow, (0, 0), glow)
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 233, 163, 255))

    # palm silhouettes at the edges
    palm(d, 6, 330, 560, 58, DARK + (255,))
    palm(d, 1006, 380, 520, -52, DARK + (255,))

    # dateline
    text_tracked(d, W // 2, 46, "LEONIDA  •  NOV 19, 2026",
                 font(BOLD, 30), WHITE + (255,), tracking=7)

    # ---- release-form card (drawn flat, then rotated -2 deg) ----
    cw, ch = 820, 500
    card = Image.new("RGBA", (cw + 80, ch + 80), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    # soft shadow
    cd.rounded_rectangle([48, 52, 48 + cw, 52 + ch], radius=26,
                         fill=(0, 0, 0, 110))
    cd.rounded_rectangle([40, 44, 40 + cw, 44 + ch], radius=26,
                         fill=CREAM + (255,))
    cd.rounded_rectangle([40, 44, 40 + cw, 44 + ch], radius=26,
                         outline=(120, 90, 40, 255), width=3)
    cx = 40 + cw // 2
    text_tracked(cd, cx, 44 + 30, "LEONIDA STATE PRISON",
                 font(MONO, 30), INK + (255,), tracking=4)
    text_center(cd, cx, 44 + 72, "RELEASE FORM", font(BLACK, 56),
                INK + (255,))
    cd.line([(40 + 70, 44 + 152), (40 + cw - 70, 44 + 152)],
            fill=INK + (255,), width=4)
    rows = [
        ("NAME:", "EVERY GTA FAN"),
        ("CRIME:", "WAITING FOR GTA 6"),
        ("SENTENCE:", "13 YEARS"),
        ("SERVED:", "2013 – 2026"),
    ]
    y = 44 + 178
    rf = font(MONO, 34)
    for label, value in rows:
        cd.text((40 + 64, y), label, font=rf, fill=(150, 40, 40, 255))
        cd.text((40 + 300, y), value, font=rf, fill=INK + (255,))
        y += 58
    # signature scrawl + clerk line
    cd.line([(40 + 64, 44 + 452), (40 + 330, 44 + 452)],
            fill=INK + (255,), width=2)
    cd.text((40 + 64, 44 + 458), "Warden L. Vance", font=font(MONO, 22),
            fill=INK + (255,))
    card = card.rotate(-2, expand=True, resample=Image.BICUBIC)
    img.paste(card, (52, 118), card)

    # ---- TIME SERVED stamp over the card's lower area ----
    # centred (420, 605): clear of the "13 YEARS" row, clear of the ghost
    stamp = stamp_layer()
    img.paste(stamp, (182, 501), stamp)

    # ---- make.fun ghost, fellow inmate, bottom right ----
    ghost = ghost_layer()
    img.paste(ghost, (722, 512), ghost)

    # ---- bottom headline + make.fun pill ----
    d = ImageDraw.Draw(img, "RGBA")
    text_center(d, W // 2, 826, "GTA VI IS OUT NOW", font(BLACK, 84),
                WHITE + (255,), stroke=3, stroke_fill=(0, 0, 0, 255))
    # pill
    pill_w, pill_h = 300, 62
    px, py = (W - pill_w) // 2, 928
    d.rounded_rectangle([px, py, px + pill_w, py + pill_h], radius=31,
                        fill=MAGENTA + (255,))
    d.rounded_rectangle([px, py, px + pill_w, py + pill_h], radius=31,
                        outline=WHITE + (255,), width=3)
    text_center(d, W // 2, py + 10, "make.fun", font(BLACK, 42),
                WHITE + (255,))

    img.convert("RGB").save(OUT, "PNG", optimize=True)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
