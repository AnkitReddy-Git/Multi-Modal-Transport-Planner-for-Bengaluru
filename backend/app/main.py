"""
PurpleLink - Multi-Modal Transport Planner for Bengaluru
FastAPI Application Entry Point

ITS Architecture: Application Layer → Processing Layer → Data Layer

This is the main entry point that:
1. Initializes the transport graph on startup
2. Registers all API routes
3. Configures CORS for frontend communication
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.graph.graph_builder import TransportGraph
from app.services.disruption_service import DisruptionService
from app.routes import stations, routing, disruptions


# Global instances
transport_graph = TransportGraph()
disruption_service = DisruptionService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - builds graph on startup."""
    print("=" * 60)
    print("  PurpleLink - Multi-Modal Transport Planner")
    print("  Bengaluru ITS Platform v1.0")
    print("=" * 60)

    # Build the transport graph from datasets
    transport_graph.build()

    # Set graph references in route modules
    stations.set_transport_graph(transport_graph)
    routing.set_transport_graph(transport_graph)
    routing.set_disruption_service(disruption_service)
    disruptions.set_transport_graph(transport_graph)
    disruptions.set_disruption_service(disruption_service)

    # Set original graph in disruption service
    disruption_service.set_original_graph(transport_graph.G)

    stats = transport_graph.get_graph_stats()
    print(f"\n[Startup] Graph ready:")
    print(f"  Nodes: {stats['total_nodes']}")
    print(f"  Edges: {stats['total_edges']}")
    print(f"  Metro: {stats['metro_stations']} stations")
    print(f"  Bus:   {stats['bus_stops']} stops")
    print(f"  Walk:  {stats['walking_edges']} edges")
    print(f"  Xfer:  {stats['transfer_edges']} edges")
    print("=" * 60)

    yield

    print("[Shutdown] PurpleLink shutting down...")


# Create FastAPI app
app = FastAPI(
    title="PurpleLink API",
    description="Multi-Modal Transport Planner for Bengaluru - ITS Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(stations.router)
app.include_router(routing.router)
app.include_router(disruptions.router)


@app.get("/")
async def root():
    return {
        "name": "PurpleLink API",
        "version": "1.0.0",
        "description": "Multi-Modal Transport Planner for Bengaluru",
        "endpoints": {
            "stations": "/api/stations",
            "route": "/api/route",
            "route_compare": "/api/route/compare",
            "nearby_stops": "/api/nearby-stops",
            "disruptions": "/api/disruptions",
            "graph_stats": "/api/graph-stats",
        },
    }


@app.get("/health")
async def health():
    stats = transport_graph.get_graph_stats()
    return {
        "status": "healthy",
        "graph_nodes": stats["total_nodes"],
        "graph_edges": stats["total_edges"],
        "active_disruptions": len(disruption_service.get_active_disruptions()),
    }
