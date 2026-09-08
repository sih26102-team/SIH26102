import { api, USE_MOCK, mockDelay } from './api';
import { MOCK_PROJECTS, buildMockTrend } from '../utils/mockData';

/**
 * Expected real contract (from backend-data-api/app/routes/works.py):
 *   GET /works                 -> paginated flagged/scored project list
 *   GET /works/:projectId      -> single project + risk breakdown
 *   GET /analytics/trend       -> monthly flagged/high-risk counts
 *
 * Query params mirror the filters the FilterBar component exposes:
 * state, district, riskLevel, status, category, search.
 */

function applyFilters(projects, filters = {}) {
  return projects.filter((p) => {
    if (filters.state && p.state !== filters.state) return false;
    if (filters.riskLevel && p.riskLevel !== filters.riskLevel) return false;
    if (filters.status && p.status !== filters.status) return false;
    if (filters.category && p.category !== filters.category) return false;
    if (filters.search) {
      const q = filters.search.toLowerCase();
      const haystack = `${p.projectId} ${p.constituency} ${p.district} ${p.implementingAgency}`.toLowerCase();
      if (!haystack.includes(q)) return false;
    }
    return true;
  });
}

export async function fetchFlaggedWorks(filters = {}) {
  if (USE_MOCK) {
    await mockDelay();
    const filtered = applyFilters(MOCK_PROJECTS, filters)
      .slice()
      .sort((a, b) => b.riskScore - a.riskScore);
    return filtered;
  }

  const { data } = await api.get('/works', { params: filters });
  return data;
}

export async function fetchProjectById(projectId) {
  if (USE_MOCK) {
    await mockDelay(250);
    const project = MOCK_PROJECTS.find((p) => p.projectId === projectId);
    if (!project) {
      const err = new Error(`Project ${projectId} not found`);
      err.code = 'NOT_FOUND';
      throw err;
    }
    return project;
  }

  const { data } = await api.get(`/works/${projectId}`);
  return data;
}

export async function fetchTrend() {
  if (USE_MOCK) {
    await mockDelay(250);
    return buildMockTrend();
  }
  const { data } = await api.get('/analytics/trend');
  return data;
}

export function distinctValues(projects, key) {
  return Array.from(new Set(projects.map((p) => p[key]))).sort();
}
