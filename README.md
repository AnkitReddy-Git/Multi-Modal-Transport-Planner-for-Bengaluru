# 🟣 PurpleLink — Multi-Modal Transport Planner for Bengaluru

**An Intelligent Transportation System (ITS) web application** that integrates Namma Metro Purple Line, BMTC bus routes, and walking connections into a unified **graph-based multi-modal journey planner**.

Built using **ITS principles** and **Advanced Traveler Information System (ATIS)** concepts, this platform enables users to plan optimized journeys across multiple transport modes in Bengaluru.

---

## 🎯 Project Objective

Develop a graph-based multi-modal journey planning platform that:

- ✅ Integrates **Metro + Bus + Walking** into one transport graph
- ✅ Computes optimized routes using **Dijkstra's Algorithm**
- ✅ Supports **4 optimization preferences** (fastest, cheapest, least transfers, least walking)
- ✅ Visualizes routes interactively on a **dark-themed Leaflet map**
- ✅ Calculates **travel time, fare, walking distance, and transfers**
- ✅ Simulates **route disruptions** for ITS resilience testing

---

## 🧱 Software Architecture — 3-Layer ITS Model

```
┌─────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                         │
│         React.js + Tailwind CSS + React-Leaflet             │
│    Route Planner │ Map View │ Comparison │ Disruptions      │
├─────────────────────────────────────────────────────────────┤
│                   PROCESSING LAYER                          │
│              FastAPI + NetworkX + Dijkstra                   │
│    Graph Engine │ Routing │ Fare Calc │ Transfer Handler    │
├─────────────────────────────────────────────────────────────┤
│                      DATA LAYER                             │
│         CSV/GTFS Datasets + Supabase (Optional)             │
│    Metro Data │ Bus GTFS │ Walking Edges │ OpenStreetMap    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm 9+

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file in `backend/`:

```env
SUPABASE_URL=           # Optional - works without it
SUPABASE_KEY=           # Optional - works without it
```

Start the backend server:

```bash
uvicorn app.main:app --reload --port 8000
```

You should see:

```
============================================================
  PurpleLink - Multi-Modal Transport Planner
  Bengaluru ITS Platform v1.0
============================================================
[GraphBuilder] Building transport graph...
[GraphBuilder] Loaded 37 metro stations
[GraphBuilder] Loaded 72 metro edges
[GraphBuilder] Loaded 80 bus stops
[GraphBuilder] Loaded 128 bus edges
[GraphBuilder] Generated 134 walking edges
[GraphBuilder] Graph built: 117 nodes, 334 edges
============================================================
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

---

## ✨ Core Features

### 🗺️ Multi-Modal Route Planning
- Enter source and destination stations
- Choose from 4 optimization preferences
- Get step-by-step journey breakdown (Walk → Bus → Metro → Walk)

### 📊 Route Comparison Dashboard
- Compare up to 3 alternative routes side-by-side
- Each card shows: total time, fare, transfers, walking distance
- Click a card to highlight that route on the map

### 🔁 Route Disruption Simulator (ITS Feature)
- **Close a station** — removes it from the graph
- **Disable an edge** — blocks a specific connection
- **Add delay** — increases travel time on affected segments
- Routes dynamically recompute around disruptions
- *This directly aligns with ITS traffic management and resilience systems*

### 💰 Fare Estimation
- Metro: Distance-based slab fare (₹10 – ₹60)
- Bus: ₹5 base + ₹1/km (approximate BMTC ordinary fare)
- Detailed fare breakdown per mode

### 🚶 Walking Integration
- Walking edges auto-generated between stops within 500m radius
- Uses OSRM foot routing for displayed walking geometry
- Falls back to Haversine straight-line approximation when routing is unavailable

---

## 📂 Project Structure

