import os
import json
import urllib.request
import urllib.parse
import threading
import datetime
import zoneinfo
from gi.repository import GLib

WMO_CONDITIONS = {
    0: ('Clear Sky', 'clear-day', 'clear-night'),
    1: ('Mainly Clear', 'clear-day', 'clear-night'),
    2: ('Partly Cloudy', 'partly-cloudy-day', 'partly-cloudy-night'),
    3: ('Overcast', 'cloudy', 'cloudy'),
    45: ('Foggy', 'fog', 'fog'),
    48: ('Depositing Rime Fog', 'fog', 'fog'),
    51: ('Light Drizzle', 'rain', 'rain'),
    53: ('Moderate Drizzle', 'rain', 'rain'),
    55: ('Dense Drizzle', 'rain', 'rain'),
    56: ('Light Freezing Drizzle', 'sleet', 'sleet'),
    57: ('Dense Freezing Drizzle', 'sleet', 'sleet'),
    61: ('Slight Rain', 'rain', 'rain'),
    63: ('Moderate Rain', 'rain', 'rain'),
    65: ('Heavy Rain', 'rain', 'rain'),
    66: ('Light Freezing Rain', 'sleet', 'sleet'),
    67: ('Heavy Freezing Rain', 'sleet', 'sleet'),
    71: ('Slight Snow', 'snow', 'snow'),
    73: ('Moderate Snow', 'snow', 'snow'),
    75: ('Heavy Snow', 'snow', 'snow'),
    77: ('Snow Grains', 'snow', 'snow'),
    80: ('Slight Rain Showers', 'rain', 'rain'),
    81: ('Moderate Rain Showers', 'rain', 'rain'),
    82: ('Violent Rain Showers', 'rain', 'rain'),
    85: ('Slight Snow Showers', 'snow', 'snow'),
    86: ('Heavy Snow Showers', 'snow', 'snow'),
    95: ('Thunderstorm', 'thunderstorms', 'thunderstorms'),
    96: ('Thunderstorm with Slight Hail', 'hail', 'hail'),
    99: ('Thunderstorm with Heavy Hail', 'hail', 'hail'),
}

DEFAULT_LOCATIONS = [
    {
        "id": "santo_andre",
        "name": "Santo André",
        "region": "SP",
        "lat": -23.6639,
        "lon": -46.5383,
        "tz": "America/Sao_Paulo",
    },
    {
        "id": "lima",
        "name": "Lima",
        "region": "Peru",
        "lat": -12.0432,
        "lon": -77.0282,
        "tz": "America/Lima",
    },
]


