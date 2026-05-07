/**
 * InputPanel Component
 * Route planner input form with searchable station dropdowns and optimization preference selector.
 */

import { useState, useEffect, useRef } from 'react';
import { Search, Navigation, Zap, DollarSign, Shuffle, Footprints, Loader2 } from 'lucide-react';

const PREFERENCES = [
  { value: 'fastest', label: 'Fastest Route', icon: Zap, desc: 'Minimize travel time' },
  { value: 'cheapest', label: 'Cheapest Route', icon: DollarSign, desc: 'Minimize fare cost' },
  { value: 'least_transfers', label: 'Least Transfers', icon: Shuffle, desc: 'Minimize mode changes' },
  { value: 'least_walking', label: 'Least Walking', icon: Footprints, desc: 'Minimize walking distance' },
];

const filterStations = (stations, query) => {
  if (!query || query.length < 1) return [];
  const q = query.toLowerCase();
  return stations
    .filter(s => s.name.toLowerCase().includes(q) || s.id.toLowerCase().includes(q))
    .slice(0, 10);
};

export default function InputPanel({ stations = [], onFindRoute, onCompareRoutes, loading }) {
  const [source, setSource] = useState('');
  const [destination, setDestination] = useState('');
  const [preference, setPreference] = useState('fastest');
  const [showSourceDropdown, setShowSourceDropdown] = useState(false);
  const [showDestDropdown, setShowDestDropdown] = useState(false);
  const [selectedSource, setSelectedSource] = useState(null);
  const [selectedDest, setSelectedDest] = useState(null);

  const sourceRef = useRef(null);
  const destRef = useRef(null);

  const sourceResults = filterStations(stations, source);
  const destResults = filterStations(stations, destination);

  // Close dropdowns on outside click
  useEffect(() => {
    const handleClick = (e) => {
      if (sourceRef.current && !sourceRef.current.contains(e.target)) setShowSourceDropdown(false);
      if (destRef.current && !destRef.current.contains(e.target)) setShowDestDropdown(false);
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const handleSelectSource = (station) => {
    setSource(station.name);
    setSelectedSource(station);
    setShowSourceDropdown(false);
  };

  const handleSelectDest = (station) => {
    setDestination(station.name);
    setSelectedDest(station);
    setShowDestDropdown(false);
  };

  const handleFindRoute = () => {
    if (selectedSource && selectedDest) {
      onFindRoute(selectedSource.id, selectedDest.id, preference);
    }
  };

  const handleCompare = () => {
    if (selectedSource && selectedDest) {
      onCompareRoutes(selectedSource.id, selectedDest.id);
    }
  };

  const canSubmit = selectedSource && selectedDest && selectedSource.id !== selectedDest.id;

  return (
    <div className="glass-panel rounded-2xl p-5 animate-slide-left" style={{ width: '100%' }}>
      {/* Header */}
      <div className="flex items-center gap-3 mb-5">
        <div className="w-9 h-9 rounded-xl flex items-center justify-center"
          style={{ background: 'linear-gradient(135deg, #2563EB, #3B82F6)' }}>
          <Navigation size={18} color="white" />
        </div>
        <div>
          <h2 className="text-base font-semibold text-slate-900">Route Planner</h2>
          <p className="text-xs text-slate-500">Find your optimal journey</p>
        </div>
      </div>

      {/* Source Input */}
      <div className="mb-3 relative" ref={sourceRef}>
        <label className="block text-xs font-medium text-slate-500 mb-1.5 uppercase tracking-wider">
          From
        </label>
        <div className="relative">
          <Search size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
          <input
            type="text"
            className="input-field pl-10"
            placeholder="Search source station..."
            value={source}
            onChange={(e) => {
              setSource(e.target.value);
              setSelectedSource(null);
              setShowSourceDropdown(true);
            }}
            onFocus={() => setShowSourceDropdown(true)}
          />
        </div>
        {showSourceDropdown && sourceResults.length > 0 && (
          <div className="absolute z-50 w-full mt-1 glass-panel rounded-xl overflow-hidden max-h-48 overflow-y-auto">
            {sourceResults.map(station => (
              <button
                key={station.id}
                className="w-full text-left px-4 py-2.5 hover:bg-slate-100 transition-colors flex items-center gap-3 border-b border-slate-100 last:border-0"
                onClick={() => handleSelectSource(station)}
              >
                <span className={`w-2 h-2 rounded-full ${station.mode === 'metro' ? 'bg-indigo-500' : 'bg-orange-500'}`} />
                <div>
                  <div className="text-sm text-slate-700 font-medium">{station.name}</div>
                  <div className="text-xs text-slate-400">{station.id} • {station.mode}</div>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Destination Input */}
      <div className="mb-4 relative" ref={destRef}>
        <label className="block text-xs font-medium text-slate-500 mb-1.5 uppercase tracking-wider">
          To
        </label>
        <div className="relative">
          <Search size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
          <input
            type="text"
            className="input-field pl-10"
            placeholder="Search destination..."
            value={destination}
            onChange={(e) => {
              setDestination(e.target.value);
              setSelectedDest(null);
              setShowDestDropdown(true);
            }}
            onFocus={() => setShowDestDropdown(true)}
          />
        </div>
        {showDestDropdown && destResults.length > 0 && (
          <div className="absolute z-50 w-full mt-1 glass-panel rounded-xl overflow-hidden max-h-48 overflow-y-auto">
            {destResults.map(station => (
              <button
                key={station.id}
                className="w-full text-left px-4 py-2.5 hover:bg-slate-100 transition-colors flex items-center gap-3 border-b border-slate-100 last:border-0"
                onClick={() => handleSelectDest(station)}
              >
                <span className={`w-2 h-2 rounded-full ${station.mode === 'metro' ? 'bg-indigo-500' : 'bg-orange-500'}`} />
                <div>
                  <div className="text-sm text-slate-700 font-medium">{station.name}</div>
                  <div className="text-xs text-slate-400">{station.id} • {station.mode}</div>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Preference Selector */}
      <div className="mb-4">
        <label className="block text-xs font-medium text-slate-500 mb-2 uppercase tracking-wider">
          Optimize For
        </label>
        <div className="grid grid-cols-2 gap-2">
          {PREFERENCES.map(pref => {
            const Icon = pref.icon;
            const isActive = preference === pref.value;
            return (
              <button
                key={pref.value}
                onClick={() => setPreference(pref.value)}
                className={`flex items-center gap-2 px-3 py-2.5 rounded-xl text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 border border-blue-200'
                    : 'bg-slate-100 text-slate-500 border border-transparent hover:bg-slate-200 hover:text-slate-700'
                }`}
              >
                <Icon size={14} />
                <span>{pref.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col gap-2">
        <button
          className="btn-primary w-full flex items-center justify-center gap-2"
          onClick={handleFindRoute}
          disabled={!canSubmit || loading}
        >
          {loading ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <Navigation size={16} />
          )}
          {loading ? 'Computing...' : 'Find Route'}
        </button>

        <button
          className="btn-ghost w-full flex items-center justify-center gap-2"
          onClick={handleCompare}
          disabled={!canSubmit || loading}
        >
          <Shuffle size={14} />
          Compare Routes
        </button>
      </div>
    </div>
  );
}
