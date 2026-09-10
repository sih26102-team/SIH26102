import { api, USE_MOCK, mockDelay } from './api';
import PIPELINE_PROJECTS from '../data/pipeline_projects.json';

function buildPipelineTrend(projects) {
  const months = [
    'Dec 25', 'Jan 26', 'Feb 26', 'Mar 26', 'Apr 26',
    'May 26', 'Jun 26', 'Jul 26', 'Aug 26',
  ];
  const totalHigh = projects.filter(p => p.riskLevel === 'HIGH').length;
  const totalFlagged = projects.filter(p => p.riskScore >= 40).length;

  return months.map((month, i) => {
    const factor = 0.65 + (i * 0.045);
    const flagged = Math.round(totalFlagged * factor);
    const high = Math.round(totalHigh * factor);
    return {
      month,
      totalFlagged: flagged,
      highRisk: high,
    };
  });
}

function applyFilters(projects, filters = {}) {
  return projects.filter((p) => {
    if (filters.state && p.state !== filters.state) return false;
    if (filters.riskLevel && p.riskLevel !== filters.riskLevel) return false;
    if (filters.status && p.status !== filters.status) return false;
    if (filters.category && p.category !== filters.category) return false;
    if (filters.search) {
      const q = filters.search.toLowerCase();
      const haystack = `${p.projectId} ${p.constituency} ${p.district} ${p.implementingAgency} ${p.category}`.toLowerCase();
      if (!haystack.includes(q)) return false;
    }
    return true;
  });
}

export async function fetchFlaggedWorks(filters = {}) {
  if (USE_MOCK) {
    await mockDelay(150);
    return applyFilters(PIPELINE_PROJECTS, filters)
      .slice()
      .sort((a, b) => b.riskScore - a.riskScore);
  }

  try {
    const { data } = await api.get('/works', { params: filters });
    if (Array.isArray(data) && data.length > 0) {
      return data.map((item) => {
        const id = item.projectId || item.project_id || (item.work_id ? `WRK-${item.work_id}` : 'PRJ-UNKNOWN');
        return {
          ...item,
          id,
          projectId: id,
          sanctionedAmount: item.sanctionedAmount ?? item.sanctioned_amount ?? item.recommended_amount ?? 1000000,
          expenditure: item.expenditure ?? 0,
          riskScore: item.riskScore ?? item.risk_score ?? 60,
          riskLevel: item.riskLevel ?? item.risk_level ?? 'MEDIUM',
          progressPct: item.progressPct ?? item.progress_percent ?? 25,
          utilizationPct: item.utilizationPct ?? 35,
          category: item.category || 'Civil Work',
          status: item.status || 'ongoing',
          constituency: item.constituency || 'General Constituency',
          state: item.state || 'National',
        };
      });
    }
    return applyFilters(PIPELINE_PROJECTS, filters).slice().sort((a, b) => b.riskScore - a.riskScore);
  } catch (err) {
    console.warn('Backend /works API unavailable; loading data-pipeline dataset:', err.message);
    await mockDelay(100);
    return applyFilters(PIPELINE_PROJECTS, filters).slice().sort((a, b) => b.riskScore - a.riskScore);
  }
}

export async function fetchProjectById(projectId) {
  if (USE_MOCK) {
    await mockDelay(150);
    const project = PIPELINE_PROJECTS.find((p) => p.projectId === projectId || p.id === projectId);
    if (!project) {
      const fallback = PIPELINE_PROJECTS[0];
      return { ...fallback, projectId, id: projectId };
    }
    return project;
  }

  try {
    const { data } = await api.get(`/works/${projectId}`);
    return data;
  } catch (err) {
    console.warn(`Backend /works/${projectId} API unavailable; loading from data-pipeline:`, err.message);
    await mockDelay(100);
    const project = PIPELINE_PROJECTS.find((p) => p.projectId === projectId || p.id === projectId);
    if (!project) {
      const fallback = PIPELINE_PROJECTS[0];
      return { ...fallback, projectId, id: projectId };
    }
    return project;
  }
}

export async function fetchTrend() {
  if (USE_MOCK) {
    await mockDelay(150);
    return buildPipelineTrend(PIPELINE_PROJECTS);
  }

  try {
    const { data } = await api.get('/analytics/trend');
    return data;
  } catch (err) {
    console.warn('Backend /analytics/trend API unavailable; generating trend from data-pipeline:', err.message);
    await mockDelay(100);
    return buildPipelineTrend(PIPELINE_PROJECTS);
  }
}

export function distinctValues(projects, key) {
  return Array.from(new Set(projects.map((p) => p[key]))).filter(Boolean).sort();
}
