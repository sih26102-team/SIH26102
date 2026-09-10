import { api, USE_MOCK, mockDelay } from './api';
import { MOCK_CASES } from '../utils/mockData';

let mockCaseStore = null;
function getStore() {
  if (!mockCaseStore) {
    mockCaseStore = MOCK_CASES.map((c, i) => ({
      id: i + 1,
      caseId: c.caseId || `CASE-${2026000 + i}`,
      title: `Anomaly Investigation for ${c.projectId}`,
      flagged_work_id: c.projectId,
      projectId: c.projectId,
      status: c.status?.toUpperCase().replace(/ /g, '_') || 'REQUESTED',
      risk_score: 87.0,
      risk_level: 'HIGH',
      flagged_reasons: 'High burn rate and expenditure mismatch observed; field inspection required.',
      assigned_to_id: 2,
      assignedTo: c.assignedTo || 'Senior Field Investigator',
      evidence_photo_url: null,
      latitude: null,
      longitude: null,
      location_timestamp: null,
      site_condition: null,
      financial_observation: null,
      investigator_recommendation: null,
      investigator_notes: null,
      resolution: null,
      resolution_notes: null,
      audit_logs: c.auditTrail?.map((a, idx) => ({
        id: idx + 1,
        case_id: i + 1,
        action: a.action,
        details: a.action,
        timestamp: a.at ? new Date(a.at).toISOString() : new Date().toISOString()
      })) || []
    }));
  }
  return mockCaseStore;
}

export async function fetchCases(params = {}) {
  if (USE_MOCK) {
    await mockDelay();
    return getStore();
  }
  try {
    const { data } = await api.get('/cases/', { params });
    return data.map((c) => ({
      ...c,
      caseId: `CASE-${c.id}`,
      projectId: c.flagged_work_id,
      assignedTo: c.assigned_officer?.full_name || c.assigned_officer?.username || 'Unassigned',
      auditTrail: c.audit_logs?.map((a) => ({
        at: a.timestamp?.slice(0, 10),
        actor: a.performed_by_id ? `User #${a.performed_by_id}` : 'System',
        action: `${a.action}: ${a.details || ''}`
      })) || []
    }));
  } catch (err) {
    console.warn('API /cases fetch failed, falling back to local store:', err.message);
    return getStore();
  }
}

export async function fetchCaseAudit(caseId) {
  if (USE_MOCK) {
    await mockDelay(200);
    const store = getStore();
    const found = store.find((c) => c.id === Number(caseId) || c.caseId === caseId);
    return found?.audit_logs || [];
  }
  const cleanId = String(caseId).replace('CASE-', '');
  const { data } = await api.get(`/cases/${cleanId}/audit`);
  return data;
}

export async function requestInvestigation(payload) {
  if (USE_MOCK) {
    await mockDelay(300);
    const store = getStore();
    const newCase = {
      id: store.length + 1,
      caseId: `CASE-${2026000 + store.length + 1}`,
      title: payload.title || `Investigation for ${payload.flagged_work_id}`,
      flagged_work_id: payload.flagged_work_id,
      projectId: payload.flagged_work_id,
      status: 'REQUESTED',
      risk_score: payload.risk_score || 85.0,
      risk_level: payload.risk_level || 'HIGH',
      flagged_reasons: payload.flagged_reasons,
      request_reason: payload.request_reason,
      assignedTo: 'Unassigned (Pending Approval)',
      audit_logs: [
        {
          id: 1,
          action: 'INVESTIGATION_REQUESTED',
          details: payload.request_reason,
          timestamp: new Date().toISOString()
        }
      ]
    };
    store.unshift(newCase);
    return newCase;
  }

  const { data } = await api.post('/cases/request', payload);
  return data;
}

export async function adminDirectAssign(payload) {
  if (USE_MOCK) {
    await mockDelay(300);
    const store = getStore();
    const newCase = {
      id: store.length + 1,
      caseId: `CASE-${2026000 + store.length + 1}`,
      title: payload.title || `Direct Assignment for ${payload.flagged_work_id}`,
      flagged_work_id: payload.flagged_work_id,
      projectId: payload.flagged_work_id,
      status: 'ASSIGNED',
      risk_score: payload.risk_score || 85.0,
      risk_level: payload.risk_level || 'HIGH',
      flagged_reasons: payload.flagged_reasons,
      assigned_to_id: payload.investigator_id,
      assignedTo: `Investigator #${payload.investigator_id}`,
      audit_logs: [
        {
          id: 1,
          action: 'ADMIN_DIRECT_ASSIGNMENT',
          details: 'Directly assigned by Administrator',
          timestamp: new Date().toISOString()
        }
      ]
    };
    store.unshift(newCase);
    return newCase;
  }

  const { data } = await api.post('/cases/assign', payload);
  return data;
}

export async function approveCase(caseId, payload = {}) {
  const cleanId = String(caseId).replace('CASE-', '');
  if (USE_MOCK) {
    await mockDelay(300);
    const store = getStore();
    const found = store.find((c) => c.id === Number(cleanId) || c.caseId === caseId);
    if (found) {
      found.status = 'ASSIGNED';
      found.assignedTo = 'Senior Field Investigator';
    }
    return found;
  }
  const { data } = await api.post(`/cases/${cleanId}/approve`, payload);
  return data;
}

export async function rejectCase(caseId, payload) {
  const cleanId = String(caseId).replace('CASE-', '');
  if (USE_MOCK) {
    await mockDelay(300);
    const store = getStore();
    const found = store.find((c) => c.id === Number(cleanId) || c.caseId === caseId);
    if (found) {
      found.status = 'REJECTED';
      found.resolution_notes = payload.rejection_reason;
    }
    return found;
  }
  const { data } = await api.post(`/cases/${cleanId}/reject`, payload);
  return data;
}

export async function submitEvidence(caseId, payload) {
  const cleanId = String(caseId).replace('CASE-', '');
  if (USE_MOCK) {
    await mockDelay(400);
    const store = getStore();
    const found = store.find((c) => c.id === Number(cleanId) || c.caseId === caseId);
    if (found) {
      found.status = 'EVIDENCE_SUBMITTED';
      Object.assign(found, payload);
    }
    return found;
  }
  const { data } = await api.post(`/cases/${cleanId}/evidence`, payload);
  return data;
}

export async function resolveCase(caseId, payload) {
  const cleanId = String(caseId).replace('CASE-', '');
  if (USE_MOCK) {
    await mockDelay(300);
    const store = getStore();
    const found = store.find((c) => c.id === Number(cleanId) || c.caseId === caseId);
    if (found) {
      found.status = payload.resolution;
      found.resolution = payload.resolution;
      found.resolution_notes = payload.resolution_notes;
    }
    return found;
  }
  const { data } = await api.post(`/cases/${cleanId}/resolve`, payload);
  return data;
}
