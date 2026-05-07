"""
Dijkstra's Shortest Path Algorithm Module
Implements weighted multi-modal routing using NetworkX.
Supports multiple optimization preferences with dynamic weight profiles.
"""

import networkx as nx
import uuid
from typing import List, Optional

from app.models.models import RouteStep, RouteResponse, OptimizationPreference, FareBreakdownItem
from app.graph.transfer_handler import count_transfers
from app.services.fare_aggregator import calculate_segment_fares
from app.services.osrm_service import get_bus_route_geometry, get_walking_route_geometry


# Weight profiles for each optimization preference
WEIGHT_PROFILES = {
    OptimizationPreference.FASTEST: {
        "time": 1.0,
        "fare": 0.0,
        "transfer": 0.3,
        "walking": 0.1,
    },
    OptimizationPreference.CHEAPEST: {
        "time": 0.2,
        "fare": 1.0,
        "transfer": 0.1,
        "walking": 0.0,
    },
    OptimizationPreference.LEAST_TRANSFERS: {
        "time": 0.3,
        "fare": 0.0,
        "transfer": 1.0,
        "walking": 0.1,
    },
    OptimizationPreference.LEAST_WALKING: {
        "time": 0.2,
        "fare": 0.0,
        "transfer": 0.1,
        "walking": 1.0,
    },
}


def compute_edge_weight(edge_data: dict, weights: dict) -> float:
    """
    Compute the weighted score for a single edge.

    score = (time_weight * time) + (fare_weight * fare) +
            (transfer_weight * transfer_penalty) + (walking_weight * walking_distance)
    """
    time_val = edge_data.get("time", 0)
    fare_val = edge_data.get("fare", 0)
    distance_val = edge_data.get("distance", 0)
    mode = edge_data.get("mode", "")

    # Transfer penalty component
    transfer_penalty = 1.0 if mode == "transfer" else 0.0

    # Walking distance component (only for walking/transfer edges)
    walking_component = distance_val if mode in ("walking", "transfer") else 0.0

    score = (
        weights["time"] * time_val
        + weights["fare"] * fare_val
        + weights["transfer"] * transfer_penalty * 10  # Scale transfer penalty
        + weights["walking"] * walking_component * 20   # Scale walking distance
    )

    return max(score, 0.01)  # Ensure positive weight


def find_shortest_path(
    graph: nx.DiGraph,
    source: str,
    destination: str,
    preference: OptimizationPreference,
    stations_info: dict,
    station_sequences: dict = None,
) -> Optional[RouteResponse]:
    """
    Find the shortest path between source and destination using Dijkstra's algorithm.

    Args:
        graph: The transport graph
        source: Source station/stop ID
        destination: Destination station/stop ID
        preference: Optimization preference
        stations_info: Dict of station_id -> station info
        station_sequences: Dict of station_id -> sequence_number for metro fare calc

    Returns:
        RouteResponse with full journey details, or None if no path found
    """
    weights = WEIGHT_PROFILES[preference]

    # Custom weight function for Dijkstra
    def weight_fn(u, v, data):
        return compute_edge_weight(data, weights)

    try:
        # Run Dijkstra's algorithm
        path = nx.dijkstra_path(graph, source, destination, weight=weight_fn)

        if len(path) < 2:
            return None

        # Build route steps
        steps: List[RouteStep] = []
        total_time = 0.0
        total_fare = 0.0
        total_distance = 0.0
        walking_distance = 0.0
        route_modes = []

        for i in range(len(path) - 1):
            from_id = path[i]
            to_id = path[i + 1]
            edge_data = graph.edges[from_id, to_id]

            from_info = stations_info.get(from_id, {})
            to_info = stations_info.get(to_id, {})

            mode = edge_data.get("mode", "unknown")
            route_modes.append(mode)

            step_time = edge_data.get("time", 0)
            step_fare = edge_data.get("fare", 0)
            step_distance = edge_data.get("distance", 0)

            total_time += step_time
            total_fare += step_fare
            total_distance += step_distance

            if mode in ("walking", "transfer"):
                walking_distance += step_distance

            fallback_geometry = edge_data.get("geometry", [])
            if not fallback_geometry:
                fallback_geometry = _fallback_step_geometry(from_info, to_info)

            # Resolve display geometry before merging so each rendered step has
            # road-following, pedestrian, or metro-track geometry.
            step_geometry = _resolve_edge_geometry(
                mode, from_info, to_info, fallback_geometry
            )
            edge_data["geometry"] = step_geometry

            steps.append(RouteStep(
                from_station=from_id,
                from_name=from_info.get("name", from_id),
                to_station=to_id,
                to_name=to_info.get("name", to_id),
                mode=mode,
                line=edge_data.get("line"),
                time=round(step_time, 1),
                fare=round(step_fare, 1),
                distance=round(step_distance, 3),
                geometry=step_geometry,
            ))

        # Merge consecutive same-mode steps for cleaner display
        merged_steps = _merge_consecutive_steps(steps)
        route_geometry = _concatenate_step_geometries(merged_steps)

        # Calculate realistic per-segment fares
        fare_result = calculate_segment_fares(
            [_route_step_to_dict(step) for step in merged_steps],
            station_sequences or {}
        )

        # Build fare_breakdown items
        fare_breakdown = [
            FareBreakdownItem(
                mode=item["mode"],
                from_name=item["from_name"],
                to_name=item["to_name"],
                fare=item["fare"],
                stations=item.get("stations"),
                distance_km=item.get("distance_km"),
            )
            for item in fare_result["fare_breakdown"]
        ]

        transfers = count_transfers(route_modes)

        return RouteResponse(
            route=merged_steps,
            total_time=round(total_time, 1),
            total_fare=fare_result["total_fare"],
            total_distance=round(total_distance, 2),
            transfers=transfers,
            walking_distance=round(walking_distance, 3),
            route_id=str(uuid.uuid4())[:8],
            preference=preference.value,
            geometry=route_geometry,
            fare_breakdown=fare_breakdown,
        )

    except nx.NetworkXNoPath:
        return None
    except nx.NodeNotFound:
        return None


