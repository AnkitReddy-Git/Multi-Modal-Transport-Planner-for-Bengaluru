/**
 * RouteComparison Component
 * Shows up to 3 alternative route cards for comparison.
 */
import { Clock, IndianRupee, Footprints, ArrowRightLeft, Award } from 'lucide-react';

export default function RouteComparison({ routes = [], selectedIndex = 0, onSelect }) {
  if (!routes || routes.length === 0) return null;

  // Find cheapest route for badge
  const minFare = Math.min(...routes.map(r => (r.total_fare || Infinity)));

  return (
    <div className="animate-fade-in">
      <div className="flex items-center gap-2 mb-3 px-1">
        <Award size={14} className="text-blue-600" />
        <h3 className="text-xs font-semibold text-slate-700 uppercase tracking-wider">Route Comparison</h3>
        <span className="text-xs text-slate-400">({routes.length} routes)</span>
      </div>
      <div className="flex gap-3 overflow-x-auto pb-2">
        {routes.map((r, idx) => {
          const rd = r;
          const isSelected = idx === selectedIndex;
          const isBest = idx === 0;
          const isCheapest = (rd.total_fare || 0) === minFare;
          return (
            <div
              key={idx}
              onClick={() => onSelect(idx)}
              className={`route-card flex-shrink-0 ${isSelected ? 'selected' : ''}`}
              style={{ minWidth: 200 }}
            >
              <div className="absolute top-2 right-2 flex gap-1">
                {isBest && (
                  <span className="bg-blue-50 text-blue-700 border border-blue-200 text-xs px-2 py-0.5 rounded-md font-medium">
                    Best
                  </span>
                )}
                {isCheapest && (
                  <span className="bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs px-2 py-0.5 rounded-md font-medium">
                    Cheapest
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-500 mb-2 capitalize font-medium">
                {rd.preference?.replace('_', ' ') || `Option ${idx + 1}`}
              </p>
              <div className="grid grid-cols-2 gap-y-2 gap-x-4">
                <Stat icon={Clock} label="Time" value={`${Math.round(rd.total_time || 0)} min`} />
                <Stat icon={IndianRupee} label="Fare" value={`₹${rd.total_fare || 0}`} color={isCheapest ? '#059669' : null} />
                <Stat icon={ArrowRightLeft} label="Transfers" value={rd.transfers ?? 0} />
                <Stat icon={Footprints} label="Walking" value={`${((rd.walking_distance || 0) * 1000).toFixed(0)}m`} />
              </div>
              {/* Mode sequence */}
              <div className="flex gap-2 mt-3 flex-wrap">
                {(rd.route || []).map((step, i) => (
                  <span key={i} className={`mode-badge ${step.mode}`} style={{ fontSize: 9, padding: '2px 6px' }}>
                    {step.mode === 'metro' ? '' : step.mode === 'bus' ? '' : step.mode === 'walking' ? '' : ''}
                  </span>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function Stat({ icon: Icon, label, value, color }) {
  return (
    <div className="flex items-center gap-2">
      <Icon size={11} className="text-slate-400" />
      <div>
        <p className="text-xs font-semibold leading-none" style={{ color: color || '#1e293b' }}>{value}</p>
        <p className="text-xs text-slate-400 leading-none mt-0.5">{label}</p>
      </div>
    </div>
  );
}
