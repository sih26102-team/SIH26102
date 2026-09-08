import AppLayout from '../components/AppLayout';
import StatCard from '../components/StatCard';
import FilterBar from '../components/FilterBar';
import FlaggedWorksTable from '../components/FlaggedWorksTable';
import { useFlaggedWorks } from '../hooks/useFlaggedWorks';
import { formatINR } from '../utils/formatters';

export default function DashboardPage() {
  const { projects, filters, updateFilter, clearFilters, loading, error, stats, filterOptions } = useFlaggedWorks();

  return (
    <AppLayout
      title="Flagged Works"
      subtitle="Projects prioritized by risk score, most recent scoring run"
    >
      <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard label="Flagged projects" value={stats.total} />
        <StatCard label="High risk" value={stats.high} tone="high" hint="Prioritize for verification" />
        <StatCard label="Medium risk" value={stats.medium} tone="medium" hint="Routine review queue" />
        <StatCard label="Sanctioned (shown)" value={formatINR(stats.totalSanctioned)} />
      </div>

      <div className="mb-4">
        <FilterBar
          filters={filters}
          onChange={updateFilter}
          onClear={clearFilters}
          stateOptions={filterOptions.states}
          categoryOptions={filterOptions.categories}
          statusOptions={filterOptions.statuses}
        />
      </div>

      <FlaggedWorksTable projects={projects} loading={loading} error={error} />
    </AppLayout>
  );
}
