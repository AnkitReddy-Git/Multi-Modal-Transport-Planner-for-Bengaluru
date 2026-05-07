"""
Fare Calculation Service (Legacy Compatibility)
Delegates to new slab-based fare services.
"""

from typing import List, Dict
from app.models.models import RouteStep
from app.services.metro_fare_service import calculate_metro_fare as _metro_fare
from app.services.bus_fare_service import calculate_bus_fare as _bus_fare


def calculate_metro_fare(num_stations: int) -> float:
    """Delegate to metro_fare_service."""
    return _metro_fare(num_stations)


def calculate_bus_fare(distance_km: float) -> float:
    """Delegate to bus_fare_service."""
    return _bus_fare(distance_km)


def calculate_route_fare(steps: List[RouteStep]) -> Dict:
    """
    Calculate detailed fare breakdown for a complete route.
    Backward-compatible wrapper.
    """
    metro_fare = 0.0
    bus_fare = 0.0
    metro_stations = 0
    bus_distance = 0.0

    for step in steps:
        if step.mode == "metro":
            estimated_stations = max(1, int(step.time / 2.5))
            metro_stations += estimated_stations
        elif step.mode == "bus":
            bus_distance += step.distance

    if metro_stations > 0:
        metro_fare = _metro_fare(metro_stations)

    if bus_distance > 0:
        bus_fare = _bus_fare(bus_distance)

    return {
        "metro_fare": metro_fare,
        "bus_fare": bus_fare,
        "walking_fare": 0.0,
        "total_fare": round(metro_fare + bus_fare, 1),
        "breakdown": {
            "metro": {"stations": metro_stations, "fare": metro_fare},
            "bus": {"distance_km": round(bus_distance, 2), "fare": bus_fare},
        },
    }
