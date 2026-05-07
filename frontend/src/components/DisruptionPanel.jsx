/**
 * DisruptionPanel Component
 * Route Disruption Simulator - allows closing stations, disabling edges, adding delays.
 */
import { useState } from 'react';
import { AlertTriangle, X, RotateCcw, Plus, Loader2 } from 'lucide-react';

export default function DisruptionPanel({ stations = [], disruptions = [], onCreate, onDelete, onReset, loading }) {
  const [type, setType] = useState('station_closed');
  const [node, setNode] = useState('');
  const [edgeFrom, setEdgeFrom] = useState('');
  const [edgeTo, setEdgeTo] = useState('');
  const [delay, setDelay] = useState(10);
  const [desc, setDesc] = useState('');

  const handleCreate = () => {
    const data = { type, description: desc || `${type} simulation` };
    if (type === 'station_closed') {
      data.affected_node = node;
    } else if (type === 'edge_disabled') {
      data.affected_edge_from = edgeFrom;
      data.affected_edge_to = edgeTo;
    } else if (type === 'delay') {
      data.affected_node = node || undefined;
      data.affected_edge_from = !node ? edgeFrom : undefined;
      data.affected_edge_to = !node ? edgeTo : undefined;
      data.delay_minutes = delay;
    }
    onCreate(data);
    setDesc('');
  };

  return (
    <div className="glass-panel rounded-2xl p-5 animate-fade-in">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <AlertTriangle size={16} className="text-amber-500" />
          <h3 className="text-sm font-semibold text-slate-900">Disruption Simulator</h3>
        </div>
        {disruptions.length > 0 && (
          <button onClick={onReset} className="btn-ghost text-xs flex items-center gap-1 py-1 px-2">
            <RotateCcw size={11} /> Reset
          </button>
        )}
      </div>

      {/* Type selector */}
      <select className="input-field mb-3 text-sm" value={type} onChange={e => setType(e.target.value)}>
        <option value="station_closed">🚫 Close Station</option>
        <option value="edge_disabled">❌ Disable Edge</option>
        <option value="delay">⏱️ Add Delay</option>
      </select>

      {/* Node selector for station_closed and delay */}
      {(type === 'station_closed' || type === 'delay') && (
        <select className="input-field mb-3 text-sm" value={node} onChange={e => setNode(e.target.value)}>
          <option value="">Select station...</option>
          {stations.map(s => (
            <option key={s.id} value={s.id}>{s.name} ({s.id})</option>
          ))}
        </select>
      )}

      {/* Edge selectors */}
      {(type === 'edge_disabled' || (type === 'delay' && !node)) && (
        <div className="flex gap-2 mb-3">
          <select className="input-field text-sm flex-1" value={edgeFrom} onChange={e => setEdgeFrom(e.target.value)}>
            <option value="">From...</option>
            {stations.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
          <select className="input-field text-sm flex-1" value={edgeTo} onChange={e => setEdgeTo(e.target.value)}>
            <option value="">To...</option>
            {stations.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
        </div>
      )}

      {/* Delay slider */}
      {type === 'delay' && (
        <div className="mb-3">
          <label className="text-xs text-slate-500 mb-1 block">Delay: {delay} min</label>
          <input type="range" min="5" max="30" value={delay} onChange={e => setDelay(Number(e.target.value))}
            className="w-full accent-blue-600" />
        </div>
      )}

      <input className="input-field mb-3 text-sm" placeholder="Description (optional)" value={desc}
        onChange={e => setDesc(e.target.value)} />

      <button onClick={handleCreate} disabled={loading} className="btn-danger w-full flex items-center justify-center gap-2">
        {loading ? <Loader2 size={14} className="animate-spin" /> : <Plus size={14} />}
        Simulate Disruption
      </button>

      {/* Active disruptions list */}
      {disruptions.length > 0 && (
        <div className="mt-4 space-y-2">
          <p className="text-xs font-medium text-amber-700 uppercase tracking-wider">Active ({disruptions.length})</p>
          {disruptions.map(d => (
            <div key={d.id} className="flex items-center justify-between p-2 rounded-lg bg-red-50 border border-red-200">
              <div>
                <p className="text-xs text-slate-800 font-medium">{d.description || d.type}</p>
                <p className="text-xs text-red-600/60">
                  {d.affected_node || `${d.affected_edge_from} → ${d.affected_edge_to}`}
                  {d.delay_minutes > 0 && ` (+${d.delay_minutes}min)`}
                </p>
              </div>
              <button onClick={() => onDelete(d.id)} className="text-red-500/60 hover:text-red-600 transition-colors">
                <X size={14} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
