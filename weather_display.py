#!/usr/bin/env python3
"""Station météo e-ink (Inky Impression 7.3") - v0.15

Usage :
    python3 weather_display.py              # affiche sur l'écran
    python3 weather_display.py --preview    # écrit preview.png, sans toucher l'écran
    python3 weather_display.py --preview /tmp/test.png
"""
import argparse
import locale
import sys
import warnings

import config
import data
import sections
from canvas import Canvas

warnings.filterwarnings("ignore", message="Busy Wait")
try:
    locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
except Exception:
    pass


def build_image(weather, events, saint=""):
    """Compose l'image complète (palettisée Inky) à partir des données."""
    c = Canvas()
    if not weather:
        sections.draw_error(c)
    else:
        sections.draw_header(c, weather, saint)
        sections.draw_hourly(c, weather)
        sections.draw_daily(c, weather)
        sections.draw_agenda(c, events)
    sections.draw_footer(c)
    return c.img


def show_on_inky(img):
    from inky.inky_e673 import Inky
    inky = Inky()
    inky.set_image(img)
    inky.show()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--preview", nargs="?", const="preview.png", metavar="FICHIER",
                        help="sauvegarde un PNG au lieu d'envoyer à l'écran")
    args = parser.parse_args()

    if not config.API_KEY:
        print("ERREUR: Configure .env avec OPENWEATHER_API_KEY")
        sys.exit(1)

    img = build_image(data.fetch_weather(), data.fetch_calendar(), data.get_saint())

    if args.preview:
        img.convert("RGB").save(args.preview)
        print(f"✅ Aperçu écrit : {args.preview}")
        return

    try:
        show_on_inky(img)
        print("✅ Affichage OK")
    except Exception as e:
        print(f"❌ Erreur affichage: {e}")


if __name__ == "__main__":
    main()
