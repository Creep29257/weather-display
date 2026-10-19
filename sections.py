"""Zones de l'écran : en-tête, heures, 4 jours, agenda, pied de page."""
from datetime import datetime, timedelta

import config
from palette import BLACK, WHITE, BLUE, GREEN, YELLOW, RED

# Mise en page
HOURS_COUNT = 18
HOURS_PER_ROW = 9
AGENDA_X = 500
AGENDA_MAX_EVENTS = 10
AGENDA_TITLE_MAX = 28


def draw_error(c):
    c.text((10, 200), "Erreur météo", RED, 'large')


def draw_header(c, w, saint):
    now = datetime.now()
    c.text((10, 10), now.strftime("%A %d %B %Y").capitalize(), BLACK, 'large')

    # lever / coucher, phase de lune, saint
    sunrise = datetime.fromtimestamp(w['current']['sunrise'])
    sunset = datetime.fromtimestamp(w['current']['sunset'])
    x = 10
    c.icon(x, 38, "01d", 24)
    x += 28
    txt = f"{sunrise.strftime('%H:%M')}/{sunset.strftime('%H:%M')}"
    c.text((x, 40), txt, BLUE, 'medium')
    x += c.text_width(txt, 'medium') + 14

    if w.get('daily'):
        c.moon(x + 9, 50, 9, w['daily'][0].get('moon_phase', 0))
        x += 28
    if saint:
        c.text((x, 40), f"| {saint}", BLUE, 'medium')

    # météo actuelle (en haut à droite)
    cur = w['current']
    c.icon(660, 2, cur['weather'][0]['icon'], 50)
    c.text((590, 52), f"{int(cur['temp'])}°C ({int(cur['feels_like'])}°)", BLACK, 'large')
    c.line([(0, 78), (800, 78)])


def draw_hourly(c, w):
    c.text((10, 82), "PROCHAINES HEURES", BLACK, 'small')
    x0, y0, box_w, box_h = 5, 95, 85, 70

    for idx, h in enumerate(w['hourly'][:HOURS_COUNT]):
        row, col = divmod(idx, HOURS_PER_ROW)
        x, y = x0 + col * box_w, y0 + row * box_h
        cx = x + 49

        c.text_centered(cx, y, datetime.fromtimestamp(h['dt']).strftime('%Hh'))
        c.icon(x + 29, y + 11, h['weather'][0]['icon'], 40)
        c.text_centered(cx, y + 54, f"{round(h['temp'])}° {int(h.get('pop', 0) * 100)}%")

    c.line([(0, 245), (800, 245)])


def _temp_color(tmax):
    if tmax < 5:
        return BLUE
    if tmax < 15:
        return GREEN
    if tmax < 25:
        return YELLOW
    return RED


def _draw_temp_bar(c, x, y, tmin, tmax, width=150, height=18):
    """Barre de températures sur une échelle de -10 à +40 °C."""
    c.rect([x, y, x + width, y + height], outline=BLACK, fill=WHITE)

    def pos(t):
        return max(2, min(int(((t + 10) / 50) * width), width - 2))

    c.rect([x + pos(tmin), y + 2, x + pos(tmax), y + height - 2], fill=_temp_color(tmax))


def draw_daily(c, w):
    c.text((10, 249), "4 JOURS", BLACK, 'medium')
    y = 270

    for d in w['daily'][1:5]:
        dt = datetime.fromtimestamp(d['dt'])
        tmin, tmax = round(d['temp']['min']), round(d['temp']['max'])
        pop = int(d.get('pop', 0) * 100)
        wind = round(d['wind_speed'] * 3.6)

        c.icon(10, y, d['weather'][0]['icon'], 42)
        c.text((58, y + 12), dt.strftime('%a %d/%m'))

        bx, bw = 135, 150
        _draw_temp_bar(c, bx, y + 12, tmin, tmax, bw)
        c.text((bx + bw + 8, y + 12), f"{tmin}°  -  {tmax}°")

        c.icon(bx + bw + 80, y + 10, "10d", 24)
        c.text((bx + bw + 105, y + 12), f"{pop}%", BLACK, 'tiny')
        c.icon(bx + bw + 140, y + 10, "50d", 24)
        c.text((bx + bw + 165, y + 12), f"{wind}", BLACK, 'tiny')

        y += 47


def _date_label(dt):
    today = datetime.now().strftime('%d/%m')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%d/%m')
    key = dt.strftime('%d/%m')
    if key == today:
        return "Aujourd'hui"
    if key == tomorrow:
        return "Demain"
    return dt.strftime('%A %d/%m').capitalize()


def draw_agenda(c, events):
    c.line([(AGENDA_X - 5, 245), (AGENDA_X - 5, 470)])
    c.text((AGENDA_X, 249), "AGENDA", BLACK, 'medium')

    if not events:
        c.text((AGENDA_X, 270), "Aucun événement", BLACK, 'tiny')
        return

    y, current_date, shown = 270, None, 0
    for e in events:
        if shown >= AGENDA_MAX_EVENTS:
            break

        key = e['datetime'].strftime('%d/%m')
        if key != current_date:
            if current_date is not None:
                y += 3
            c.text((AGENDA_X, y), f"▸ {_date_label(e['datetime'])}", BLACK, 'small')
            y += 18
            current_date = key

        c.text((AGENDA_X, y), f"  {e['time']} {e['title'][:AGENDA_TITLE_MAX]}", BLACK, 'tiny')
        y += 18
        shown += 1
        if y > 460:
            break


def draw_footer(c):
    txt = f"{datetime.now().strftime('%d/%m %H:%M')} • {config.LOCATION_NAME}"
    c.text_right(790, 462, txt, BLACK, 'tiny')
