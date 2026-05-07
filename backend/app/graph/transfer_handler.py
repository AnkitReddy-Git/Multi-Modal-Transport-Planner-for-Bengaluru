"""
Transfer Handler Module
Manages transfer penalties when switching between transport modes.
"""

from app.config import settings


# Transfer penalty matrix (in minutes)
# Rows: from_mode, Columns: to_mode
TRANSFER_PENALTIES = {
    ("bus", "metro"): settings.TRANSFER_PENALTY_MIN,
    ("metro", "bus"): settings.TRANSFER_PENALTY_MIN,
    ("bus", "walking"): 2.0,
    ("walking", "bus"): 2.0,
    ("metro", "walking"): 2.0,
    ("walking", "metro"): 2.0,
    ("bus", "bus"): 3.0,  # Changing bus lines
}


def get_transfer_penalty(from_mode: str, to_mode: str) -> float:
    """
    Get the transfer penalty in minutes for switching between modes.

    Args:
        from_mode: Source transport mode
        to_mode: Destination transport mode

    Returns:
        Transfer penalty in minutes
    """
    if from_mode == to_mode and from_mode != "bus":
        return 0.0

    return TRANSFER_PENALTIES.get((from_mode, to_mode), settings.TRANSFER_PENALTY_MIN)


def is_transfer(from_mode: str, to_mode: str) -> bool:
    """Check if switching between two modes constitutes a transfer."""
    if from_mode == to_mode:
        return False
    if from_mode == "walking" or to_mode == "walking":
        return False  # Walking is not counted as a transfer in the transfer count
    return True


def count_transfers(route_modes: list) -> int:
    """
    Count the number of transfers in a route.

    Args:
        route_modes: List of transport modes for each segment

    Returns:
        Number of transfers
    """
    transfers = 0
    prev_mode = None

    for mode in route_modes:
        if mode == "walking" or mode == "transfer":
            continue
        if prev_mode is not None and prev_mode != mode:
            transfers += 1
        prev_mode = mode

    return transfers
