import os
import json
import urllib.request
import urllib.parse
import threading
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

class WeatherEngine:
    def __init__(self, icons_dir=None):
        self.icons_dir = self._resolve_icons_dir(icons_dir)
        self.cache_file = os.path.expanduser('~/.cache/gridgets/weather_cache.json')
        self.cached_data = self._load_cache()
        self.listeners = []
        self._fetching = False
        self._retry_timer_id = None

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
                    if isinstance(data, dict) and data.get('temperature'):
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

    def fetch_async(self, city="São Paulo", use_fahrenheit=False, on_complete=None):
        if self._fetching:
            return
        self._fetching = True

        def _thread_target():
            try:
                # 1. Geocoding with fallback
                clean_city = city.strip()
                search_terms = [clean_city]
                if ',' in clean_city:
                    search_terms.append(clean_city.split(',')[0].strip())
                if '-' in clean_city:
                    search_terms.append(clean_city.split('-')[0].strip())

                geo_data = None
                for term in search_terms:
                    try:
                        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(term)}&count=1&language=en&format=json"
                        req = urllib.request.Request(geo_url, headers={'User-Agent': 'Gridgets-Qtile/1.0'})
                        with urllib.request.urlopen(req, timeout=12) as resp:
                            res_json = json.loads(resp.read().decode('utf-8'))
                            if res_json.get('results'):
                                geo_data = res_json
                                break
                    except Exception:
                        continue

                if not geo_data or not geo_data.get('results'):
                    raise RuntimeError(f"Could not resolve geocoding coordinates for city: {city}")

                res = geo_data['results'][0]
                lat = res['latitude']
                lon = res['longitude']
                city_name = res.get('name', clean_city)

                # 2. Weather forecast from Open-Meteo
                temp_unit = "fahrenheit" if use_fahrenheit else "celsius"
                weather_url = (
                    f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
                    f"&current_weather=true&hourly=temperature_2m,weathercode"
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

                unit_symbol = "°F" if use_fahrenheit else "°C"
                result = {
                    'status': 'ok',
                    'city': city_name,
                    'temperature': f"{round(temp)}{unit_symbol}",
                    'temp_raw': temp,
                    'high': f"{round(temp_max)}{unit_symbol}",
                    'low': f"{round(temp_min)}{unit_symbol}",
                    'condition': condition_text,
                    'icon_path': icon_path,
                    'is_day': is_day,
                }

                self.cached_data = result
                self._save_cache(result)

                # Reset retry timer if successful
                self._retry_timer_id = None

                # Notify on GTK main thread
                GLib.idle_add(self._notify_listeners, result)
            except Exception as e:
                print(f"[WeatherEngine] Fetch error: {e}")
                # If we have no cached data, notify UI of retry
                if not self.cached_data:
                    error_payload = {
                        'status': 'error',
                        'city': city,
                        'temperature': '--°',
                        'high': '--°',
                        'low': '--°',
                        'condition': 'Retrying...',
                        'icon_path': self.get_icon_path('partly-cloudy-day'),
                    }
                    GLib.idle_add(self._notify_listeners, error_payload)

                # Schedule fast automatic retry (10s on boot/network failure)
                GLib.idle_add(self._schedule_retry, city, use_fahrenheit)
            finally:
                self._fetching = False
                if on_complete:
                    GLib.idle_add(on_complete)

        t = threading.Thread(target=_thread_target, daemon=True)
        t.start()

    def _schedule_retry(self, city, use_fahrenheit):
        if not self._retry_timer_id:
            # Fast retry after 10s if network was connecting during boot
            self._retry_timer_id = GLib.timeout_add_seconds(10, self._retry_fetch, city, use_fahrenheit)
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

