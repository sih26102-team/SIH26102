export default function EmptyState({ title, description, tone = 'neutral' }) {
  const toneClasses = tone === 'error' ? 'text-risk-high' : 'text-muted';
  return (
    <div className="flex flex-col items-center justify-center gap-1 rounded-lg border border-dashed border-border py-14 text-center">
      <p className={`font-display text-base font-semibold ${toneClasses}`}>{title}</p>
      {description && <p className="max-w-sm text-sm text-muted">{description}</p>}
    </div>
  );
}
