/**
 * RouteDetails Component
 * Step-by-step journey breakdown with timeline visualization.
 */
import { Clock, IndianRupee, Footprints, ArrowRightLeft, MapPin, Train, Bus, PersonStanding } from 'lucide-react';

const MODE_ICONS = { metro: Train, bus: Bus, walking: PersonStanding, transfer: ArrowRightLeft };
const MODE_LABELS = { metro: 'Metro', bus: 'Bus', walking: 'Walk', transfer: 'Transfer' };

function SummaryCard({ icon: Icon, label, value, color }) {
  return (
    <div className="text-center p-2 rounded-xl bg-white border border-slate-100">
      <Icon size={14} className="mx-auto mb-1" style={{ color }} />
      <p className="text-sm font-semibold text-slate-800">{value}</p>
      <p className="text-xs text-slate-400">{label}</p>
    </div>
  );
}

export default function RouteDetails({ route, fareBreakdown }) {
  if (!route) return null;
  const rd = route.route || route;
  const steps = rd.route || [];
  const totalTime = rd.total_time || 0;
  const totalFare = rd.total_fare || 0;
  const transfers = rd.transfers || 0;
  const walkDist = rd.walking_distance || 0;

  return (
    <div className="glass-panel rounded-2xl p-5 animate-slide-right overflow-y-auto" style={{ maxHeight: 'calc(100vh - 200px)' }}>
      <div className="flex items-center gap-3 mb-4">
        <div className="w-8 h-8 rounded-lg flex items-center justify-center bg-blue-50">
          <MapPin size={16} className="text-blue-600" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-slate-900">Journey Details</h3>
          <p className="text-xs text-slate-500">Step-by-step breakdown</p>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-3 mb-5">
        <SummaryCard icon={Clock} label="Time" value={`${Math.round(totalTime)}m`} color="#2563EB" />
        <SummaryCard icon={IndianRupee} label="Fare" value={`₹${totalFare}`} color="#059669" />
        <SummaryCard icon={ArrowRightLeft} label="Xfers" value={transfers} color="#D97706" />
        <SummaryCard icon={Footprints} label="Walk" value={`${(walkDist * 1000).toFixed(0)}m`} color="#3B82F6" />
      </div>

      {fareBreakdown && fareBreakdown.breakdown && fareBreakdown.breakdown.length > 0 && (
        <div className="mb-5 p-3 rounded-xl bg-slate-50 border border-slate-100">
          <p className="text-xs font-medium text-slate-500 mb-2 uppercase tracking-wider">Fare Breakdown</p>
          <div className="space-y-2">
            {fareBreakdown.breakdown.map((seg, i) => {
              const SegIcon = MODE_ICONS[seg.mode] || MapPin;
              const isMetro = seg.mode === 'metro';
              const isBus = seg.mode === 'bus';
              const isPaid = seg.fare > 0;
              return (
                <div key={i} className="flex items-center justify-between text-xs py-1.5 border-b border-slate-100 last:border-0">
                  <div className="flex items-center gap-2">
                    <SegIcon size={12} className={isMetro ? 'text-purple-600' : isBus ? 'text-orange-600' : 'text-slate-400'} />
                    <span className="text-slate-600">
                      {seg.from_name} <span className="text-slate-300">→</span> {seg.to_name}
                    </span>
                    {isMetro && seg.stations > 0 && (
                      <span className="text-slate-400">({seg.stations} stn)</span>
                    )}
                    {isBus && seg.distance_km > 0 && (
                      <span className="text-slate-400">({seg.distance_km} km)</span>
                    )}
                  </div>
                  <span className={`font-semibold ${isPaid ? 'text-emerald-600' : 'text-slate-400'}`}>
                    {isPaid ? `₹${seg.fare}` : 'Free'}
                  </span>
                </div>
              );
            })}
          </div>
          <div className="mt-2 pt-2 border-t border-slate-200 flex items-center justify-between">
            <span className="text-xs font-medium text-slate-700">Total Fare</span>
            <span className="text-sm font-bold text-emerald-700">₹{fareBreakdown.total_fare}</span>
          </div>
        </div>
      )}

      <div className="space-y-0">
        {steps.map((step, idx) => {
          const Icon = MODE_ICONS[step.mode] || MapPin;
          return (
            <div key={idx} className="timeline-step animate-fade-in" style={{ animationDelay: `${idx * 80}ms` }}>
              <div className={`timeline-dot ${step.mode}`} />
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <span className={`mode-badge ${step.mode}`}>
                    <Icon size={12} />
                    <span>{MODE_LABELS[step.mode]}{step.line && ` • ${step.line}`}</span>
                  </span>
                  <p className="text-xs text-slate-700 font-medium mt-1.5">{step.from_name}</p>
                  <p className="text-xs text-slate-500 mt-0.5">→ {step.to_name}</p>
                </div>
                <div className="text-right ml-6">
                  <p className="text-xs font-medium text-slate-600">{step.time}m</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
