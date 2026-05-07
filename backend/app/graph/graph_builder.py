"""
Transport Graph Builder Module
Constructs a unified weighted directed graph from metro, bus, and walking data.
Part of the Processing Layer in the ITS 3-Layer Architecture.
"""

import networkx as nx
import pandas as pd
import math
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from app.config import settings


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two GPS coordinates in meters."""
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


class TransportGraph:
    """
    Unified multi-modal transport graph for Bengaluru.
    Integrates metro stations, bus stops, walking connections, and transfer edges
    into a single weighted directed NetworkX graph.
    """

    def __init__(self):
        self.G = nx.DiGraph()
        self.stations: Dict[str, dict] = {}  # id -> station info
        self.metro_stations: List[str] = []
        self.bus_stops: List[str] = []
        self.station_sequences: Dict[str, int] = {}  # station_id -> sequence_number (metro)
        self.walking_edge_count = 0
        self.transfer_edge_count = 0
        self._metro_geometry: List[List[float]] = []  # Full Purple Line path [lat, lon]
        self._station_geo_indices: Dict[str, int] = {}  # station_id -> index in _metro_geometry

    def _load_metro_geometry(self):
        """Load predefined Purple Line geometry and map stations to their closest points."""
        geo_path = settings.METRO_DIR / "purple_line_geometry.json"
        if not geo_path.exists():
            print("[GraphBuilder] Metro geometry file not found, using straight lines")
            return

        with open(geo_path, "r") as f:
            self._metro_geometry = json.load(f)

        # Map each metro station to the closest geometry point
        for station_id in self.metro_stations:
            station = self.stations.get(station_id)
            if not station:
                continue
            s_lat, s_lon = station["lat"], station["lon"]

            best_idx = 0
            best_dist = float("inf")
            for idx, (g_lat, g_lon) in enumerate(self._metro_geometry):
                dist = haversine_distance(s_lat, s_lon, g_lat, g_lon)
                if dist < best_dist:
                    best_dist = dist
                    best_idx = idx

            self._station_geo_indices[station_id] = best_idx

        print(f"[GraphBuilder] Loaded metro geometry with {len(self._metro_geometry)} points")

    def _get_metro_edge_geometry(self, from_id: str, to_id: str) -> List[List[float]]:
        """Extract geometry segment between two metro stations from the full path."""
        from_idx = self._station_geo_indices.get(from_id, 0)
        to_idx = self._station_geo_indices.get(to_id, 0)

        if from_idx == to_idx:
            # Fallback: just the two station coordinates
            from_station = self.stations.get(from_id)
            to_station = self.stations.get(to_id)
            if from_station and to_station:
                return [[from_station["lat"], from_station["lon"]], [to_station["lat"], to_station["lon"]]]
            return []

        if from_idx < to_idx:
            segment = self._metro_geometry[from_idx : to_idx + 1]
        else:
            segment = self._metro_geometry[to_idx : from_idx + 1][::-1]

        # Ensure endpoints match station coordinates exactly
        from_station = self.stations.get(from_id)
        to_station = self.stations.get(to_id)
        if from_station and to_station:
            segment[0] = [from_station["lat"], from_station["lon"]]
            segment[-1] = [to_station["lat"], to_station["lon"]]

        return segment

    def build(self) -> nx.DiGraph:
        """Build the complete transport graph from all data sources."""
        print("[GraphBuilder] Building transport graph...")
        self._load_metro_nodes()
        self._load_metro_geometry()
        self._load_metro_edges()
        self._load_bus_nodes()
        self._load_bus_edges()
        self._generate_walking_edges()
        self._generate_transfer_edges()
        print(f"[GraphBuilder] Graph built: {self.G.number_of_nodes()} nodes, {self.G.number_of_edges()} edges")
        print(f"[GraphBuilder] Metro stations: {len(self.metro_stations)}")
        print(f"[GraphBuilder] Bus stops: {len(self.bus_stops)}")
        print(f"[GraphBuilder] Walking edges: {self.walking_edge_count}")
        print(f"[GraphBuilder] Transfer edges: {self.transfer_edge_count}")
        return self.G

    def _load_metro_nodes(self):
        """Load Purple Line metro stations as graph nodes."""
        csv_path = settings.METRO_DIR / "purple_line.csv"
        df = pd.read_csv(csv_path)

        for _, row in df.iterrows():
            station_id = row["station_id"]
            seq_num = int(row.get("sequence_number", 0))
            self.G.add_node(
                station_id,
                name=row["station_name"],
                lat=row["latitude"],
                lon=row["longitude"],
                type=row["type"],
                line=row["line"],
                mode="metro",
                sequence_number=seq_num,
            )
            self.stations[station_id] = {
                "id": station_id,
                "name": row["station_name"],
                "lat": row["latitude"],
                "lon": row["longitude"],
                "type": row["type"],
                "line": row["line"],
                "mode": "metro",
                "sequence_number": seq_num,
            }
            if seq_num > 0:
                self.station_sequences[station_id] = seq_num
            self.metro_stations.append(station_id)

        print(f"[GraphBuilder] Loaded {len(self.metro_stations)} metro stations")

    def _load_metro_edges(self):
        """Load metro edges (bidirectional sequential connections) with geometry."""
        csv_path = settings.METRO_DIR / "metro_edges.csv"
        df = pd.read_csv(csv_path)

        for _, row in df.iterrows():
            from_id = row["from_station"]
            to_id = row["to_station"]

            # Get actual metro track geometry
            if self._metro_geometry:
                geometry = self._get_metro_edge_geometry(from_id, to_id)
            else:
                # Fallback: straight line
                from_station = self.stations.get(from_id)
                to_station = self.stations.get(to_id)
                geometry = []
                if from_station and to_station:
                    geometry = [[from_station["lat"], from_station["lon"]], [to_station["lat"], to_station["lon"]]]

            self.G.add_edge(
                from_id,
                to_id,
                time=row["time_minutes"],
                fare=row["fare_inr"],
                distance=row["distance_km"],
                mode="metro",
                line=row["line"],
                geometry=geometry,
            )

        print(f"[GraphBuilder] Loaded {len(df)} metro edges with geometry")

    def _load_bus_nodes(self):
        """Load BMTC bus stops as graph nodes."""
        txt_path = settings.BUS_DIR / "stops.txt"
        df = pd.read_csv(txt_path)

        for _, row in df.iterrows():
            stop_id = row["stop_id"]
            self.G.add_node(
                stop_id,
                name=row["stop_name"],
                lat=row["stop_lat"],
                lon=row["stop_lon"],
                type="bus_stop",
                line=None,
                mode="bus",
            )
            self.stations[stop_id] = {
                "id": stop_id,
                "name": row["stop_name"],
                "lat": row["stop_lat"],
                "lon": row["stop_lon"],
                "type": "bus_stop",
                "line": None,
                "mode": "bus",
            }
            self.bus_stops.append(stop_id)

        print(f"[GraphBuilder] Loaded {len(self.bus_stops)} bus stops")

    def _load_bus_edges(self):
        """Load bus edges from GTFS stop_times (bidirectional)."""
        stop_times_path = settings.BUS_DIR / "stop_times.txt"
        trips_path = settings.BUS_DIR / "trips.txt"
        routes_path = settings.BUS_DIR / "routes.txt"

        stop_times = pd.read_csv(stop_times_path)
        trips = pd.read_csv(trips_path)
        routes = pd.read_csv(routes_path)

        # Merge to get route info for each stop_time
        merged = stop_times.merge(trips, on="trip_id").merge(routes, on="route_id")

        edge_count = 0
        # Group by trip_id and create edges between consecutive stops
        for trip_id, group in merged.groupby("trip_id"):
            group = group.sort_values("stop_sequence")
            stops_list = group.to_dict("records")

            for i in range(len(stops_list) - 1):
                from_stop = stops_list[i]
                to_stop = stops_list[i + 1]

                # Calculate time from GTFS times
                from_time = self._parse_gtfs_time(from_stop["departure_time"])
                to_time = self._parse_gtfs_time(to_stop["arrival_time"])
                travel_time = max(1, (to_time - from_time))  # minutes

                # Calculate distance
                from_node = self.G.nodes.get(from_stop["stop_id"])
                to_node = self.G.nodes.get(to_stop["stop_id"])

                if from_node and to_node:
                    dist = haversine_distance(
                        from_node["lat"], from_node["lon"],
                        to_node["lat"], to_node["lon"]
                    ) / 1000  # km
                else:
                    dist = 1.0  # default

                # Calculate fare (distance-based)
                fare = min(
                    settings.BUS_MAX_FARE,
                    settings.BUS_BASE_FARE + settings.BUS_PER_KM_FARE * dist
                )

                route_name = from_stop.get("route_short_name", "")

                # Startup fallback only; route responses lazily upgrade bus
                # geometry through OSRM before the map renders it.
                geometry = []
                if from_node and to_node:
                    lat1, lon1 = from_node["lat"], from_node["lon"]
                    lat2, lon2 = to_node["lat"], to_node["lon"]
                    # Interpolate 5 points for smoother polyline
                    for t in range(6):
                        frac = t / 5.0
                        lat = lat1 + (lat2 - lat1) * frac
                        lon = lon1 + (lon2 - lon1) * frac
                        geometry.append([lat, lon])

                # Add edge (the trip direction already provides directionality,
                # and we have reverse trips in the data, so both directions are covered)
                if not self.G.has_edge(from_stop["stop_id"], to_stop["stop_id"]):
                    self.G.add_edge(
                        from_stop["stop_id"],
                        to_stop["stop_id"],
                        time=travel_time,
                        fare=round(fare, 1),
                        distance=round(dist, 2),
                        mode="bus",
                        line=route_name,
                        geometry=geometry,
                    )
                    edge_count += 1

        print(f"[GraphBuilder] Loaded {edge_count} bus edges with geometry")

    def _generate_walking_edges(self):
        """
        Generate walking edges between all nearby stops within WALKING_RADIUS_M.
        Connects metro stations to bus stops and bus stops to each other.
        """
        all_nodes = list(self.G.nodes(data=True))
        radius = settings.WALKING_RADIUS_M
        speed = settings.WALKING_SPEED_KMH

        for i, (node1_id, node1_data) in enumerate(all_nodes):
            for j, (node2_id, node2_data) in enumerate(all_nodes):
                if i >= j:
                    continue
                # Skip same-mode same-line connections (already have direct edges)
                if node1_data.get("mode") == node2_data.get("mode") == "metro":
                    continue

                dist_m = haversine_distance(
                    node1_data["lat"], node1_data["lon"],
                    node2_data["lat"], node2_data["lon"]
                )

                if dist_m <= radius:
                    dist_km = dist_m / 1000
                    walk_time = (dist_km / speed) * 60  # minutes

                    # Startup fallback only; route responses lazily upgrade
                    # walking geometry through OSRM before display.
                    straight = [[node1_data["lat"], node1_data["lon"]], [node2_data["lat"], node2_data["lon"]]]
                    geometry_1to2 = straight
                    geometry_2to1 = straight[::-1]

                    # Add bidirectional walking edges
                    if not self.G.has_edge(node1_id, node2_id):
                        self.G.add_edge(
                            node1_id, node2_id,
                            time=round(walk_time, 1),
                            fare=0,
                            distance=round(dist_km, 3),
                            mode="walking",
                            line=None,
                            geometry=geometry_1to2,
                        )
                        self.walking_edge_count += 1

                    if not self.G.has_edge(node2_id, node1_id):
                        self.G.add_edge(
                            node2_id, node1_id,
                            time=round(walk_time, 1),
                            fare=0,
                            distance=round(dist_km, 3),
                            mode="walking",
                            line=None,
                            geometry=geometry_2to1,
                        )
                        self.walking_edge_count += 1

        print(f"[GraphBuilder] Generated {self.walking_edge_count} walking edges with geometry")

    def _generate_transfer_edges(self):
        """
        Generate transfer edges at interchange points.
        Adds transfer penalty when switching between modes.
        """
        penalty = settings.TRANSFER_PENALTY_MIN

        # Find nodes that are very close (within 100m) and different modes
        all_nodes = list(self.G.nodes(data=True))

        for i, (node1_id, node1_data) in enumerate(all_nodes):
            for j, (node2_id, node2_data) in enumerate(all_nodes):
                if i >= j:
                    continue

                mode1 = node1_data.get("mode", "")
                mode2 = node2_data.get("mode", "")

                if mode1 == mode2:
                    continue

                dist_m = haversine_distance(
                    node1_data["lat"], node1_data["lon"],
                    node2_data["lat"], node2_data["lon"]
                )

                # Transfer points within 200m
                if dist_m <= 200:
                    walk_time = (dist_m / 1000 / settings.WALKING_SPEED_KMH) * 60

                    # Add transfer edge with penalty
                    transfer_time = walk_time + penalty

                    # Startup fallback only; route responses lazily upgrade
                    # transfer walking geometry through OSRM before display.
                    straight = [[node1_data["lat"], node1_data["lon"]], [node2_data["lat"], node2_data["lon"]]]

                    if not self.G.has_edge(node1_id, node2_id):
                        self.G.add_edge(
                            node1_id, node2_id,
                            time=round(transfer_time, 1),
                            fare=0,
                            distance=round(dist_m / 1000, 3),
                            mode="transfer",
                            line=None,
                            geometry=straight,
                        )
                        self.transfer_edge_count += 1

                    if not self.G.has_edge(node2_id, node1_id):
                        self.G.add_edge(
                            node2_id, node1_id,
                            time=round(transfer_time, 1),
                            fare=0,
                            distance=round(dist_m / 1000, 3),
                            mode="transfer",
                            line=None,
                            geometry=straight[::-1],
                        )
                        self.transfer_edge_count += 1

        print(f"[GraphBuilder] Generated {self.transfer_edge_count} transfer edges with geometry")

    def _parse_gtfs_time(self, time_str: str) -> float:
        """Parse GTFS time string (HH:MM:SS) to minutes from midnight."""
        parts = time_str.strip().split(":")
        hours = int(parts[0])
        minutes = int(parts[1])
        return hours * 60 + minutes

    def get_station_info(self, station_id: str) -> Optional[dict]:
        """Get station info by ID."""
        return self.stations.get(station_id)

    def get_all_stations(self) -> List[dict]:
        """Get all stations/stops."""
        return list(self.stations.values())

    def get_nearby_stops(self, lat: float, lon: float, radius_m: float = 500) -> List[dict]:
        """Find stops within radius of given coordinates."""
        nearby = []
        for station_id, info in self.stations.items():
            dist = haversine_distance(lat, lon, info["lat"], info["lon"])
            if dist <= radius_m:
                nearby.append({**info, "distance_m": round(dist, 1)})
        nearby.sort(key=lambda x: x["distance_m"])
        return nearby

    def get_graph_stats(self) -> dict:
        """Get graph statistics."""
        modes = {}
        for u, v, data in self.G.edges(data=True):
            mode = data.get("mode", "unknown")
            modes[mode] = modes.get(mode, 0) + 1

        return {
            "total_nodes": self.G.number_of_nodes(),
            "total_edges": self.G.number_of_edges(),
            "metro_stations": len(self.metro_stations),
            "bus_stops": len(self.bus_stops),
            "walking_edges": modes.get("walking", 0),
            "transfer_edges": modes.get("transfer", 0),
        }