class WeatherEngine:
    def __init__(self, icons_dir=None):
        self.icons_dir = self._resolve_icons_dir(icons_dir)
        self.cache_file = os.path.expanduser('~/.cache/gridgets/weather_cache.json')
        self.cached_data = self._load_cache()
        self.listeners = []
        self._fetching = False
        self._retry_timer_id = None
        self.last_fetch_time = None

    def _resolve_icons_dir(self, custom_dir):
        candidates = [
            custom_dir,
            os.path.expanduser('~/temporary/dotfiles/gridgets/assets/weather/icons'),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'gridgets', 'assets', 'weather', 'icons'),
            os.path.expanduser('~/.local/share/gridgets/assets/weather/icons'),
        ]
        for c in candidates:
            if c and os.path.isdir(c):
                return os.path.abspath(c)
        return os.path.expanduser('~/temporary/dotfiles/gridgets/assets/weather/icons')

    def _load_cache(self):
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and (data.get('temperature') or data.get('locations')):
                        return data
        except Exception as err:
            print(f"[WeatherEngine] Cache load notice: {err}")
        return {}

    def _save_cache(self, data):
        try:
            cache_dir = os.path.dirname(self.cache_file)
            os.makedirs(cache_dir, exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as err:
            print(f"[WeatherEngine] Cache save error: {err}")

    def add_listener(self, callback):
        self.listeners.append(callback)
        if self.cached_data:
            callback(self.cached_data)

    def get_icon_path(self, icon_name):
        if not self.icons_dir:
            return None
        filename = f"wi_{icon_name}.svg"
        full_path = os.path.join(self.icons_dir, filename)
        if os.path.exists(full_path):
            return full_path
        fallback = os.path.join(self.icons_dir, "wi_clear-day.svg")
        return fallback if os.path.exists(fallback) else None

    def fetch_async(self, city=None, use_fahrenheit=False, on_complete=None, force=False):
        now_utc = datetime.datetime.now(datetime.timezone.utc)

        # Smart 2-second live refresh:
        # If cache exists and network was fetched < 30s ago, update real-time local times and notify immediately
        if not force and self.cached_data and self.last_fetch_time:
            elapsed = (now_utc - self.last_fetch_time).total_seconds()
            if elapsed < 30:
                locations = self.cached_data.get('locations', [])
                tz_map = {
                    "santo_andre": "America/Sao_Paulo",
                    "lima": "America/Lima"
                }
                for loc in locations:
                    tz_name = loc.get('tz') or tz_map.get(loc.get('id', ''), "UTC")
                    try:
                        tz_obj = zoneinfo.ZoneInfo(tz_name)
                        loc['time'] = now_utc.astimezone(tz_obj).strftime("%H:%M")
                    except Exception:
                        pass
                self.cached_data['updated_at'] = now_utc.strftime("%H:%M:%S")
                GLib.idle_add(self._notify_listeners, self.cached_data)
                if on_complete:
                    GLib.idle_add(on_complete)
                return

        if self._fetching:
            return
        self._fetching = True

        def _thread_target():
            try:
                temp_unit = "fahrenheit" if use_fahrenheit else "celsius"
                unit_symbol = "°F" if use_fahrenheit else "°C"
                now_utc = datetime.datetime.now(datetime.timezone.utc)

                locations_data = []

                for loc in DEFAULT_LOCATIONS:
                    lat = loc["lat"]
                    lon = loc["lon"]
                    city_id = loc["id"]
                    city_name = loc["name"]
                    region = loc["region"]
                    tz_name = loc["tz"]

                    # Localized time
                    try:
                        tz_obj = zoneinfo.ZoneInfo(tz_name)
                        local_time_str = now_utc.astimezone(tz_obj).strftime("%H:%M")
                    except Exception:
                        local_time_str = now_utc.strftime("%H:%M")

                    weather_url = (
                        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
                        f"&current_weather=true"
                        f"&daily=weathercode,temperature_2m_max,temperature_2m_min&temperature_unit={temp_unit}&timezone=auto"
                    )
                    req = urllib.request.Request(weather_url, headers={'User-Agent': 'Gridgets-Qtile/1.0'})
                    with urllib.request.urlopen(req, timeout=12) as resp:
                        w_data = json.loads(resp.read().decode('utf-8'))

                    curr = w_data.get('current_weather', {})
                    wmo_code = curr.get('weathercode', 0)
                    is_day = curr.get('is_day', 1) == 1
                    temp = curr.get('temperature', 0)

                    condition_info = WMO_CONDITIONS.get(wmo_code, ('Clear', 'clear-day', 'clear-night'))
                    condition_text = condition_info[0]
                    icon_base = condition_info[1] if is_day else condition_info[2]
                    icon_path = self.get_icon_path(icon_base)

                    daily = w_data.get('daily', {})
                    temp_max = daily.get('temperature_2m_max', [temp])[0] if daily.get('temperature_2m_max') else temp
                    temp_min = daily.get('temperature_2m_min', [temp])[0] if daily.get('temperature_2m_min') else temp

                    loc_item = {
                        'id': city_id,
                        'city': city_name,
                        'region': region,
                        'time': local_time_str,
                        'temperature': f"{round(temp)}{unit_symbol}",
                        'temp_raw': temp,
                        'high': f"{round(temp_max)}{unit_symbol}",
                        'low': f"{round(temp_min)}{unit_symbol}",
                        'condition': condition_text,
                        'icon_path': icon_path,
                        'is_day': is_day,
                    }
                    locations_data.append(loc_item)

                # Combine into unified multi-city payload
                primary = locations_data[0] if locations_data else {}
                result = {
                    'status': 'ok',
                    'city': primary.get('city', 'Santo André'),
                    'temperature': primary.get('temperature', '--°'),
                    'high': primary.get('high', '--°'),
                    'low': primary.get('low', '--°'),
                    'condition': primary.get('condition', 'Clear'),
                    'icon_path': primary.get('icon_path'),
                    'locations': locations_data,
                    'updated_at': now_utc.strftime("%H:%M:%S"),
                }

                self.last_fetch_time = now_utc
                self.cached_data = result
                self._save_cache(result)
                self._retry_timer_id = None

                GLib.idle_add(self._notify_listeners, result)
            except Exception as e:
                print(f"[WeatherEngine] Fetch error: {e}")
                if not self.cached_data:
                    error_payload = {
                        'status': 'error',
                        'city': 'Santo André',
                        'temperature': '--°',
                        'high': '--°',
                        'low': '--°',
                        'condition': 'Retrying...',
                        'locations': [],
                    }
                    GLib.idle_add(self._notify_listeners, error_payload)

                GLib.idle_add(self._schedule_retry, city, use_fahrenheit)
            finally:
                self._fetching = False
                if on_complete:
                    GLib.idle_add(on_complete)

        t = threading.Thread(target=_thread_target, daemon=True)
        t.start()

    def _schedule_retry(self, city, use_fahrenheit):
        if not self._retry_timer_id:
            self._retry_timer_id = GLib.timeout_add_seconds(15, self._retry_fetch, city, use_fahrenheit)
        return False

    def _retry_fetch(self, city, use_fahrenheit):
        self._retry_timer_id = None
        self.fetch_async(city, use_fahrenheit)
        return False

    def _notify_listeners(self, data):
        for cb in list(self.listeners):
            try:
                cb(data)
            except Exception as e:
                print(f"[WeatherEngine] Callback error: {e}")
        return False


weather_engine = WeatherEngine()