```
PurpleLink/
│
├── backend/                    # FastAPI Server (Processing + Data Layer)
│   ├── app/
│   │   ├── algorithms/
│   │   │   ├── dijkstra.py         # Dijkstra's shortest path implementation
│   │   │   └── route_optimizer.py  # Multi-route comparison engine
│   │   ├── graph/
│   │   │   ├── graph_builder.py    # Unified transport graph constructor
│   │   │   └── transfer_handler.py # Transfer penalty logic
│   │   ├── models/
│   │   │   └── models.py          # Pydantic request/response schemas
│   │   ├── routes/
│   │   │   ├── stations.py        # GET /api/stations, /api/nearby-stops
│   │   │   ├── routing.py         # GET /api/route, /api/route/compare
│   │   │   └── disruptions.py     # CRUD /api/disruptions
│   │   ├── services/
│   │   │   ├── osrm_service.py    # OSRM route geometry with fallback cache
│   │   │   ├── fare_service.py    # Fare calculation module
│   │   │   ├── disruption_service.py  # Disruption simulation engine
│   │   │   └── geocoding_service.py   # Nominatim geocoding
│   │   ├── database/
│   │   │   └── database.py        # Optional Supabase integration
│   │   ├── config.py              # Environment & settings
│   │   └── main.py                # FastAPI app entry point
│   ├── requirements.txt
│   └── .env
│
├── datasets/                   # Transport Data (Data Layer)
│   ├── metro/
│   │   ├── purple_line.csv         # 37 Purple Line stations with GPS coords
│   │   └── metro_edges.csv         # Bidirectional station connections
│   └── bus/
│       ├── stops.txt               # 80 BMTC bus stops (GTFS format)
│       ├── routes.txt              # 18 bus routes
│       ├── trips.txt               # Trip instances per route
│       └── stop_times.txt          # Stop sequences with arrival times
│
├── frontend/                   # React App (Application Layer)
│   ├── src/
│   │   ├── components/
│   │   │   ├── MapView.jsx         # React-Leaflet interactive map
│   │   │   ├── InputPanel.jsx      # Route planner with search dropdowns
│   │   │   ├── RouteDetails.jsx    # Step-by-step journey timeline
│   │   │   ├── RouteComparison.jsx # Side-by-side route cards
│   │   │   ├── DisruptionPanel.jsx # Disruption simulator controls
│   │   │   ├── Legend.jsx          # Transport mode color legend
│   │   │   └── StatsBar.jsx        # Network statistics bar
│   │   ├── pages/
│   │   │   └── HomePage.jsx        # Main dashboard layout
│   │   ├── services/
│   │   │   └── api.js              # Axios API client
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css               # Design system & Tailwind config
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
│
├── .gitignore
└── README.md
```

---

## 🧠 Graph Model

### Nodes
| Type | Count | Description |
|------|-------|-------------|
| Metro Station | 37 | All Purple Line stations (Challaghatta → Whitefield) |
| Bus Stop | 80 | BMTC stops around Purple Line corridor |

### Edges
| Type | Description | Weight |
|------|-------------|--------|
| Metro | Sequential station connections (bidirectional) | time, fare, distance |
| Bus | GTFS-derived stop connections (bidirectional) | time, fare, distance |
| Walking | Auto-generated within 500m radius | time (from distance), fare=0 |
| Transfer | Mode-switching penalty edges | time + 5min penalty |

### Edge Attributes
```json
{
  "time": 3.0,        // minutes
  "fare": 10.0,       // INR
  "distance": 1.2,    // km
  "mode": "metro",    // metro | bus | walking | transfer
  "line": "purple"    // route/line identifier
}
```

---

## 🧠 Routing Logic — Dijkstra's Algorithm

### Weighted Scoring Formula

```
score = (time_weight × time) + (fare_weight × fare) + 
        (transfer_weight × transfers) + (walking_weight × walking_distance)
```

### Optimization Weight Profiles

| Preference | Time | Fare | Transfers | Walking |
|-----------|------|------|-----------|---------|
| 🚀 Fastest | 1.0 | 0.0 | 0.3 | 0.1 |
| 💰 Cheapest | 0.2 | 1.0 | 0.1 | 0.0 |
| 🔄 Least Transfers | 0.3 | 0.0 | 1.0 | 0.1 |
| 🚶 Least Walking | 0.2 | 0.0 | 0.1 | 1.0 |

