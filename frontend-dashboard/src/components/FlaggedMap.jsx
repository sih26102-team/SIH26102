import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import { useNavigate } from 'react-router-dom';
import { riskColorClasses } from '../utils/riskUtils';
import { formatINR } from '../utils/formatters';
import EmptyState from './EmptyState';

const INDIA_CENTER = [22.9734, 78.6569];

export default function FlaggedMap({ projects, loading }) {
  const navigate = useNavigate();

  if (loading) {
    return <EmptyState title="Loading map…" description="Plotting flagged project locations." />;
  }
  if (!projects || projects.length === 0) {
    return <EmptyState title="Nothing to plot" description="No flagged projects match the current filters." />;
  }

  return (
    <div className="overflow-hidden rounded-lg border border-border bg-surface shadow-card">
      <div className="border-b border-border px-4 py-3">
        <h3 className="font-display text-base font-semibold text-ink">Geographic distribution</h3>
        <p className="text-xs text-muted">Marker size and color reflect risk score - illustrative district-level positions</p>
      </div>
      <MapContainer center={INDIA_CENTER} zoom={5} scrollWheelZoom={false} style={{ height: '420px', width: '100%' }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {projects.map((p) => {
          const { ring } = riskColorClasses(p.riskLevel);
          const radius = 5 + p.riskScore / 12;
          return (
            <CircleMarker
              key={p.projectId}
              center={[p.lat, p.lng]}
              radius={radius}
              pathOptions={{ color: ring, fillColor: ring, fillOpacity: 0.55, weight: 1.5 }}
              eventHandlers={{ click: () => navigate(`/projects/${p.projectId}`) }}
            >
              <Popup>
                <div className="text-xs">
                  <p className="font-mono font-semibold">{p.projectId}</p>
                  <p>{p.district}, {p.state}</p>
                  <p>Risk score: {p.riskScore} ({p.riskLevel})</p>
                  <p>Sanctioned: {formatINR(p.sanctionedAmount)}</p>
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>
    </div>
  );
}

