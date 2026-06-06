from dataclasses import dataclass
from os import getenv

from dotenv import load_dotenv

load_dotenv()  # Reads the .env file


@dataclass(frozen=True)
class Settings:
    database_url: str
    fred_api_key: str


def get_settings() -> Settings:
    database_url = getenv("DATABASE_URL")
    fred_api_key = getenv("FRED_API_KEY")

    if not database_url:
        raise RuntimeError("DATABASE_URL is missing. Add it to your .env file.")

    return Settings(database_url=database_url, fred_api_key=fred_api_key)
