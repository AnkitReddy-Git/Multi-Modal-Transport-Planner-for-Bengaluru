"""
PurpleLink Configuration Module
Loads environment variables and provides application settings.
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from backend directory
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    """Application settings loaded from environment variables."""

    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # Dataset paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATASETS_DIR: Path = BASE_DIR / "datasets"
    METRO_DIR: Path = DATASETS_DIR / "metro"
    BUS_DIR: Path = DATASETS_DIR / "bus"

    # Graph parameters
    WALKING_RADIUS_M: float = 500.0  # meters
    WALKING_SPEED_KMH: float = 5.0   # km/h
    TRANSFER_PENALTY_MIN: float = 5.0  # minutes

    # Fare parameters
    METRO_BASE_FARE: float = 10.0
    METRO_PER_STATION_FARE: float = 5.0
    METRO_MAX_FARE: float = 60.0
    BUS_BASE_FARE: float = 5.0
    BUS_PER_KM_FARE: float = 1.0
    BUS_MAX_FARE: float = 30.0

    @property
    def supabase_enabled(self) -> bool:
        return bool(self.SUPABASE_URL and self.SUPABASE_KEY)


settings = Settings()
