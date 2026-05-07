"""
Bus Fare Service
Implements realistic BMTC-style distance-based slab fare calculation.

Fare Rules (BMTC ordinary bus approximate slabs):
- 0-2 km:   Rs.5
- 2-5 km:   Rs.10
- 5-10 km:  Rs.15
- 10-15 km: Rs.20
- 15-20 km: Rs.25
- 20+ km:   Rs.30
"""

from typing import Dict


def calculate_bus_fare(distance_km: float) -> float:
    """
    Calculate BMTC bus fare based on traveled distance.

    Args:
        distance_km: Distance traveled in kilometers

    Returns:
        Fare in INR
    """
    if distance_km <= 0:
        return 0.0
    elif distance_km <= 2:
        return 5.0
    elif distance_km <= 5:
        return 10.0
    elif distance_km <= 10:
        return 15.0
    elif distance_km <= 15:
        return 20.0
    elif distance_km <= 20:
        return 25.0
    else:
        return 30.0


def get_bus_fare_breakdown(distance_km: float) -> Dict:
    """
    Get detailed fare breakdown for a bus journey.

    Args:
        distance_km: Distance traveled in kilometers

    Returns:
        Dict with distance and fare
    """
    fare = calculate_bus_fare(distance_km)

    return {
        "distance_km": round(distance_km, 2),
        "fare": fare,
    }
