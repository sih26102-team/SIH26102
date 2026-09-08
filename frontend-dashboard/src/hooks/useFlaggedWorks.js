import { useEffect, useMemo, useState, useCallback } from 'react';
import { fetchFlaggedWorks, distinctValues } from '../services/worksService';

const EMPTY_FILTERS = { state: '', riskLevel: '', status: '', category: '', search: '' };

/**
 * Owns the flagged-works list + filter state so DashboardPage and
 * FlaggedWorksTable stay simple. Re-fetches whenever filters change.
 *
 * Filter dropdown options for real-world data fields (state, category,
 * status) must never be hardcoded lists - these describe facts about
 * actual MPLADS projects (which state, what kind of work, what stage),
 * not vocabulary our own system invents. A fixed list would silently
 * hide any project whose real value isn't on it. Risk level (HIGH/
 * MEDIUM/LOW) is the one exception, safely hardcoded in FilterBar,
 * because that label is assigned by our own risk-scoring engine, not
 * sourced from the raw project data.
 *
 * `filterOptions` is derived from an unfiltered fetch of the actual
 * data (real backend or mock), taken once on mount, not from the
 * currently-filtered `projects` (which would shrink the dropdowns as
 * the user filters).
 */
export function useFlaggedWorks() {
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const [projects, setProjects] = useState([]);
  const [allProjects, setAllProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async (activeFilters) => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchFlaggedWorks(activeFilters);
      setProjects(data);
    } catch (err) {
      setError(err.message || 'Could not load flagged works');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load(filters);
  }, [filters, load]);

  // One unfiltered fetch, only on mount, purely to populate filter
  // dropdown options - never re-run when `filters` changes.
  useEffect(() => {
    fetchFlaggedWorks({})
      .then(setAllProjects)
      .catch(() => setAllProjects([]));
  }, []);

  const filterOptions = useMemo(
    () => ({
      states: distinctValues(allProjects, 'state'),
      categories: distinctValues(allProjects, 'category'),
      statuses: distinctValues(allProjects, 'status'),
    }),
    [allProjects]
  );

  const updateFilter = useCallback((key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  }, []);

  const clearFilters = useCallback(() => setFilters(EMPTY_FILTERS), []);

  const stats = useMemo(() => {
    const high = projects.filter((p) => p.riskLevel === 'HIGH').length;
    const medium = projects.filter((p) => p.riskLevel === 'MEDIUM').length;
    const totalSanctioned = projects.reduce((sum, p) => sum + p.sanctionedAmount, 0);
    return { total: projects.length, high, medium, totalSanctioned };
  }, [projects]);

  return {
    projects,
    filters,
    updateFilter,
    clearFilters,
    loading,
    error,
    stats,
    filterOptions,
    refetch: () => load(filters),
  };
}
