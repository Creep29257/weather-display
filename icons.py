"""Chargement des icônes météo et recolorisation en aplats 6 couleurs."""
import colorsys
import os
from functools import lru_cache

from PIL import Image, ImageFilter

import config
from palette import BLACK, WHITE, YELLOW, BLUE, RED, GREEN, PALETTE

# Seuils à ajuster selon les icônes
ALPHA_MIN = 110      # en dessous : transparent
SAT_COLOR = 0.22     # au-dessus : pixel coloré
VAL_DARK = 0.74      # gris plus sombre : noir


def _pick_color(hue, sat, val, is_edge):
    if sat > SAT_COLOR and val > 0.35:
        if 25 <= hue <= 75:
            return YELLOW
        if 160 <= hue <= 270:
            return BLUE
        if hue < 20 or hue > 340:
            return RED
        return GREEN
    # gris : contour ou zone sombre -> noir, corps clair -> blanc
    return BLACK if (val < VAL_DARK or is_edge) else WHITE


def _convert(path, size):
    im = Image.open(path).convert("RGBA").resize((size, size), Image.LANCZOS)
    alpha = im.getchannel("A").point(lambda v: 255 if v > ALPHA_MIN else 0)
    inner = alpha.filter(ImageFilter.MinFilter(3))  # alpha érodé -> détecte le bord

    out = Image.new("P", (size, size), WHITE)
    out.putpalette(PALETTE)
    px, ap, ip, op = im.load(), alpha.load(), inner.load(), out.load()

    for y in range(size):
        for x in range(size):
            if ap[x, y] == 0:
                continue
            r, g, b, _ = px[x, y]
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            op[x, y] = _pick_color(h * 360, s, v, ip[x, y] == 0)
    return out, alpha


@lru_cache(maxsize=None)
def load_icon(code, size):
    """Retourne (image palettisée, masque) ; mis en cache par (code, taille)."""
    return _convert(os.path.join(config.ICON_DIR, f"{code}.png"), size)
