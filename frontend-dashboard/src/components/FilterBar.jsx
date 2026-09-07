const RISK_LEVELS = ['HIGH', 'MEDIUM', 'LOW'];

function Select({ label, value, onChange, options }) {
  return (
    <label className="flex flex-col gap-1 text-xs font-medium text-muted">
      {label}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="rounded border border-border bg-white px-2.5 py-1.5 text-sm text-ink outline-none focus:border-navy-600"
      >
        <option value="">All</option>
        {options.map((opt) => (
          <option key={opt} value={opt}>{opt}</option>
        ))}
      </select>
    </label>
  );
}

export default function FilterBar({
  filters,
  onChange,
  onClear,
  stateOptions = [],
  categoryOptions = [],
  statusOptions = [],
}) {
  const hasActiveFilters = Object.values(filters).some(Boolean);

  return (
    <div className="flex flex-wrap items-end gap-3 rounded-lg border border-border bg-surface p-4 shadow-card">
      <label className="flex min-w-[220px] flex-1 flex-col gap-1 text-xs font-medium text-muted">
        Search
        <input
          type="text"
          value={filters.search}
          onChange={(e) => onChange('search', e.target.value)}
          placeholder="Project ID, district, agency…"
          className="rounded border border-border bg-white px-2.5 py-1.5 text-sm text-ink outline-none focus:border-navy-600"
        />
      </label>

      <Select label="State" value={filters.state} onChange={(v) => onChange('state', v)} options={stateOptions} />
      <Select label="Risk level" value={filters.riskLevel} onChange={(v) => onChange('riskLevel', v)} options={RISK_LEVELS} />
      <Select label="Status" value={filters.status} onChange={(v) => onChange('status', v)} options={statusOptions} />
      <Select label="Category" value={filters.category} onChange={(v) => onChange('category', v)} options={categoryOptions} />

      {hasActiveFilters && (
        <button
          type="button"
          onClick={onClear}
          className="rounded px-3 py-1.5 text-xs font-semibold text-navy-600 underline-offset-2 hover:underline"
        >
          Clear filters
        </button>
      )}
    </div>
  );
}
