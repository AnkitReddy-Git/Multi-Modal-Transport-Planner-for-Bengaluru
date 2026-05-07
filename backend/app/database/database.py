"""
Database Module
Handles optional Supabase PostgreSQL integration.
Falls back to local CSV data when Supabase is unavailable.
"""

from typing import Optional
from app.config import settings


_supabase_client = None


def get_supabase_client():
    """Get or create Supabase client (lazy initialization)."""
    global _supabase_client

    if not settings.supabase_enabled:
        return None

    if _supabase_client is None:
        try:
            from supabase import create_client
            _supabase_client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY,
            )
            print("[Database] Supabase client initialized")
        except Exception as e:
            print(f"[Database] Supabase initialization failed: {e}")
            print("[Database] Falling back to offline mode")
            return None

    return _supabase_client


def is_database_available() -> bool:
    """Check if database connection is available."""
    client = get_supabase_client()
    if client is None:
        return False

    try:
        # Simple health check
        client.table("stations").select("id").limit(1).execute()
        return True
    except Exception:
        return False


def sync_stations_to_db(stations: list):
    """Sync station data to Supabase (optional)."""
    client = get_supabase_client()
    if client is None:
        return

    try:
        for station in stations:
            client.table("stations").upsert({
                "id": station["id"],
                "name": station["name"],
                "lat": station["lat"],
                "lon": station["lon"],
                "type": station["type"],
                "line": station.get("line"),
            }).execute()
        print(f"[Database] Synced {len(stations)} stations to Supabase")
    except Exception as e:
        print(f"[Database] Station sync failed: {e}")
