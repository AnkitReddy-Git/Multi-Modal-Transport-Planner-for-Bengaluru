import json
import unittest
from unittest.mock import patch

import networkx as nx

from app.algorithms.dijkstra import find_shortest_path
from app.models.models import OptimizationPreference
from app.services import osrm_service


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def build_two_node_graph(mode="bus", geometry=None):
    graph = nx.DiGraph()
    stations = {
        "A": {"name": "Alpha", "lat": 12.0, "lon": 77.0},
        "B": {"name": "Beta", "lat": 12.1, "lon": 77.1},
    }

    graph.add_node("A", **stations["A"])
    graph.add_node("B", **stations["B"])
    graph.add_edge(
        "A",
        "B",
        time=6,
        fare=0,
        distance=1.2,
        mode=mode,
        line="purple" if mode == "metro" else "500",
        geometry=geometry or [[12.0, 77.0], [12.1, 77.1]],
    )
    return graph, stations


class OSRMServiceTests(unittest.TestCase):
    def setUp(self):
        osrm_service.clear_cache()

    def test_fetch_osrm_geometry_converts_geojson_to_leaflet_order(self):
        payload = {
            "routes": [
                {
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[77.0, 12.0], [77.05, 12.05]],
                    }
                }
            ]
        }

        with patch.object(
            osrm_service.urllib.request,
            "urlopen",
            return_value=FakeResponse(payload),
        ):
            geometry = osrm_service._fetch_osrm_geometry(
                "driving", 77.0, 12.0, 77.05, 12.05
            )

        self.assertEqual(geometry, [[12.0, 77.0], [12.05, 77.05]])

    def test_route_geometry_uses_in_memory_cache(self):
        routed_geometry = [[12.0, 77.0], [12.05, 77.05], [12.1, 77.1]]

        with patch.object(
            osrm_service,
            "_fetch_osrm_geometry",
            return_value=routed_geometry,
        ) as fetch:
            first = osrm_service.get_route_geometry("foot", 12.0, 77.0, 12.1, 77.1)
            second = osrm_service.get_route_geometry("foot", 12.0, 77.0, 12.1, 77.1)

        self.assertEqual(first, routed_geometry)
        self.assertEqual(second, routed_geometry)
        self.assertEqual(fetch.call_count, 1)

    def test_route_geometry_falls_back_when_osrm_fails(self):
        with patch.object(osrm_service, "_fetch_osrm_geometry", return_value=None):
            geometry = osrm_service.get_route_geometry("foot", 12.0, 77.0, 12.1, 77.1)

        self.assertGreater(len(geometry), 2)
        self.assertEqual(geometry[0], [12.0, 77.0])
        self.assertEqual(geometry[-1], [12.1, 77.1])


class DijkstraGeometryTests(unittest.TestCase):
    def test_bus_step_and_route_geometry_are_osrm_enhanced(self):
        graph, stations = build_two_node_graph(mode="bus")
        routed_geometry = [[12.0, 77.0], [12.04, 77.08], [12.1, 77.1]]

        with patch(
            "app.algorithms.dijkstra.get_bus_route_geometry",
            return_value=routed_geometry,
        ):
            route = find_shortest_path(
                graph,
                "A",
                "B",
                OptimizationPreference.FASTEST,
                stations,
                {},
            )

        self.assertIsNotNone(route)
        self.assertEqual(route.route[0].geometry, routed_geometry)
        self.assertEqual(route.geometry, routed_geometry)

    def test_walking_step_and_route_geometry_are_osrm_enhanced(self):
        graph, stations = build_two_node_graph(mode="walking")
        routed_geometry = [[12.0, 77.0], [12.02, 77.04], [12.1, 77.1]]

        with patch(
            "app.algorithms.dijkstra.get_walking_route_geometry",
            return_value=routed_geometry,
        ):
            route = find_shortest_path(
                graph,
                "A",
                "B",
                OptimizationPreference.FASTEST,
                stations,
                {},
            )

        self.assertIsNotNone(route)
        self.assertEqual(route.route[0].geometry, routed_geometry)
        self.assertEqual(route.geometry, routed_geometry)

    def test_metro_geometry_uses_predefined_track_without_osrm(self):
        metro_geometry = [[12.0, 77.0], [12.06, 77.02], [12.1, 77.1]]
        graph, stations = build_two_node_graph(mode="metro", geometry=metro_geometry)

        with patch("app.algorithms.dijkstra.get_bus_route_geometry") as bus_route:
            with patch("app.algorithms.dijkstra.get_walking_route_geometry") as walk_route:
                route = find_shortest_path(
                    graph,
                    "A",
                    "B",
                    OptimizationPreference.FASTEST,
                    stations,
                    {"A": 1, "B": 2},
                )

        self.assertIsNotNone(route)
        self.assertEqual(route.route[0].geometry, metro_geometry)
        self.assertEqual(route.geometry, metro_geometry)
        bus_route.assert_not_called()
        walk_route.assert_not_called()


if __name__ == "__main__":
    unittest.main()
