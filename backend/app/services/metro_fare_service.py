"""
Metro Fare Service
Implements realistic BMRCL Namma Metro fare calculation based on station count.

Fare Rules (BMRCL approximate slab system):
- 0-2 stations:  Rs.10
- 3-5 stations:  Rs.20
- 6-10 stations: Rs.30
- 11-15 stations: Rs.40
- 16-20 stations: Rs.50
- 20+ stations:  Rs.60
"""

from typing import Dict


def calculate_metro_fare(num_stations: int) -> float:
    """
    Calculate metro fare based on number of stations traveled.

    Args:
        num_stations: Number of stations traveled (positive integer)

    Returns:
        Fare in INR
    """
    if num_stations <= 0:
        return 0.0
    elif num_stations <= 2:
        return 10.0
    elif num_stations <= 5:
        return 20.0
    elif num_stations <= 10:
        return 30.0
    elif num_stations <= 15:
        return 40.0
    elif num_stations <= 20:
        return 50.0
    else:
        return 60.0


def get_metro_fare_breakdown(source_seq: int, dest_seq: int) -> Dict:
    """
    Get detailed fare breakdown for a metro journey.

    Args:
        source_seq: Source station sequence number
        dest_seq: Destination station sequence number

    Returns:
        Dict with stations count and fare
    """
    station_diff = abs(dest_seq - source_seq)
    fare = calculate_metro_fare(station_diff)

    return {
        "stations": station_diff,
        "fare": fare,
    }
