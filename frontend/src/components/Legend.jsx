/**
 * Legend Component - Transport mode color legend
 */
import { Train, Bus, PersonStanding, ArrowRightLeft } from 'lucide-react';

const MODES = [
  { label: 'Metro', color: '#7C3AED', icon: Train },
  { label: 'Bus', color: '#EA580C', icon: Bus },
  { label: 'Walking', color: '#059669', icon: PersonStanding },
  { label: 'Transfer', color: '#D97706', icon: ArrowRightLeft },
];

export default function Legend() {
  return (
    <div className="glass-panel rounded-xl px-5 py-3 flex items-center gap-8">
      {MODES.map(m => {
        const Icon = m.icon;
        return (
          <div key={m.label} className="flex items-center gap-3">
            <span className="w-3 h-3 rounded-full" style={{ background: m.color }} />
            <Icon size={12} style={{ color: m.color }} />
            <span className="text-xs text-slate-500 font-medium">{m.label}</span>
          </div>
        );
      })}
    </div>
  );
}
