from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from macrodata_norway.config import get_settings


def get_engine() -> Engine:  # Represents the connection setup to the database
    settings = get_settings()

    return create_engine(
        settings.database_url,
        pool_pre_ping=True,  # Check if the conection is alive before using it
    )
