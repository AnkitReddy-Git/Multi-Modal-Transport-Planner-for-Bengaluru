"""
Stations API Routes
Endpoints for station/stop data retrieval and search.
"""

from fastapi import APIRouter, Query
from typing import List, Optional

from app.models.models import Station
from app.services.geocoding_service import search_stations

router = APIRouter(prefix="/api", tags=["stations"])

# Reference to graph (set during app startup)
_transport_graph = None


def set_transport_graph(graph):
    global _transport_graph
    _transport_graph = graph


@router.get("/stations")
async def get_all_stations(
    type: Optional[str] = Query(None, description="Filter by type: metro, bus_stop, metro_interchange"),
    mode: Optional[str] = Query(None, description="Filter by mode: metro, bus"),
):
    """
    Get all stations and stops.
    Optional filters by type or mode.
    """
    stations = _transport_graph.get_all_stations()

    if type:
        stations = [s for s in stations if s.get("type") == type]

    if mode:
        stations = [s for s in stations if s.get("mode") == mode]

    return {"stations": stations, "count": len(stations)}


@router.get("/stations/{station_id}")
async def get_station(station_id: str):
    """Get a single station by ID."""
    station = _transport_graph.get_station_info(station_id)
    if station:
        return {"station": station}
    return {"error": "Station not found", "station_id": station_id}


@router.get("/stations/search/{query}")
async def search_stations_endpoint(query: str):
    """Search stations by name."""
    stations = _transport_graph.get_all_stations()
    results = search_stations(query, stations)
    return {"results": results, "count": len(results)}


@router.get("/nearby-stops")
async def get_nearby_stops(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    radius: float = Query(500, description="Search radius in meters"),
):
    """Get nearby stops within a radius of given coordinates."""
    stops = _transport_graph.get_nearby_stops(lat, lon, radius)
    return {"stops": stops, "count": len(stops)}


@router.get("/graph-stats")
async def get_graph_stats():
    """Get transport graph statistics."""
    stats = _transport_graph.get_graph_stats()
    return {"stats": stats}
