/**
 * MapView Component
 * Interactive Leaflet map centered on Bengaluru displaying metro stations,
 * bus stops, and route polylines with color coding by transport mode.
 */

import { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap, CircleMarker } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix Leaflet default marker icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Bengaluru center
const BENGALURU_CENTER = [12.9716, 77.5946];
const DEFAULT_ZOOM = 12;

// Custom icons
const createIcon = (color, size = 10) => {
  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="
      width: ${size}px;
      height: ${size}px;
      background: ${color};
      border: 2px solid white;
      border-radius: 50%;
      box-shadow: 0 1px 4px rgba(0,0,0,0.3);
    "></div>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
  });
};

const metroIcon = createIcon('#7C3AED', 14);
const metroInterchangeIcon = createIcon('#A78BFA', 18);

// Mode colors for polylines
const MODE_COLORS = {
  metro: '#7C3AED',
  bus: '#EA580C',
  walking: '#059669',
  transfer: '#D97706',
};

const getRoutePathOptions = (mode, color) => ({
  color,
  weight: mode === 'metro' ? 7 : mode === 'walking' || mode === 'transfer' ? 3 : 4,
  opacity: mode === 'metro' ? 0.92 : 0.86,
  dashArray: mode === 'walking' ? '8, 10' : mode === 'transfer' ? '4, 8' : null,
  lineCap: 'round',
  lineJoin: 'round',
});

// Animate map to fit route
function FitBounds({ bounds }) {
  const map = useMap();
  useEffect(() => {
    if (bounds && bounds.length > 0) {
      map.fitBounds(bounds, { padding: [60, 60], maxZoom: 15 });
    }
  }, [bounds, map]);
  return null;
}

function AnimatedPolyline({ positions, pathOptions, animationKey }) {
  const pathRef = useRef(null);
  const dashArray = pathOptions?.dashArray || '';

  useEffect(() => {
    const leafletPath = pathRef.current;
    const element = leafletPath?.getElement?.();

    if (!element?.getTotalLength) {
      return undefined;
    }

    const length = element.getTotalLength();
    if (!Number.isFinite(length) || length <= 0) {
      return undefined;
    }

    element.style.transition = 'none';
    element.style.strokeDasharray = `${length} ${length}`;
    element.style.strokeDashoffset = `${length}`;

    const frame = requestAnimationFrame(() => {
      element.style.transition = 'stroke-dashoffset 700ms ease-out';
      element.style.strokeDashoffset = '0';
    });

    const timeout = window.setTimeout(() => {
      element.style.transition = '';
      element.style.strokeDashoffset = '';
      element.style.strokeDasharray = dashArray;
    }, 760);

    return () => {
      cancelAnimationFrame(frame);
      window.clearTimeout(timeout);
    };
  }, [animationKey, dashArray, positions]);

  return <Polyline ref={pathRef} positions={positions} pathOptions={pathOptions} />;
}

