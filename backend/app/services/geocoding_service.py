"""
Geocoding Service
Uses Nominatim API for converting place names to coordinates and vice versa.
"""

import requests
from typing import Optional, Dict, List


NOMINATIM_URL = "https://nominatim.openstreetmap.org"
HEADERS = {"User-Agent": "PurpleLink-ITS/1.0 (academic-project)"}


def geocode(place_name: str, city: str = "Bengaluru") -> Optional[Dict]:
    """
    Convert a place name to coordinates using Nominatim.

    Args:
        place_name: Place name (e.g., "MG Road", "Majestic")
        city: City context

    Returns:
        Dict with 'lat', 'lon', 'display_name' or None
    """
    try:
        params = {
            "q": f"{place_name}, {city}, Karnataka, India",
            "format": "json",
            "limit": 1,
            "addressdetails": 1,
        }

        response = requests.get(
            f"{NOMINATIM_URL}/search",
            params=params,
            headers=HEADERS,
            timeout=10,
        )

        if response.status_code == 200:
            results = response.json()
            if results:
                result = results[0]
                return {
                    "lat": float(result["lat"]),
                    "lon": float(result["lon"]),
                    "display_name": result.get("display_name", place_name),
                }

    except Exception as e:
        print(f"[Geocoding] Error: {e}")

    return None


def reverse_geocode(lat: float, lon: float) -> Optional[str]:
    """
    Convert coordinates to a place name using Nominatim.

    Args:
        lat: Latitude
        lon: Longitude

    Returns:
        Place name string or None
    """
    try:
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
        }

        response = requests.get(
            f"{NOMINATIM_URL}/reverse",
            params=params,
            headers=HEADERS,
            timeout=10,
        )

        if response.status_code == 200:
            result = response.json()
            return result.get("display_name", "Unknown location")

    except Exception as e:
        print(f"[Geocoding] Reverse geocode error: {e}")

    return None


def search_stations(query: str, stations: List[dict]) -> List[dict]:
    """
    Search stations by name (fuzzy matching).
    Uses local station data rather than Nominatim.

    Args:
        query: Search query
        stations: List of station dicts

    Returns:
        Matching stations sorted by relevance
    """
    query_lower = query.lower().strip()
    results = []

    for station in stations:
        name = station.get("name", "").lower()
        station_id = station.get("id", "").lower()

        if query_lower in name or query_lower in station_id:
            # Calculate a simple relevance score
            if name.startswith(query_lower):
                score = 3
            elif query_lower in name:
                score = 2
            else:
                score = 1

            results.append({**station, "_score": score})

    results.sort(key=lambda x: (-x["_score"], x.get("name", "")))

    # Remove score from results
    for r in results:
        r.pop("_score", None)

    return results[:20]
