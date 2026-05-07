"""
Fare Aggregator Service
Computes segment-wise and total fare for multi-modal journeys.

Aggregates:
- Metro segment fares (using BMRCL slab rules)
- Bus segment fares (using BMTC distance slab rules)
- Walking fares (Rs.0)
"""

from typing import List, Dict
from app.services.metro_fare_service import calculate_metro_fare
from app.services.bus_fare_service import calculate_bus_fare


def calculate_segment_fares(route_steps: List[dict], station_sequences: dict) -> Dict:
    """
    Calculate per-segment fares and total fare for a complete route.

    Args:
        route_steps: List of merged route steps with mode, from_station, to_station, distance
        station_sequences: Dict mapping station_id -> sequence_number (for metro)

    Returns:
        Dict with:
            - total_fare: Total journey fare
            - fare_breakdown: List of per-segment breakdowns
            - mode_totals: Aggregated fares by mode
    """
    fare_breakdown = []
    metro_total = 0.0
    bus_total = 0.0
    walk_total = 0.0

    for step in route_steps:
        mode = step.get("mode", "")
        from_id = step.get("from_station", "")
        to_id = step.get("to_station", "")
        from_name = step.get("from_name", from_id)
        to_name = step.get("to_name", to_id)
        distance = step.get("distance", 0.0)

        if mode == "metro":
            # Count stations using sequence numbers
            from_seq = station_sequences.get(from_id, 0)
            to_seq = station_sequences.get(to_id, 0)
            station_count = abs(to_seq - from_seq)

            # Fallback: if sequences not available, estimate from distance/time
            if station_count == 0:
                station_count = max(1, int(step.get("time", 0) / 2.5))

            fare = calculate_metro_fare(station_count)
            metro_total += fare

            fare_breakdown.append({
                "mode": "metro",
                "from_name": from_name,
                "to_name": to_name,
                "fare": fare,
                "stations": station_count,
            })

        elif mode == "bus":
            fare = calculate_bus_fare(distance)
            bus_total += fare

            fare_breakdown.append({
                "mode": "bus",
                "from_name": from_name,
                "to_name": to_name,
                "fare": fare,
                "distance_km": round(distance, 2),
            })

        elif mode in ("walking", "transfer"):
            fare = 0.0
            walk_total += fare

            fare_breakdown.append({
                "mode": mode,
                "from_name": from_name,
                "to_name": to_name,
                "fare": 0.0,
                "distance_km": round(distance, 2),
            })

    total_fare = metro_total + bus_total + walk_total

    return {
        "total_fare": round(total_fare, 1),
        "fare_breakdown": fare_breakdown,
        "mode_totals": {
            "metro": {"fare": metro_total},
            "bus": {"fare": bus_total},
            "walking": {"fare": walk_total},
        },
    }
