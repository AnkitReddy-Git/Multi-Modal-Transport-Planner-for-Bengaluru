"""
Disruption Simulation Service
Allows simulating transport disruptions: station closures, edge disabling, delays.
Supports dynamic rerouting — a key ITS/ATIS feature.
"""

import uuid
import copy
import networkx as nx
from typing import Dict, List, Optional

from app.models.models import Disruption, DisruptionType


class DisruptionService:
    """
    Manages transport disruptions for the route disruption simulator.
    Works by maintaining a modified copy of the original graph.
    """

    def __init__(self):
        self.disruptions: Dict[str, Disruption] = {}
        self._original_graph: Optional[nx.DiGraph] = None

    def set_original_graph(self, graph: nx.DiGraph):
        """Store reference to the original graph."""
        self._original_graph = graph

    def add_disruption(
        self,
        disruption_type: DisruptionType,
        affected_node: Optional[str] = None,
        affected_edge_from: Optional[str] = None,
        affected_edge_to: Optional[str] = None,
        delay_minutes: float = 0,
        description: str = "",
    ) -> Disruption:
        """
        Add a new disruption.

        Args:
            disruption_type: Type of disruption
            affected_node: Node ID for station closures
            affected_edge_from: Edge source for edge disruptions
            affected_edge_to: Edge destination for edge disruptions
            delay_minutes: Delay in minutes (for delay type)
            description: Human-readable description

        Returns:
            Created Disruption object
        """
        disruption_id = str(uuid.uuid4())[:8]

        disruption = Disruption(
            id=disruption_id,
            type=disruption_type,
            affected_node=affected_node,
            affected_edge_from=affected_edge_from,
            affected_edge_to=affected_edge_to,
            delay_minutes=delay_minutes,
            description=description,
            status="active",
        )

        self.disruptions[disruption_id] = disruption
        print(f"[DisruptionService] Added disruption: {disruption_type.value} - {description}")

        return disruption

    def remove_disruption(self, disruption_id: str) -> bool:
        """Remove a disruption by ID."""
        if disruption_id in self.disruptions:
            del self.disruptions[disruption_id]
            print(f"[DisruptionService] Removed disruption: {disruption_id}")
            return True
        return False

    def reset_all(self):
        """Remove all active disruptions."""
        count = len(self.disruptions)
        self.disruptions.clear()
        print(f"[DisruptionService] Reset {count} disruptions")

    def get_active_disruptions(self) -> List[Disruption]:
        """Get all active disruptions."""
        return list(self.disruptions.values())

    def get_disrupted_graph(self, original_graph: nx.DiGraph) -> nx.DiGraph:
        """
        Apply all active disruptions to a copy of the graph and return it.
        The original graph is never modified.

        Args:
            original_graph: The original transport graph

        Returns:
            Modified graph with disruptions applied
        """
        if not self.disruptions:
            return original_graph

        # Deep copy the graph
        G = original_graph.copy()

        for disruption in self.disruptions.values():
            if disruption.status != "active":
                continue

            if disruption.type == DisruptionType.STATION_CLOSED:
                self._apply_station_closure(G, disruption)
            elif disruption.type == DisruptionType.EDGE_DISABLED:
                self._apply_edge_disable(G, disruption)
            elif disruption.type == DisruptionType.DELAY:
                self._apply_delay(G, disruption)

        return G

    def _apply_station_closure(self, G: nx.DiGraph, disruption: Disruption):
        """Remove a station node and all its edges from the graph."""
        node_id = disruption.affected_node
        if node_id and node_id in G:
            G.remove_node(node_id)
            print(f"[DisruptionService] Closed station: {node_id}")

    def _apply_edge_disable(self, G: nx.DiGraph, disruption: Disruption):
        """Remove an edge from the graph (both directions)."""
        from_id = disruption.affected_edge_from
        to_id = disruption.affected_edge_to

        if from_id and to_id:
            if G.has_edge(from_id, to_id):
                G.remove_edge(from_id, to_id)
            if G.has_edge(to_id, from_id):
                G.remove_edge(to_id, from_id)
            print(f"[DisruptionService] Disabled edge: {from_id} <-> {to_id}")

    def _apply_delay(self, G: nx.DiGraph, disruption: Disruption):
        """Add delay to edges connected to a node or specific edge."""
        delay = disruption.delay_minutes or 0

        if disruption.affected_node:
            # Add delay to all edges from/to this node
            node_id = disruption.affected_node
            if node_id in G:
                for _, _, data in G.edges(node_id, data=True):
                    data["time"] = data.get("time", 0) + delay
                for u, v, data in G.in_edges(node_id, data=True):
                    data["time"] = data.get("time", 0) + delay
                print(f"[DisruptionService] Added {delay}min delay to station: {node_id}")

        elif disruption.affected_edge_from and disruption.affected_edge_to:
            from_id = disruption.affected_edge_from
            to_id = disruption.affected_edge_to
            if G.has_edge(from_id, to_id):
                G.edges[from_id, to_id]["time"] += delay
            if G.has_edge(to_id, from_id):
                G.edges[to_id, from_id]["time"] += delay
            print(f"[DisruptionService] Added {delay}min delay to edge: {from_id} <-> {to_id}")
