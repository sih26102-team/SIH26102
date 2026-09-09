import { api, USE_MOCK, mockDelay } from './api';
import { MOCK_CASES } from '../utils/mockData';

let mockCaseStore = null;
function getStore() {
  if (!mockCaseStore) mockCaseStore = MOCK_CASES.map((c) => ({ ...c }));
  return mockCaseStore;
}

export async function fetchCases() {
  if (USE_MOCK) {
    await mockDelay();
    return getStore();
  }
  const { data } = await api.get('/cases');
  return data;
}

export async function updateCaseStatus(caseId, status, actor = 'Current Reviewer') {
  if (USE_MOCK) {
    await mockDelay(300);
    const store = getStore();
    const caseRecord = store.find((c) => c.caseId === caseId);
    if (!caseRecord) {
      const err = new Error(`Case ${caseId} not found`);
      err.code = 'NOT_FOUND';
      throw err;
    }
    caseRecord.status = status;
    caseRecord.auditTrail = [
      ...caseRecord.auditTrail,
      { at: new Date().toISOString().slice(0, 10), actor, action: `Status changed to "${status}"` },
    ];
    return caseRecord;
  }

  const { data } = await api.patch(`/cases/${caseId}`, { status });
  return data;
}
