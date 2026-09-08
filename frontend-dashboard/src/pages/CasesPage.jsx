import { useEffect, useState } from 'react';
import AppLayout from '../components/AppLayout';
import CaseStatusBadge from '../components/CaseStatusBadge';
import AuditTrailList from '../components/AuditTrailList';
import EmptyState from '../components/EmptyState';
import { fetchCases, updateCaseStatus } from '../services/casesService';

const STATUS_OPTIONS = ['Open', 'Under Review', 'Escalated', 'Closed - No Action', 'Closed - Action Taken'];

export default function CasesPage() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCaseId, setSelectedCaseId] = useState(null);
  const [updating, setUpdating] = useState(false);

  function load() {
    setLoading(true);
    fetchCases()
      .then((data) => {
        setCases(data);
        if (!selectedCaseId && data.length > 0) setSelectedCaseId(data[0].caseId);
      })
      .finally(() => setLoading(false));
  }

  useEffect(load, []); // eslint-disable-line react-hooks/exhaustive-deps

  const selectedCase = cases.find((c) => c.caseId === selectedCaseId);

  async function handleStatusChange(newStatus) {
    if (!selectedCase) return;
    setUpdating(true);
    try {
      await updateCaseStatus(selectedCase.caseId, newStatus);
      load();
    } finally {
      setUpdating(false);
    }
  }

  return (
    <AppLayout title="Case Management" subtitle="Track flagged projects through investigation and resolution">
      {loading && <EmptyState title="Loading cases…" />}

      {!loading && cases.length === 0 && (
        <EmptyState title="No open cases" description="Cases are created when a reviewer opens a flagged project for investigation." />
      )}

      {!loading && cases.length > 0 && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="overflow-hidden rounded-lg border border-border bg-surface shadow-card lg:col-span-2">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="border-b border-border bg-navy-50 text-left text-xs font-semibold uppercase tracking-wide text-navy-700">
                  <th className="px-4 py-3">Case</th>
                  <th className="px-4 py-3">Project</th>
                  <th className="px-4 py-3">Assigned to</th>
                  <th className="px-4 py-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {cases.map((c) => (
                  <tr
                    key={c.caseId}
                    onClick={() => setSelectedCaseId(c.caseId)}
                    className={`cursor-pointer border-b border-border last:border-0 hover:bg-navy-50/60 ${
                      c.caseId === selectedCaseId ? 'bg-navy-50' : ''
                    }`}
                  >
                    <td className="px-4 py-3 font-mono text-xs">{c.caseId}</td>
                    <td className="px-4 py-3 font-mono text-xs">{c.projectId}</td>
                    <td className="px-4 py-3">{c.assignedTo}</td>
                    <td className="px-4 py-3"><CaseStatusBadge status={c.status} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {selectedCase && (
            <div className="space-y-4">
              <div className="rounded-lg border border-border bg-surface p-5 shadow-card">
                <p className="font-mono text-xs font-semibold text-ink">{selectedCase.caseId}</p>
                <p className="mt-1 text-sm text-muted">Linked project: {selectedCase.projectId}</p>

                <label className="mt-4 block text-xs font-medium text-muted">
                  Update status
                  <select
                    value={selectedCase.status}
                    disabled={updating}
                    onChange={(e) => handleStatusChange(e.target.value)}
                    className="mt-1 w-full rounded border border-border bg-white px-2.5 py-1.5 text-sm text-ink outline-none focus:border-navy-600"
                  >
                    {STATUS_OPTIONS.map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </label>
              </div>

              <div className="rounded-lg border border-border bg-surface p-5 shadow-card">
                <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted">Audit trail</p>
                <AuditTrailList entries={selectedCase.auditTrail} />
              </div>
            </div>
          )}
        </div>
      )}
    </AppLayout>
  );
}