export default function MapView({ stations = [], route = null, selectedRouteIndex = 0 }) {
  // Determine which route to display
  const activeRoute = route;
  const activeRouteData = Array.isArray(activeRoute?.route) ? activeRoute : activeRoute?.route;
  const routeSteps = activeRouteData?.route || [];
  const routeGeometry = activeRouteData?.geometry || [];
  const routeKey = `${activeRouteData?.route_id || 'route'}-${selectedRouteIndex}`;

  // Build bounds for route
  const bounds = routeGeometry.length > 1 ? routeGeometry : null;

  // Group stations by type
  const metroStations = stations.filter(s => s.mode === 'metro');
  const busStops = stations.filter(s => s.mode === 'bus');

  // Build polyline segments from route steps (color by mode)
  const polylineSegments = routeSteps.map((step, idx) => {
    const coords = step.geometry || [];
    const color = MODE_COLORS[step.mode] || '#7c3aed';
    return {
      coords,
      color,
      mode: step.mode,
      key: `${routeKey}-${idx}-${step.mode}`,
      pathOptions: getRoutePathOptions(step.mode, color),
    };
  });

  const startPoint = routeSteps[0]?.geometry?.[0] || routeGeometry[0] || BENGALURU_CENTER;
  const endGeometry = routeSteps[routeSteps.length - 1]?.geometry || routeGeometry;
  const endPoint = endGeometry?.slice(-1)?.[0] || BENGALURU_CENTER;

  return (
    <MapContainer
      center={BENGALURU_CENTER}
      zoom={DEFAULT_ZOOM}
      style={{ height: '100%', width: '100%' }}
      zoomControl={true}
    >
      {/* Light-themed map tiles */}
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
      />

      {/* Fit map to route bounds */}
      {bounds && <FitBounds bounds={bounds} />}

      {/* Metro stations */}
      {metroStations.map((station) => (
        <Marker
          key={station.id}
          position={[station.lat, station.lon]}
          icon={station.type === 'metro_interchange' ? metroInterchangeIcon : metroIcon}
        >
          <Popup>
            <div>
              <div style={{ fontWeight: 600, color: '#7C3AED', marginBottom: 4 }}>
                🚇 {station.name}
              </div>
              <div style={{ fontSize: 11, color: '#64748B' }}>
                ID: {station.id} • Metro Line
              </div>
            </div>
          </Popup>
        </Marker>
      ))}

      {/* Bus stops - smaller markers */}
      {busStops.map((stop) => (
        <CircleMarker
          key={stop.id}
          center={[stop.lat, stop.lon]}
          radius={5}
          pathOptions={{
            color: '#EA580C',
            fillColor: '#EA580C',
            fillOpacity: 0.7,
            weight: 1,
          }}
        >
          <Popup>
            <div>
              <div style={{ fontWeight: 600, color: '#EA580C', marginBottom: 4 }}>
                🚌 {stop.name}
              </div>
              <div style={{ fontSize: 11, color: '#64748B' }}>
                ID: {stop.id}
              </div>
            </div>
          </Popup>
        </CircleMarker>
      ))}

      {/* Route polylines - one per step, colored by mode */}
      {polylineSegments.map((seg) => (
        seg.coords.length >= 2 && (
          <AnimatedPolyline
            key={seg.key}
            positions={seg.coords}
            pathOptions={seg.pathOptions}
            animationKey={seg.key}
          />
        )
      ))}

      {/* Start and end markers for active route */}
      {routeSteps.length > 0 && (
        <>
          <Marker
            position={startPoint}
            icon={L.divIcon({
              className: 'custom-marker',
              html: `<div style="
                width: 22px; height: 22px;
                background: #059669;
                border: 2px solid white;
                border-radius: 50%;
                box-shadow: 0 1px 6px rgba(0,0,0,0.25);
                display: flex; align-items: center; justify-content: center;
                font-size: 10px; color: white; font-weight: 700;
              ">A</div>`,
              iconSize: [22, 22],
              iconAnchor: [11, 11],
            })}
          >
            <Popup>
              <div style={{ fontWeight: 600, color: '#059669' }}>
                📍 Start: {routeSteps[0].from_name}
              </div>
            </Popup>
          </Marker>

          <Marker
            position={endPoint}
            icon={L.divIcon({
              className: 'custom-marker',
              html: `<div style="
                width: 22px; height: 22px;
                background: #DC2626;
                border: 2px solid white;
                border-radius: 50%;
                box-shadow: 0 1px 6px rgba(0,0,0,0.25);
                display: flex; align-items: center; justify-content: center;
                font-size: 10px; color: white; font-weight: 700;
              ">B</div>`,
              iconSize: [22, 22],
              iconAnchor: [11, 11],
            })}
          >
            <Popup>
              <div style={{ fontWeight: 600, color: '#DC2626' }}>
                🏁 End: {routeSteps[routeSteps.length - 1].to_name}
              </div>
            </Popup>
          </Marker>
        </>
      )}
    </MapContainer>
  );
}
