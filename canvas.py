"""Primitives de dessin : texte, lignes, icônes, lune."""
import math

from PIL import ImageDraw, ImageFont

import config
from icons import load_icon
from palette import BLACK, WHITE, YELLOW, new_image


def _font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


class Canvas:
    def __init__(self):
        self.img = new_image(config.WIDTH, config.HEIGHT)
        self.draw = ImageDraw.Draw(self.img)
        self.fonts = {
            'large': _font(config.FONT_BOLD, 24),
            'medium': _font(config.FONT_REGULAR, 18),
            'small': _font(config.FONT_REGULAR, 14),
            'tiny': _font(config.FONT_REGULAR, 12),
        }

    # --- texte ---
    def text(self, xy, s, fill=BLACK, font='small'):
        self.draw.text(xy, s, fill=fill, font=self.fonts[font])

    def text_width(self, s, font='small'):
        return int(self.draw.textlength(s, font=self.fonts[font]))

    def text_centered(self, cx, y, s, fill=BLACK, font='small'):
        self.text((cx - self.text_width(s, font) // 2, y), s, fill, font)

    def text_right(self, right, y, s, fill=BLACK, font='small'):
        self.text((right - self.text_width(s, font), y), s, fill, font)

    # --- formes ---
    def line(self, points, fill=BLACK, width=2):
        self.draw.line(points, fill=fill, width=width)

    def rect(self, box, fill=None, outline=None, width=1):
        self.draw.rectangle(box, fill=fill, outline=outline, width=width)

    # --- icônes ---
    def icon(self, x, y, code, size=40):
        try:
            icon, mask = load_icon(code, size)
            self.img.paste(icon, (x, y), mask)
        except Exception:
            self.rect([x, y, x + size, y + size], fill=WHITE, outline=BLACK, width=2)
            self.text((x + size // 3, y + size // 4), "?")

    def moon(self, cx, cy, r, phase):
        """Phase de lune dessinée (0 = nouvelle, 0.5 = pleine)."""
        self.draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BLACK)
        k = math.cos(2 * math.pi * phase)  # 1 = nouvelle lune, -1 = pleine lune
        for dy in range(-r + 1, r):
            w = math.sqrt(max(r * r - dy * dy, 0))
            if phase < 0.5:   # croissante : éclairée à droite
                x0, x1 = cx + k * w, cx + w
            else:             # décroissante : éclairée à gauche
                x0, x1 = cx - w, cx - k * w
            if x1 - x0 >= 1:
                self.draw.line([(round(x0), cy + dy), (round(x1), cy + dy)], fill=YELLOW)
        self.draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=BLACK)
