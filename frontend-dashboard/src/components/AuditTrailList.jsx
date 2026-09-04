import { formatDate } from '../utils/formatters';

export default function AuditTrailList({ entries }) {
  if (!entries || entries.length === 0) {
    return <p className="text-sm text-muted">No audit history yet.</p>;
  }

  return (
    <ol className="space-y-3">
      {entries.map((entry, i) => (
        <li key={i} className="flex gap-3 text-sm">
          <div className="flex flex-col items-center">
            <span className="mt-1.5 h-2 w-2 rounded-full bg-navy-600" />
            {i < entries.length - 1 && <span className="mt-1 w-px flex-1 bg-border" />}
          </div>
          <div className="pb-3">
            <p className="text-ink">{entry.action}</p>
            <p className="text-xs text-muted">{entry.actor} · {formatDate(entry.at)}</p>
          </div>
        </li>
      ))}
    </ol>
  );
}
