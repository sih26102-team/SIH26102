import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import RiskScoreRing from './RiskScoreRing';
import DataQualityBadge from './DataQualityBadge';
import EmptyState from './EmptyState';
import { formatINR, formatDate, formatDelay } from '../utils/formatters';

const COLUMNS = [
  { key: 'riskScore', label: 'Risk' },
  { key: 'projectId', label: 'Project' },
  { key: 'location', label: 'Location' },
  { key: 'category', label: 'Category' },
  { key: 'sanctionedAmount', label: 'Sanctioned' },
  { key: 'utilizationPct', label: 'Utilization' },
  { key: 'progressPct', label: 'Progress' },
  { key: 'delayDays', label: 'Timeline' },
  { key: 'status', label: 'Status' },
];

/**
 * This table is the investigator's main triage view - it exists to answer
 * "what should I look at first", so it sorts by risk score by default and
 * every row leads to the full explanation on ProjectDetailPage. It never
 * claims a row is confirmed fraud; it shows a score and a status, same
 * vocabulary the context briefing insists on throughout (Section 2).
 */
export default function FlaggedWorksTable({ projects, loading, error }) {
  const navigate = useNavigate();
  const [sortKey, setSortKey] = useState('riskScore');
  const [sortDir, setSortDir] = useState('desc');

  const sorted = useMemo(() => {
    const copy = [...projects];
    copy.sort((a, b) => {
      const av = a[sortKey];
      const bv = b[sortKey];
      if (typeof av === 'string') {
        return sortDir === 'asc' ? av.localeCompare(bv) : bv.localeCompare(av);
      }
      return sortDir === 'asc' ? av - bv : bv - av;
    });
    return copy;
  }, [projects, sortKey, sortDir]);

  function toggleSort(key) {
    if (key === sortKey) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDir('desc');
    }
  }

  if (loading) {
    return <EmptyState title="Loading flagged works…" description="Fetching the latest scored projects." />;
  }
  if (error) {
    return <EmptyState tone="error" title="Couldn't load flagged works" description={error} />;
  }
  if (sorted.length === 0) {
    return (
      <EmptyState
        title="No projects match these filters"
        description="Try clearing a filter, or widen the risk level range."
      />
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-border bg-surface shadow-card">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[880px] border-collapse text-sm">
          <thead>
            <tr className="border-b border-border bg-navy-50 text-left">
              {COLUMNS.map((col) => (
                <th key={col.key} className="px-4 py-3">
                  <button
                    type="button"
                    onClick={() => (col.key === 'location' ? null : toggleSort(col.key))}
                    className="flex items-center gap-1 text-xs font-semibold uppercase tracking-wide text-navy-700"
                  >
                    {col.label}
                    {sortKey === col.key && (
                      <span className="text-navy-400">{sortDir === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </button>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sorted.map((p) => (
              <tr
                key={p.projectId}
                onClick={() => navigate(`/projects/${p.projectId}`)}
                className="cursor-pointer border-b border-border last:border-0 hover:bg-navy-50/60"
              >
                <td className="px-4 py-3">
                  <RiskScoreRing score={p.riskScore} level={p.riskLevel} size={40} strokeWidth={4} showLabel={false} />
                </td>
                <td className="px-4 py-3">
                  <div className="font-mono text-xs font-medium text-ink">{p.projectId}</div>
                  <div className="mt-0.5 text-xs text-muted">{p.implementingAgency}</div>
                </td>
                <td className="px-4 py-3">
                  <div className="text-ink">{p.district}</div>
                  <div className="text-xs text-muted">{p.state}</div>
                </td>
                <td className="px-4 py-3 text-ink">{p.category}</td>
                <td className="px-4 py-3 font-mono text-ink">{formatINR(p.sanctionedAmount)}</td>
                <td className="px-4 py-3 text-ink">{p.utilizationPct}%</td>
                <td className="px-4 py-3 text-ink">{p.progressPct}%</td>
                <td className="px-4 py-3">
                  <span className={p.delayDays > 0 ? 'text-risk-medium' : 'text-risk-low'}>
                    {formatDelay(p.delayDays)}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex flex-col gap-1">
                    <span className="text-ink">{p.status}</span>
                    <DataQualityBadge dataQuality={p.dataQuality} />
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="border-t border-border bg-navy-50/50 px-4 py-2 text-xs text-muted">
        Showing {sorted.length} flagged project{sorted.length !== 1 ? 's' : ''} · Sanctioned as of{' '}
        {formatDate(new Date().toISOString())}
      </div>
    </div>
  );
}
// FlaggedWorksTable.jsx — owner: Chandana
