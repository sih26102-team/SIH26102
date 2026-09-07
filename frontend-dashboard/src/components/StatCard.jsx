export default function StatCard({ label, value, tone = 'default', hint }) {
  const toneClasses = {
    default: 'text-ink',
    high: 'text-risk-high',
    medium: 'text-risk-medium',
    low: 'text-risk-low',
  };

  return (
    <div className="rounded-lg border border-border bg-surface p-3 shadow-card sm:p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-muted">{label}</p>
      <p className={`mt-1 whitespace-nowrap font-display text-base font-semibold sm:text-2xl ${toneClasses[tone]}`}>{value}</p>
      {hint && <p className="mt-1 text-xs text-muted">{hint}</p>}
    </div>
  );
}
