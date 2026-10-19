"""Configuration : variables d'environnement et chemins."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Écran
WIDTH, HEIGHT = 800, 480

# Météo
API_KEY = os.getenv('OPENWEATHER_API_KEY')
LAT = os.getenv('WEATHER_LAT', '48.8566')
LON = os.getenv('WEATHER_LON', '2.3522')
LOCATION_NAME = os.getenv('LOCATION_NAME', 'Paris')

# Google Calendar
GCAL_ENABLED = os.getenv('GCAL_ENABLED', 'false').lower() == 'true'
GCAL_CALENDAR_ID = os.getenv('GCAL_CALENDAR_ID', 'primary')
GCAL_DAYS_AHEAD = int(os.getenv('GCAL_DAYS_AHEAD', '1'))
GCAL_TOKEN_PATH = os.path.expanduser(os.getenv('GCAL_TOKEN_PATH', '~/weather-display/token.json'))

# Fichiers (relatifs au dossier du script : le cron n'a plus besoin de faire cd)
ICON_DIR = os.path.join(BASE_DIR, "modernicon/weather_icons_dovora_interactive/PNG/128")
SAINTS_FILE = os.path.join(BASE_DIR, "saints.json")

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
FONT_REGULAR = os.path.join(FONT_DIR, "DejaVuSans.ttf")
FONT_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
