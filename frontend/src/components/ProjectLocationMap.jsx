import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import { riskColorClasses } from '../utils/riskUtils';
import { formatINR } from '../utils/formatters';
import EmptyState from './EmptyState';

export default function ProjectLocationMap({ project }) {
  if (!project?.lat || !project?.lng) {
    return (
      <EmptyState
        title="No location on file"
        description="This record doesn't have coordinates to plot."
      />
    );
  }

  const { ring } = riskColorClasses(project.riskLevel);
  const position = [project.lat, project.lng];

  return (
    <div className="overflow-hidden rounded-lg border border-border bg-surface shadow-card">
      <div className="border-b border-border px-4 py-3">
        <h3 className="font-display text-base font-semibold text-ink">Project location</h3>
        <p className="text-xs text-muted">{project.constituency}, {project.district}, {project.state}</p>
      </div>
      <MapContainer center={position} zoom={11} scrollWheelZoom={false} style={{ height: '280px', width: '100%' }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <CircleMarker
          center={position}
          radius={10 + project.riskScore / 12}
          pathOptions={{ color: ring, fillColor: ring, fillOpacity: 0.55, weight: 2 }}
        >
          <Popup>
            <div className="text-xs">
              <p className="font-mono font-semibold">{project.projectId}</p>
              <p>{project.district}, {project.state}</p>
              <p>Risk score: {project.riskScore} ({project.riskLevel})</p>
              <p>Sanctioned: {formatINR(project.sanctionedAmount)}</p>
            </div>
          </Popup>
        </CircleMarker>
      </MapContainer>
    </div>
  );
}
