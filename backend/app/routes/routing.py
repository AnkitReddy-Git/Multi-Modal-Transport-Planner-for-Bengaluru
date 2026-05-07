"""
Routing API Routes
Endpoints for multi-modal route computation and comparison.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional

from app.models.models import OptimizationPreference, RouteResponse
from app.algorithms.dijkstra import find_shortest_path
from app.algorithms.route_optimizer import compute_route_alternatives

router = APIRouter(prefix="/api", tags=["routing"])

# References set during app startup
_transport_graph = None
_disruption_service = None


def set_transport_graph(graph):
    global _transport_graph
    _transport_graph = graph


def set_disruption_service(service):
    global _disruption_service
    _disruption_service = service


def _resolve_station_id(query: str) -> str:
    """
    Resolve a station query to a station ID.
    Accepts either a station ID directly or a station name.
    """
    # Check if it's already a valid ID
    if _transport_graph.get_station_info(query):
        return query

    # Try case-insensitive name search
    query_lower = query.lower().strip()
    for station in _transport_graph.get_all_stations():
        if station["name"].lower() == query_lower:
            return station["id"]
        if station["id"].lower() == query_lower:
            return station["id"]

    # Try partial match
    for station in _transport_graph.get_all_stations():
        if query_lower in station["name"].lower():
            return station["id"]

    return query  # Return as-is, will fail in routing if invalid


@router.get("/route")
async def get_route(
    source: str = Query(..., description="Source station ID or name"),
    destination: str = Query(..., description="Destination station ID or name"),
    preference: str = Query("fastest", description="Optimization: fastest, cheapest, least_transfers, least_walking"),
):
    """
    Compute an optimized multi-modal route.

    Parameters:
    - source: Station ID (e.g., M15) or name (e.g., Majestic)
    - destination: Station ID or name
    - preference: Optimization preference

    Returns route with step-by-step journey, time, fare, transfers, walking distance,
    and geometry for map rendering.
    """
    # Resolve station IDs
    source_id = _resolve_station_id(source)
    dest_id = _resolve_station_id(destination)

    # Validate
    if not _transport_graph.get_station_info(source_id):
        raise HTTPException(status_code=404, detail=f"Source station not found: {source}")
    if not _transport_graph.get_station_info(dest_id):
        raise HTTPException(status_code=404, detail=f"Destination station not found: {destination}")
    if source_id == dest_id:
        raise HTTPException(status_code=400, detail="Source and destination are the same")

    # Parse preference
    try:
        pref = OptimizationPreference(preference.lower())
    except ValueError:
        pref = OptimizationPreference.FASTEST

    # Get graph (with disruptions applied if any)
    graph = _disruption_service.get_disrupted_graph(_transport_graph.G)

    # Find route
    route = find_shortest_path(
        graph, source_id, dest_id, pref,
        _transport_graph.stations,
        _transport_graph.station_sequences
    )

    if not route:
        raise HTTPException(
            status_code=404,
            detail=f"No route found from {source} to {destination}. "
                   "This may be due to active disruptions blocking all paths."
        )

    # Fare breakdown is now computed inside find_shortest_path
    return {
        "route": route.dict(),
        "fare_breakdown": {
            "total_fare": route.total_fare,
            "breakdown": [item.dict() for item in route.fare_breakdown] if route.fare_breakdown else [],
            "mode_totals": {
                "metro": {"fare": sum(item.fare for item in route.fare_breakdown if item.mode == "metro")},
                "bus": {"fare": sum(item.fare for item in route.fare_breakdown if item.mode == "bus")},
                "walking": {"fare": 0.0},
            },
        },
    }


@router.get("/route/compare")
async def compare_routes(
    source: str = Query(..., description="Source station ID or name"),
    destination: str = Query(..., description="Destination station ID or name"),
):
    """
    Compute up to 3 alternative routes for comparison.
    Uses all 4 optimization preferences and returns distinct routes.
    """
    source_id = _resolve_station_id(source)
    dest_id = _resolve_station_id(destination)

    if not _transport_graph.get_station_info(source_id):
        raise HTTPException(status_code=404, detail=f"Source station not found: {source}")
    if not _transport_graph.get_station_info(dest_id):
        raise HTTPException(status_code=404, detail=f"Destination station not found: {destination}")

    # Get graph with disruptions
    graph = _disruption_service.get_disrupted_graph(_transport_graph.G)

    routes = compute_route_alternatives(
        graph, source_id, dest_id,
        _transport_graph.stations,
        _transport_graph.station_sequences
    )

    if not routes:
        raise HTTPException(
            status_code=404,
            detail=f"No routes found from {source} to {destination}"
        )

    # Fare breakdown is now computed inside each route
    result_routes = []
    for route in routes:
        fare_breakdown_data = {
            "total_fare": route.total_fare,
            "breakdown": [item.dict() for item in route.fare_breakdown] if route.fare_breakdown else [],
            "mode_totals": {
                "metro": {"fare": sum(item.fare for item in route.fare_breakdown if item.mode == "metro")},
                "bus": {"fare": sum(item.fare for item in route.fare_breakdown if item.mode == "bus")},
                "walking": {"fare": 0.0},
            },
        }
        result_routes.append({
            "route": route.dict(),
            "fare_breakdown": fare_breakdown_data,
        })

    return {"routes": result_routes, "count": len(result_routes)}
