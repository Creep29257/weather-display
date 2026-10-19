"""Sources de données : météo OpenWeather, Google Calendar, saint du jour."""
import json
from datetime import datetime, timedelta

import requests

import config

_MONTHS = ['january', 'february', 'march', 'april', 'may', 'june',
           'july', 'august', 'september', 'october', 'november', 'december']


def fetch_weather():
    try:
        r = requests.get("https://api.openweathermap.org/data/3.0/onecall", params={
            'lat': config.LAT, 'lon': config.LON,
            'appid': config.API_KEY, 'units': 'metric', 'lang': 'fr',
            'exclude': 'minutely',
        }, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Erreur météo: {e}")
        return None


def fetch_calendar():
    """Liste d'événements {'time', 'datetime', 'title'} ; [] si désactivé ou en erreur."""
    if not config.GCAL_ENABLED:
        return []
    try:
        import os
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        creds = None
        if os.path.exists(config.GCAL_TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(
                config.GCAL_TOKEN_PATH,
                ['https://www.googleapis.com/auth/calendar.readonly'])
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        if not creds or not creds.valid:
            return []

        service = build('calendar', 'v3', credentials=creds)
        now = datetime.now().astimezone()
        start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        end = (now + timedelta(days=config.GCAL_DAYS_AHEAD)).replace(
            hour=23, minute=59, second=59, microsecond=0).isoformat()

        items = service.events().list(
            calendarId=config.GCAL_CALENDAR_ID,
            timeMin=start, timeMax=end,
            maxResults=15, singleEvents=True, orderBy='startTime',
        ).execute().get('items', [])

        events = []
        for e in items:
            s = e['start'].get('dateTime', e['start'].get('date'))
            if 'T' in s:
                dt = datetime.fromisoformat(s.replace('Z', '+00:00'))
                time_str = dt.strftime('%H:%M')
            else:
                dt = datetime.fromisoformat(s)
                time_str = 'Jour'
            events.append({'time': time_str, 'datetime': dt, 'title': e.get('summary', '')})
        return events
    except Exception as e:
        print(f"Erreur calendar: {e}")
        return []


def get_saint():
    try:
        with open(config.SAINTS_FILE, 'r') as f:
            saints = json.load(f)
        now = datetime.now()
        s = saints[_MONTHS[now.month - 1]][now.day - 1]
        return f"{s[1]} {s[0]}" if s[1] else s[0]
    except Exception:
        return ""
