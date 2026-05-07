/**
 * HomePage - Main dashboard assembling all components.
 */
import { useState, useEffect } from 'react';
import MapView from '../components/MapView';
import InputPanel from '../components/InputPanel';
import RouteDetails from '../components/RouteDetails';
import RouteComparison from '../components/RouteComparison';
import DisruptionPanel from '../components/DisruptionPanel';
import Legend from '../components/Legend';
import StatsBar from '../components/StatsBar';
import {
  getStations, getGraphStats, getRoute, getRouteComparison,
  getDisruptions, createDisruption, deleteDisruption, resetDisruptions,
} from '../services/api';

export default function HomePage() {
  const [stations, setStations] = useState([]);
  const [stats, setStats] = useState(null);
  const [route, setRoute] = useState(null);
  const [fareBreakdown, setFareBreakdown] = useState(null);
  const [compRoutes, setCompRoutes] = useState([]);
  const [selectedRoute, setSelectedRoute] = useState(0);
  const [disruptions, setDisruptions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showDisruption, setShowDisruption] = useState(false);

  // Load initial data
  useEffect(() => {
    async function load() {
      try {
        const [stRes, stStats, dRes] = await Promise.all([
          getStations(), getGraphStats(), getDisruptions(),
        ]);
        setStations(stRes.stations || []);
        setStats(stStats.stats || null);
        setDisruptions(dRes.disruptions || []);
      } catch (e) {
        setError('Failed to connect to backend. Is the server running?');
        console.error(e);
      }
    }
    load();
  }, []);

  const handleFindRoute = async (source, dest, pref) => {
    setLoading(true); setError(null); setCompRoutes([]);
    try {
      const res = await getRoute(source, dest, pref);
      setRoute(res);
      setFareBreakdown(res.fare_breakdown || null);
    } catch (e) {
      setError(e.response?.data?.detail || 'Route not found');
      setRoute(null);
    }
    setLoading(false);
  };

  const handleCompare = async (source, dest) => {
    setLoading(true); setError(null);
    try {
      const res = await getRouteComparison(source, dest);
      const rts = (res.routes || []).map(r => r.route || r);
      setCompRoutes(rts);
      if (rts.length > 0) {
        setRoute({ route: rts[0] });
        setFareBreakdown(res.routes?.[0]?.fare_breakdown || null);
      }
      setSelectedRoute(0);
    } catch (e) {
      setError(e.response?.data?.detail || 'Comparison failed');
    }
    setLoading(false);
  };

  const handleSelectComp = (idx) => {
    setSelectedRoute(idx);
    if (compRoutes[idx]) {
      setRoute({ route: compRoutes[idx] });
    }
  };

  const handleCreateDisruption = async (data) => {
    try {
      await createDisruption(data);
      const r = await getDisruptions();
      setDisruptions(r.disruptions || []);
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to create disruption');
    }
  };

  const handleDeleteDisruption = async (id) => {
    try {
      await deleteDisruption(id);
      const r = await getDisruptions();
      setDisruptions(r.disruptions || []);
    } catch (e) { console.error(e); }
  };

  const handleResetDisruptions = async () => {
    try {
      await resetDisruptions();
      setDisruptions([]);
    } catch (e) { console.error(e); }
  };

  return (
    <div className="h-screen flex flex-col overflow-hidden" style={{ background: '#F1F5F9' }}>
      {/* Top Bar */}
      <header className="flex items-center justify-between px-5 py-3 glass-panel border-0 border-b border-slate-200 rounded-none z-20">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl flex items-center justify-center"
            style={{ background: 'linear-gradient(135deg, #2563EB, #3B82F6)' }}>
            <span className="text-lg">�</span>
          </div>
          <div>
            <h1 className="text-lg font-bold text-slate-900 leading-tight">
              Bengaluru Transit
            </h1>
            <p className="text-xs text-slate-500 font-medium">Multi-Modal Transport Planner</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <button onClick={() => setShowDisruption(!showDisruption)}
            className={`btn-ghost text-xs flex items-center gap-1.5 ${showDisruption ? 'bg-amber-50 border-amber-200 text-amber-700' : ''}`}>
            ⚠️ Disruptions {disruptions.length > 0 && `(${disruptions.length})`}
          </button>
          <Legend />
        </div>
      </header>

      {/* Stats Bar */}
      <div className="px-5 py-2 z-10">
        <StatsBar stats={stats} disruptionCount={disruptions.length} />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden px-5 pb-4 gap-4">
        {/* Left Sidebar */}
        <div className="flex flex-col gap-4 overflow-y-auto" style={{ width: 340, flexShrink: 0 }}>
          <InputPanel stations={stations} onFindRoute={handleFindRoute}
            onCompareRoutes={handleCompare} loading={loading} />
          {showDisruption && (
            <DisruptionPanel stations={stations} disruptions={disruptions}
              onCreate={handleCreateDisruption} onDelete={handleDeleteDisruption}
              onReset={handleResetDisruptions} loading={loading} />
          )}
        </div>

        {/* Map */}
        <div className="flex-1 rounded-2xl overflow-hidden border border-slate-200 relative">
          {error && (
            <div className="absolute top-4 left-1/2 -translate-x-1/2 z-50 bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded-xl text-sm backdrop-blur-lg">
              {error}
              <button onClick={() => setError(null)} className="ml-3 text-red-500 hover:text-red-700">✕</button>
            </div>
          )}
          <MapView stations={stations} route={route} selectedRouteIndex={selectedRoute} comparisonRoutes={compRoutes} />
        </div>

        {/* Right Sidebar */}
        {route && (
          <div className="flex flex-col gap-4 overflow-y-auto" style={{ width: 320, flexShrink: 0 }}>
            <RouteDetails route={route} fareBreakdown={fareBreakdown} />
          </div>
        )}
      </div>

      {/* Bottom Comparison */}
      {compRoutes.length > 1 && (
        <div className="px-5 pb-4 z-10">
          <RouteComparison routes={compRoutes} selectedIndex={selectedRoute} onSelect={handleSelectComp} />
        </div>
      )}
    </div>
  );
}
