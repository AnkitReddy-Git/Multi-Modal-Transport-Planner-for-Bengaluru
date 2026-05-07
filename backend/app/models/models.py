"""
Pydantic models for PurpleLink API request/response schemas.
"""

from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class TransportMode(str, Enum):
    METRO = "metro"
    BUS = "bus"
    WALKING = "walking"
    TRANSFER = "transfer"


class OptimizationPreference(str, Enum):
    FASTEST = "fastest"
    CHEAPEST = "cheapest"
    LEAST_TRANSFERS = "least_transfers"
    LEAST_WALKING = "least_walking"


class Station(BaseModel):
    id: str
    name: str
    lat: float
    lon: float
    type: str
    line: Optional[str] = None


class Edge(BaseModel):
    from_station: str
    to_station: str
    time: float
    fare: float
    distance: float
    mode: str
    line: Optional[str] = None


class RouteStep(BaseModel):
    from_station: str
    from_name: str
    to_station: str
    to_name: str
    mode: str
    line: Optional[str] = None
    time: float
    fare: float
    distance: float
    geometry: Optional[List[List[float]]] = None  # [[lat, lon], ...]


class FareBreakdownItem(BaseModel):
    mode: str
    from_name: str
    to_name: str
    fare: float
    stations: Optional[int] = None
    distance_km: Optional[float] = None


class RouteResponse(BaseModel):
    route: List[RouteStep]
    total_time: float
    total_fare: float
    total_distance: float
    transfers: int
    walking_distance: float
    route_id: str
    preference: str
    geometry: List[List[float]]  # Full route polyline [[lat, lon], ...]
    fare_breakdown: Optional[List[FareBreakdownItem]] = None


class RouteComparisonResponse(BaseModel):
    routes: List[RouteResponse]


class DisruptionType(str, Enum):
    STATION_CLOSED = "station_closed"
    EDGE_DISABLED = "edge_disabled"
    DELAY = "delay"


class DisruptionCreate(BaseModel):
    type: DisruptionType
    affected_node: Optional[str] = None
    affected_edge_from: Optional[str] = None
    affected_edge_to: Optional[str] = None
    delay_minutes: Optional[float] = 0
    description: Optional[str] = ""


class Disruption(BaseModel):
    id: str
    type: DisruptionType
    affected_node: Optional[str] = None
    affected_edge_from: Optional[str] = None
    affected_edge_to: Optional[str] = None
    delay_minutes: Optional[float] = 0
    description: Optional[str] = ""
    status: str = "active"


class NearbyStopRequest(BaseModel):
    lat: float
    lon: float
    radius: Optional[float] = 500.0


class GraphStats(BaseModel):
    total_nodes: int
    total_edges: int
    metro_stations: int
    bus_stops: int
    walking_edges: int
    transfer_edges: int
