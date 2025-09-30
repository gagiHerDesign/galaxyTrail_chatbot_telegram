import requests
from typing import Optional, Tuple
from .config import NASA_KEY, OPENWEATHER_KEY, NEWS_API_KEY


def fetch_weather(city: str) -> Optional[dict]:
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_KEY}&units=metric"
    try:
        resp = requests.get(weather_url, timeout=8)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        return None
    return None


def fetch_nasa_apod() -> Tuple[Optional[str], Optional[str]]:
    nasa_url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_KEY}"
    try:
        resp = requests.get(nasa_url, timeout=6)
        if resp.status_code == 200:
            j = resp.json()
            return j.get('title'), j.get('url')
    except Exception:
        return None, None
    return None, None


def fetch_news_events(page_size: int = 3):
    """Fetch recent astronomy-related news using NewsAPI.

    Returns a tuple: (status_code, parsed_json_or_error_text)
    """
    url = (
        "https://newsapi.org/v2/everything"
        "?q=astronomy"
        "&language=en"
        "&sortBy=publishedAt"
        f"&pageSize={page_size}"
        f"&apiKey={NEWS_API_KEY}"
    )
    try:
        resp = requests.get(url, timeout=8)
        if resp.status_code == 200:
            return resp.status_code, resp.json()
        else:
            return resp.status_code, resp.text
    except Exception as e:
        return None, str(e)
