from dotenv import load_dotenv
import os
from typing import Final

load_dotenv()

BOT_USERNAME: Final = '@galaxy_trail_bot'
TOKEN: str = os.getenv('TOKEN')
NASA_KEY: str = os.getenv('NASA_API_KEY')
OPENWEATHER_KEY: str = os.getenv('OPENWEATHER_KEY')
NEWS_API_KEY: str = os.getenv('NEWS_API_KEY')

if not TOKEN:
    raise RuntimeError("TOKEN is not set. Please add TOKEN to your .env file or environment variables.")