def _merge_consecutive_steps(steps: List[RouteStep]) -> List[RouteStep]:
    """
    Merge consecutive steps of the same mode and line into single steps.
    This creates a cleaner journey breakdown (e.g., one metro segment instead of many).
    """
    if not steps:
        return steps

    merged = []
    current = steps[0]

    for next_step in steps[1:]:
        # Same mode and same line -> merge
        if (
            current.mode == next_step.mode
            and current.line == next_step.line
            and current.mode != "walking"
            and current.mode != "transfer"
        ):
            # Extend current step
            current = RouteStep(
                from_station=current.from_station,
                from_name=current.from_name,
                to_station=next_step.to_station,
                to_name=next_step.to_name,
                mode=current.mode,
                line=current.line,
                time=round(current.time + next_step.time, 1),
                fare=round(current.fare + next_step.fare, 1),
                distance=round(current.distance + next_step.distance, 3),
                geometry=_join_geometries(current.geometry, next_step.geometry),
            )
        else:
            merged.append(current)
            current = next_step

    merged.append(current)
    return merged


def _fallback_step_geometry(from_info: dict, to_info: dict) -> List[List[float]]:
    """Build a guaranteed two-point geometry from node coordinates."""
    return [
        [float(from_info.get("lat", 0)), float(from_info.get("lon", 0))],
        [float(to_info.get("lat", 0)), float(to_info.get("lon", 0))],
    ]


def _route_step_to_dict(step: RouteStep) -> dict:
    """Support both Pydantic v1 and v2 when serializing route steps."""
    if hasattr(step, "model_dump"):
        return step.model_dump()
    return step.dict()


def _resolve_edge_geometry(
    mode: str,
    from_info: dict,
    to_info: dict,
    fallback_geometry: List[List[float]],
) -> List[List[float]]:
    """
    Return the geometry the frontend should render for one graph edge.

    Metro edges keep predefined track geometry. Bus, walking, and transfer
    edges are lazily upgraded through OSRM, with fallback geometry preserved
    if the public router is unavailable.
    """
    fallback = fallback_geometry or _fallback_step_geometry(from_info, to_info)

    if mode not in ("bus", "walking", "transfer"):
        return fallback

    try:
        lat1 = float(from_info["lat"])
        lon1 = float(from_info["lon"])
        lat2 = float(to_info["lat"])
        lon2 = float(to_info["lon"])
    except (KeyError, TypeError, ValueError):
        return fallback

    try:
        if mode == "bus":
            geometry = get_bus_route_geometry(lat1, lon1, lat2, lon2)
        else:
            geometry = get_walking_route_geometry(lat1, lon1, lat2, lon2)
    except Exception:
        return fallback

    if not geometry or len(geometry) < 2:
        return fallback

    # Keep step endpoints anchored on the stop/station coordinates while the
    # interior points follow OSRM's routed geometry.
    geometry = [list(point) for point in geometry]
    geometry[0] = [lat1, lon1]
    geometry[-1] = [lat2, lon2]
    return geometry


def _join_geometries(
    first: Optional[List[List[float]]],
    second: Optional[List[List[float]]],
) -> List[List[float]]:
    """Concatenate two Leaflet polylines without duplicating shared endpoints."""
    result = list(first or [])
    segment = list(second or [])

    if not segment:
        return result
    if not result:
        return segment
    if result[-1] == segment[0]:
        result.extend(segment[1:])
    else:
        result.extend(segment)
    return result


def _concatenate_step_geometries(steps: List[RouteStep]) -> List[List[float]]:
    """Build the full route geometry from already-enhanced route steps."""
    geometry: List[List[float]] = []
    for step in steps:
        geometry = _join_geometries(geometry, step.geometry)
    return geometry
