"""
Route Optimizer Module
Computes multiple route alternatives for comparison.
Returns top distinct routes across different optimization preferences.
"""

from typing import List, Optional
import networkx as nx

from app.models.models import RouteResponse, OptimizationPreference
from app.algorithms.dijkstra import find_shortest_path


def compute_route_alternatives(
    graph: nx.DiGraph,
    source: str,
    destination: str,
    stations_info: dict,
    station_sequences: dict = None,
    max_routes: int = 3,
) -> List[RouteResponse]:
    """
    Compute up to max_routes distinct route alternatives.
    Runs Dijkstra with all 4 optimization preferences and returns
    the top distinct routes.

    Args:
        graph: Transport graph
        source: Source station ID
        destination: Destination station ID
        stations_info: Station info lookup
        max_routes: Maximum number of routes to return

    Returns:
        List of distinct RouteResponse objects
    """
    all_routes = []
    seen_paths = set()

    preferences = [
        OptimizationPreference.FASTEST,
        OptimizationPreference.CHEAPEST,
        OptimizationPreference.LEAST_TRANSFERS,
        OptimizationPreference.LEAST_WALKING,
    ]

    for pref in preferences:
        route = find_shortest_path(
            graph, source, destination, pref, stations_info, station_sequences
        )
        if route:
            # Create a path signature to check for duplicates
            path_sig = tuple(
                (s.from_station, s.to_station, s.mode) for s in route.route
            )

            if path_sig not in seen_paths:
                seen_paths.add(path_sig)
                all_routes.append(route)

    # If we have fewer routes than max, try k-shortest paths with default preference
    if len(all_routes) < max_routes:
        try:
            _add_k_shortest_alternatives(
                graph, source, destination, stations_info, station_sequences,
                all_routes, seen_paths, max_routes
            )
        except Exception:
            pass  # k-shortest may not always work

    # Sort by total_time (primary) and return top max_routes
    all_routes.sort(key=lambda r: r.total_time)

    # Mark the best route
    return all_routes[:max_routes]


def _add_k_shortest_alternatives(
    graph: nx.DiGraph,
    source: str,
    destination: str,
    stations_info: dict,
    station_sequences: dict,
    existing_routes: List[RouteResponse],
    seen_paths: set,
    max_routes: int,
):
    """Try to find additional routes using edge weight perturbation."""
    import copy
    import random

    # Slightly perturb edge weights to find alternative paths
    for attempt in range(3):
        perturbed = graph.copy()

        # Randomly increase weights on some edges
        for u, v, data in perturbed.edges(data=True):
            if random.random() < 0.3:
                data["time"] = data.get("time", 1) * (1.2 + random.random() * 0.5)

        route = find_shortest_path(
            perturbed, source, destination,
            OptimizationPreference.FASTEST, stations_info, station_sequences
        )

        if route and len(existing_routes) < max_routes:
            path_sig = tuple(
                (s.from_station, s.to_station, s.mode) for s in route.route
            )
            if path_sig not in seen_paths:
                seen_paths.add(path_sig)
                route.preference = f"alternative_{attempt + 1}"
                existing_routes.append(route)
