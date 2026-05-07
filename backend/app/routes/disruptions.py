"""
Disruptions API Routes
Endpoints for the Route Disruption Simulator feature.
"""

from fastapi import APIRouter, HTTPException
from typing import List

from app.models.models import DisruptionCreate, Disruption, DisruptionType

router = APIRouter(prefix="/api", tags=["disruptions"])

# Reference set during app startup
_disruption_service = None
_transport_graph = None


def set_disruption_service(service):
    global _disruption_service
    _disruption_service = service


def set_transport_graph(graph):
    global _transport_graph
    _transport_graph = graph


@router.get("/disruptions")
async def get_disruptions():
    """Get all active disruptions."""
    disruptions = _disruption_service.get_active_disruptions()
    return {
        "disruptions": [d.dict() for d in disruptions],
        "count": len(disruptions),
    }


@router.post("/disruptions")
async def create_disruption(data: DisruptionCreate):
    """
    Create a new disruption.

    Examples:
    - Close MG Road station: {"type": "station_closed", "affected_node": "M19", "description": "MG Road station closed"}
    - Disable edge: {"type": "edge_disabled", "affected_edge_from": "M15", "affected_edge_to": "M16", "description": "Track maintenance"}
    - Add delay: {"type": "delay", "affected_node": "M15", "delay_minutes": 10, "description": "Signal failure"}
    """
    # Validate affected node/edge exists
    if data.type == DisruptionType.STATION_CLOSED:
        if not data.affected_node:
            raise HTTPException(status_code=400, detail="affected_node is required for station_closed")
        if not _transport_graph.get_station_info(data.affected_node):
            raise HTTPException(status_code=404, detail=f"Station not found: {data.affected_node}")

    elif data.type == DisruptionType.EDGE_DISABLED:
        if not data.affected_edge_from or not data.affected_edge_to:
            raise HTTPException(
                status_code=400,
                detail="affected_edge_from and affected_edge_to are required for edge_disabled"
            )

    elif data.type == DisruptionType.DELAY:
        if not data.affected_node and not (data.affected_edge_from and data.affected_edge_to):
            raise HTTPException(
                status_code=400,
                detail="Either affected_node or affected_edge_from/to required for delay"
            )
        if not data.delay_minutes or data.delay_minutes <= 0:
            raise HTTPException(status_code=400, detail="delay_minutes must be positive")

    disruption = _disruption_service.add_disruption(
        disruption_type=data.type,
        affected_node=data.affected_node,
        affected_edge_from=data.affected_edge_from,
        affected_edge_to=data.affected_edge_to,
        delay_minutes=data.delay_minutes or 0,
        description=data.description or "",
    )

    return {"disruption": disruption.dict(), "message": "Disruption created successfully"}


@router.delete("/disruptions/{disruption_id}")
async def delete_disruption(disruption_id: str):
    """Remove a specific disruption."""
    success = _disruption_service.remove_disruption(disruption_id)
    if success:
        return {"message": "Disruption removed", "id": disruption_id}
    raise HTTPException(status_code=404, detail=f"Disruption not found: {disruption_id}")


@router.post("/disruptions/reset")
async def reset_disruptions():
    """Reset all active disruptions."""
    _disruption_service.reset_all()
    return {"message": "All disruptions reset"}
