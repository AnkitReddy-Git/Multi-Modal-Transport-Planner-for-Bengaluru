"""
OSRM Service
Fetches route geometry from Open Source Routing Machine (OSRM) public API.

Profiles:
- driving: for bus routes
- foot: for walking/pedestrian routes

Caches results to reduce repeated API calls.
Falls back to straight-line geometry on failure.
"""

import json
import urllib.request
import urllib.error
from typing import List, Optional

OSRM_BASE_URL = "https://router.project-osrm.org/route/v1"
TIMEOUT_SECONDS = 10


def _straight_line_geometry(
    lat1: float, lon1: float, lat2: float, lon2: float, num_points: int = 20
) -> List[List[float]]:
    """Generate interpolated straight-line coordinates as fallback."""
    coords = []
    for i in range(num_points + 1):
        t = i / num_points
        lat = lat1 + (lat2 - lat1) * t
        lon = lon1 + (lon2 - lon1) * t
        coords.append([lat, lon])
    return coords


def _fetch_osrm_geometry(
    profile: str,
    lon1: float, lat1: float,
    lon2: float, lat2: float,
) -> Optional[List[List[float]]]:
    """
    Call OSRM API and return geometry as [[lat, lon], ...].
    Returns None on failure.
    """
    url = (
        f"{OSRM_BASE_URL}/{profile}/"
        f"{lon1},{lat1};{lon2},{lat2}"
        f"?overview=full&geometries=geojson"
    )

    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if not data.get("routes"):
            return None

        route = data["routes"][0]
        geojson = route.get("geometry")

        if not geojson or geojson.get("type") != "LineString":
            return None

        # Convert [lon, lat] -> [lat, lon]
        coords = [[pt[1], pt[0]] for pt in geojson.get("coordinates", [])]
        if len(coords) < 2:
            return None
        return coords

    except Exception:
        return None


# In-memory cache: key="{profile}:{lat1}:{lon1}:{lat2}:{lon2}"
_cache: dict = {}


def get_route_geometry(
    profile: str,
    lat1: float, lon1: float,
    lat2: float, lon2: float,
    use_cache: bool = True,
) -> List[List[float]]:
    """
    Get route geometry from OSRM, with caching and fallback.

    Args:
        profile: 'driving' or 'foot'
        lat1, lon1: Start coordinates
        lat2, lon2: End coordinates
        use_cache: Whether to use/read from cache

    Returns:
        List of [lat, lon] coordinates (Leaflet-compatible).
        Falls back to straight-line interpolation on API failure.
    """
    # Round to 5 decimals for cache key (~1m precision)
    cache_key = (
        f"{profile}:"
        f"{round(lat1, 5)}:{round(lon1, 5)}:"
        f"{round(lat2, 5)}:{round(lon2, 5)}"
    )

    if use_cache and cache_key in _cache:
        return _cache[cache_key]

    coords = _fetch_osrm_geometry(profile, lon1, lat1, lon2, lat2)

    if coords is None:
        coords = _straight_line_geometry(lat1, lon1, lat2, lon2)

    if use_cache:
        _cache[cache_key] = coords

    return coords


def get_bus_route_geometry(
    lat1: float, lon1: float,
    lat2: float, lon2: float,
) -> List[List[float]]:
    """Get road-following geometry for bus routes (driving profile)."""
    return get_route_geometry("driving", lat1, lon1, lat2, lon2)


def get_walking_route_geometry(
    lat1: float, lon1: float,
    lat2: float, lon2: float,
) -> List[List[float]]:
    """Get pedestrian geometry for walking routes (foot profile)."""
    return get_route_geometry("foot", lat1, lon1, lat2, lon2)


def clear_cache() -> None:
    """Clear the OSRM geometry cache."""
    _cache.clear()
