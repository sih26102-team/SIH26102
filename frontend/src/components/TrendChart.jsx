import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import EmptyState from './EmptyState';

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded border border-border bg-white px-3 py-2 text-xs shadow-card">
      <p className="mb-1 font-semibold text-ink">{label}</p>
      {payload.map((entry) => (
        <p key={entry.dataKey} style={{ color: entry.color }}>
          {entry.name}: {entry.value}
        </p>
      ))}
    </div>
  );
}

export default function TrendChart({ data, loading }) {
  if (loading) {
    return <EmptyState title="Loading trend…" description="Aggregating monthly flag counts." />;
  }
  if (!data || data.length === 0) {
    return <EmptyState title="No trend data yet" description="Trend data appears once projects have been scored across multiple months." />;
  }

  return (
    <div className="rounded-lg border border-border bg-surface p-4 shadow-card">
      <div className="mb-3">
        <h3 className="font-display text-base font-semibold text-ink">Flagged projects over time</h3>
        <p className="text-xs text-muted">Total flagged vs. high-risk, last 9 months</p>
      </div>
      <ResponsiveContainer width="100%" height={260}>
        <AreaChart data={data} margin={{ top: 5, right: 12, left: -12, bottom: 0 }}>
          <defs>
            <linearGradient id="flaggedFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#1F3A5F" stopOpacity={0.25} />
              <stop offset="95%" stopColor="#1F3A5F" stopOpacity={0.02} />
            </linearGradient>
            <linearGradient id="highRiskFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#C0392B" stopOpacity={0.35} />
              <stop offset="95%" stopColor="#C0392B" stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#E2E6EA" vertical={false} />
          <XAxis dataKey="month" tick={{ fontSize: 12, fill: '#5B6672' }} axisLine={{ stroke: '#E2E6EA' }} tickLine={false} />
          <YAxis tick={{ fontSize: 12, fill: '#5B6672' }} axisLine={false} tickLine={false} />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Area
            type="monotone"
            dataKey="flagged"
            name="Total flagged"
            stroke="#1F3A5F"
            strokeWidth={2}
            fill="url(#flaggedFill)"
          />
          <Area
            type="monotone"
            dataKey="highRisk"
            name="High risk"
            stroke="#C0392B"
            strokeWidth={2}
            fill="url(#highRiskFill)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
// TrendChart.jsx — owner: Chandana
