/**
 * StatsBar Component - Network statistics bar
 */
import { Train, Bus, GitBranch, AlertTriangle, Activity } from 'lucide-react';

export default function StatsBar({ stats, disruptionCount = 0 }) {
  if (!stats) return null;
  return (
    <div className="glass-panel rounded-xl px-5 py-2.5 flex items-center gap-10">
      <StatItem icon={Train} label="Metro" value={stats.metro_stations} color="#7C3AED" />
      <StatItem icon={Bus} label="Bus Stops" value={stats.bus_stops} color="#EA580C" />
      <StatItem icon={GitBranch} label="Edges" value={stats.total_edges} color="#2563EB" />
      <StatItem icon={AlertTriangle} label="Disruptions" value={disruptionCount}
        color={disruptionCount > 0 ? '#D97706' : '#059669'} />
      <div className="flex items-center gap-3 ml-auto">
        <Activity size={12} className="text-emerald-600" />
        <span className="text-xs text-emerald-600 font-medium">Network Active</span>
      </div>
    </div>
  );
}

function StatItem({ icon: Icon, label, value, color }) {
  return (
    <div className="flex items-center gap-3">
      <Icon size={13} style={{ color }} />
      <span className="text-xs text-slate-500 font-medium">{label}:</span>
      <span className="text-xs font-semibold" style={{ color }}>{value}</span>
    </div>
  );
}
