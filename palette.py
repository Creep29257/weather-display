"""Couleurs Inky et palette PIL alignée sur leurs indices."""
from PIL import Image
from inky.inky_e673 import Inky

BLACK = Inky.BLACK
WHITE = Inky.WHITE
GREEN = Inky.GREEN
BLUE = Inky.BLUE
RED = Inky.RED
YELLOW = Inky.YELLOW

_RGB = {
    BLACK: (0, 0, 0),
    WHITE: (255, 255, 255),
    GREEN: (0, 255, 0),
    BLUE: (0, 0, 255),
    RED: (255, 0, 0),
    YELLOW: (255, 255, 0),
}


def _flat_palette():
    flat = [255, 255, 255] * 256
    for idx, rgb in _RGB.items():
        flat[idx * 3:idx * 3 + 3] = list(rgb)
    return flat


PALETTE = _flat_palette()


def new_image(width, height):
    """Image palettisée (indices = couleurs Inky), fond blanc."""
    img = Image.new("P", (width, height), WHITE)
    img.putpalette(PALETTE)
    return img