---

## 🔌 API Endpoints

### Stations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stations` | All stations (optional `?type=metro&mode=bus` filters) |
| GET | `/api/stations/{id}` | Single station by ID |
| GET | `/api/stations/search/{query}` | Fuzzy name search |
| GET | `/api/nearby-stops?lat=..&lon=..&radius=500` | Nearby stops by coordinates |
| GET | `/api/graph-stats` | Graph statistics |

### Routing
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/route?source=M15&destination=M22&preference=fastest` | Compute optimized route |
| GET | `/api/route/compare?source=M15&destination=M37` | Compare up to 3 alternatives |

### Disruptions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/disruptions` | List active disruptions |
| POST | `/api/disruptions` | Create disruption |
| DELETE | `/api/disruptions/{id}` | Remove disruption |
| POST | `/api/disruptions/reset` | Reset all disruptions |

### Example: Create Disruption
```json
POST /api/disruptions
{
  "type": "station_closed",
  "affected_node": "M19",
  "description": "MG Road station closed for maintenance"
}
```

---

## 🗺️ Map Visualization

| Mode | Color | Style |
|------|-------|-------|
| 🟣 Metro | `#7c3aed` (Purple) | Solid thick line |
| 🔴 Bus | `#ef4444` (Red) | Solid medium line |
| 🟢 Walking | `#22c55e` (Green) | Dashed line |
| 🟡 Transfer | `#f59e0b` (Amber) | Dotted line |

Map tiles: **CARTO Dark Matter** (dark theme)

---

## 📊 Datasets

### 🟣 Metro Dataset (37 stations)
Manually structured Purple Line dataset covering:
- Challaghatta (West) → Whitefield/Kadugodi (East)
- Key interchanges: Majestic, MG Road

### 🚌 BMTC Bus Dataset
Synthetic GTFS dataset with:
- **80 bus stops** around Purple Line corridor
- **18 bus routes** connecting major areas
- Focus areas: Majestic, MG Road, Indiranagar, Baiyappanahalli, KR Puram, Whitefield

---

## 🔧 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React.js + Vite | UI framework |
| Styling | Tailwind CSS v4 | Utility-first CSS |
| Maps | React-Leaflet + Leaflet.js | Map visualization |
| Icons | Lucide React | UI icons |
| Backend | FastAPI + Uvicorn | REST API server |
| Graph | NetworkX | Graph data structure |
| Routing | Dijkstra's Algorithm | Shortest path computation |
| Data | Pandas | Dataset parsing (CSV/GTFS) |
| Database | Supabase PostgreSQL | Optional persistence |
| Geometry | OSRM public API | Bus road geometry and walking route geometry |
| Geocoding | Nominatim API | Place name → coordinates |

---

## 🎓 ITS / ATIS Alignment

This project directly aligns with:

- **Advanced Traveler Information Systems (ATIS)** — real-time route information to travelers
- **Intelligent Transportation Systems (ITS)** — technology-driven transport optimization
- **Multi-modal Transport Integration** — seamless metro + bus + walking journeys
- **Graph-based Route Optimization** — academic foundation in graph theory
- **Urban Mobility Planning** — smart city transit intelligence
- **Transport Resilience** — disruption simulation and dynamic rerouting

---

## 🚫 Not Used (By Design)

| Technology | Reason |
|-----------|--------|
| Firebase | Not needed; Supabase + CSV fallback used |
| Google Maps API | Paid; using free OpenStreetMap + Leaflet |
| Machine Learning | Out of scope; graph algorithms suffice |
| IoT | Academic scope; simulated data used |
| Docker | Lightweight setup; direct Python/Node |
| Authentication | Not required for academic demo |

---

## 📝 License

Academic project — for educational purposes.

---

**Built with ❤️ for Bengaluru's commuters**
