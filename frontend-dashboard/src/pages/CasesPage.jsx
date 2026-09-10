import { useEffect, useState } from 'react';
import AppLayout from '../components/AppLayout';
import CaseStatusBadge from '../components/CaseStatusBadge';
import EmptyState from '../components/EmptyState';
import { useAuth } from '../hooks/useAuth';
import { fetchUsers } from '../services/usersService';
import {
  fetchCases,
  approveCase,
  rejectCase,
  submitEvidence,
  resolveCase,
  fetchCaseAudit
} from '../services/casesService';
import { formatDate } from '../utils/formatters';

export default function CasesPage() {
  const { user } = useAuth();
  const isAdmin = user?.role === 'admin';

  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCaseId, setSelectedCaseId] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [auditLoading, setAuditLoading] = useState(false);

  // Investigators list for admin approval assignment
  const [investigators, setInvestigators] = useState([]);
  const [selectedAssignee, setSelectedAssignee] = useState('');

  // Modals state
  const [isEvidenceModalOpen, setIsEvidenceModalOpen] = useState(false);
  const [isResolveModalOpen, setIsResolveModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Field Inspection Form State
  const [siteCondition, setSiteCondition] = useState('Foundations laid; pillar reinforcement underway but roof slab pending.');
  const [financialObservation, setFinancialObservation] = useState('Reported expenditure is 85% of sanction, but observed physical progress is ~45%.');
  const [recommendation, setRecommendation] = useState('Withhold next installment until IDA verifies contractor measurement book (MB).');
  const [investigatorNotes, setInvestigatorNotes] = useState('Field visit completed. Interacted with local residents and inspected site physical ledger.');
  const [evidencePhoto, setEvidencePhoto] = useState(null);
  const [gpsLocation, setGpsLocation] = useState(null);
  const [gpsStatus, setGpsStatus] = useState('NOT_CAPTURED'); // NOT_CAPTURED, CAPTURING, CAPTURED, ERROR

  // Resolution Form State
  const [resolutionType, setResolutionType] = useState('RESOLVED');
  const [resolutionNotes, setResolutionNotes] = useState('Field verification concluded. Physical progress reconciled with revised contractor timeline.');

  function loadCases() {
    setLoading(true);
    fetchCases()
      .then((data) => {
        setCases(data);
        if (data.length > 0 && !selectedCaseId) {
          setSelectedCaseId(data[0].id || data[0].caseId);
        }
      })
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadCases();
    if (isAdmin) {
      fetchUsers('investigator').then((invs) => {
        setInvestigators(invs);
        if (invs.length > 0) setSelectedAssignee(invs[0].id);
      }).catch(console.error);
    }
  }, [isAdmin]);

  const selectedCase = cases.find((c) => c.id === Number(selectedCaseId) || c.caseId === selectedCaseId);

  useEffect(() => {
    if (selectedCase) {
      setAuditLoading(true);
      fetchCaseAudit(selectedCase.id || selectedCase.caseId)
        .then((logs) => setAuditLogs(logs))
        .catch(() => setAuditLogs([]))
        .finally(() => setAuditLoading(false));
    }
  }, [selectedCaseId]);

  function captureGenuineLocation() {
    if (!navigator.geolocation) {
      setGpsStatus('ERROR');
      alert('Geolocation is not supported by your browser.');
      return;
    }

    setGpsStatus('CAPTURING');
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setGpsLocation({
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
          timestamp: new Date().toISOString()
        });
        setGpsStatus('CAPTURED');
      },
      (err) => {
        console.warn('GPS Error:', err);
        setGpsStatus('ERROR');
        alert(`Could not capture genuine location: ${err.message}. Status set to LOCATION NOT CAPTURED.`);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  }

  function handlePhotoUpload(e) {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setEvidencePhoto(reader.result);
      };
      reader.readAsDataURL(file);
    }
  }

  async function handleApprove(caseId) {
    if (!window.confirm('Approve this investigation request and dispatch assignment?')) return;
    setSubmitting(true);
    try {
      await approveCase(caseId, {
        investigator_id: selectedAssignee ? Number(selectedAssignee) : undefined,
        admin_notes: 'Approved for on-site physical inspection by Administrator'
      });
      loadCases();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to approve case');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleReject(caseId) {
    const reason = window.prompt('Enter reason for rejecting this investigation request:');
    if (!reason) return;
    setSubmitting(true);
    try {
      await rejectCase(caseId, { rejection_reason: reason });
      loadCases();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to reject case');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleSubmitEvidence(e) {
    e.preventDefault();
    if (!selectedCase) return;
    setSubmitting(true);
    try {
      await submitEvidence(selectedCase.id || selectedCase.caseId, {
        evidence_photo_url: evidencePhoto || 'https://images.unsplash.com/photo-1541888946425-d0fbb18f15f8?auto=format&fit=crop&w=600&q=80',
        latitude: gpsLocation?.lat || null,
        longitude: gpsLocation?.lng || null,
        location_timestamp: gpsLocation?.timestamp || null,
        site_condition: siteCondition,
        financial_observation: financialObservation,
        investigator_recommendation: recommendation,
        investigator_notes: investigatorNotes
      });
      setIsEvidenceModalOpen(false);
      loadCases();
      alert('Inspection evidence and findings successfully recorded!');
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to submit evidence');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleResolve(e) {
    e.preventDefault();
    if (!selectedCase) return;
    setSubmitting(true);
    try {
      await resolveCase(selectedCase.id || selectedCase.caseId, {
        resolution: resolutionType,
        resolution_notes: resolutionNotes
      });
      setIsResolveModalOpen(false);
      loadCases();
      alert(`Case marked as ${resolutionType}`);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to resolve case');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AppLayout
      title="Investigation Case Management"
      subtitle="Lifecycle tracking, field inspection reports, immutable audit trails, and resolution"
    >
      {loading && <EmptyState title="Loading cases…" />}

      {!loading && cases.length === 0 && (
        <EmptyState
          title="No Active Cases"
          description="Cases appear here when an investigator requests an audit or an administrator directly assigns a project."
        />
      )}

      {!loading && cases.length > 0 && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Left Table: Cases List */}
          <div className="overflow-hidden rounded-xl border border-border bg-surface shadow-card lg:col-span-2">
            <div className="border-b border-border bg-navy-50/70 px-4 py-3 text-xs font-semibold uppercase text-navy-800 flex justify-between items-center">
              <span>Active Investigation Registry</span>
              <span className="text-muted font-normal">Total: {cases.length}</span>
            </div>
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="border-b border-border bg-white text-left text-xs font-semibold uppercase tracking-wider text-muted">
                  <th className="px-4 py-3">Case</th>
                  <th className="px-4 py-3">Linked Work</th>
                  <th className="px-4 py-3">Assigned Officer</th>
                  <th className="px-4 py-3">Workflow Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {cases.map((c) => {
                  const isSelected = (c.id === Number(selectedCaseId)) || (c.caseId === selectedCaseId);
                  return (
                    <tr
                      key={c.caseId || c.id}
                      onClick={() => setSelectedCaseId(c.id || c.caseId)}
                      className={`cursor-pointer transition hover:bg-navy-50/70 ${
                        isSelected ? 'bg-navy-100/60 font-medium' : ''
                      }`}
                    >
                      <td className="px-4 py-3.5 font-mono text-xs font-bold text-navy-900">
                        {c.caseId || `CASE-${c.id}`}
                      </td>
                      <td className="px-4 py-3.5 font-mono text-xs text-ink">{c.flagged_work_id || c.projectId}</td>
                      <td className="px-4 py-3.5 text-xs text-muted">
                        {c.assignedTo || c.assigned_officer?.full_name || 'Unassigned'}
                      </td>
                      <td className="px-4 py-3.5">
                        <CaseStatusBadge status={c.status} />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Right Panel: Selected Case Detail & Action Machine */}
          {selectedCase && (
            <div className="space-y-4">
              {/* Primary Case Info Card */}
              <div className="rounded-xl border border-border bg-surface p-5 shadow-card space-y-3">
                <div className="flex items-center justify-between border-b border-border pb-3">
                  <div>
                    <span className="font-mono text-sm font-bold text-ink">
                      {selectedCase.caseId || `CASE-${selectedCase.id}`}
                    </span>
                    <p className="text-xs text-muted">Project: {selectedCase.flagged_work_id || selectedCase.projectId}</p>
                  </div>
                  <CaseStatusBadge status={selectedCase.status} />
                </div>

                <div className="text-xs text-ink space-y-1.5">
                  <p><strong>Title:</strong> {selectedCase.title}</p>
                  {selectedCase.request_reason && (
                    <p className="rounded bg-amber-50 p-2 text-amber-900 border border-amber-200">
                      <strong>Requester Reason:</strong> {selectedCase.request_reason}
                    </p>
                  )}
                  <p><strong>Assigned Officer:</strong> {selectedCase.assignedTo || selectedCase.assigned_officer?.full_name || 'Unassigned'}</p>
                  {selectedCase.resolution_notes && (
                    <p className="rounded bg-emerald-50 p-2 text-emerald-900 border border-emerald-200">
                      <strong>Resolution Notes:</strong> {selectedCase.resolution_notes}
                    </p>
                  )}
                </div>

                {/* State Machine Actions */}
                <div className="pt-2 border-t border-border space-y-2">
                  <p className="text-[11px] font-bold uppercase tracking-wider text-muted">Permitted Workflow Actions:</p>

                  {/* Admin Approval/Rejection for REQUESTED cases */}
                  {isAdmin && selectedCase.status === 'REQUESTED' && (
                    <div className="space-y-2">
                      <div className="text-xs">
                        <label className="block mb-1 font-semibold text-ink">Assign Investigator:</label>
                        <select
                          value={selectedAssignee}
                          onChange={(e) => setSelectedAssignee(e.target.value)}
                          className="w-full rounded border border-border p-1.5 text-xs text-ink"
                        >
                          {investigators.map((inv) => (
                            <option key={inv.id} value={inv.id}>{inv.full_name || inv.username}</option>
                          ))}
                        </select>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleApprove(selectedCase.id || selectedCase.caseId)}
                          disabled={submitting}
                          className="flex-1 rounded-lg bg-emerald-600 py-2 text-xs font-bold text-white shadow hover:bg-emerald-700 transition"
                        >
                          ✓ Approve & Assign
                        </button>
                        <button
                          onClick={() => handleReject(selectedCase.id || selectedCase.caseId)}
                          disabled={submitting}
                          className="flex-1 rounded-lg bg-rose-600 py-2 text-xs font-bold text-white shadow hover:bg-rose-700 transition"
                        >
                          ✗ Reject Request
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Investigator Evidence Submission for ASSIGNED or UNDER_INVESTIGATION cases */}
                  {(selectedCase.status === 'ASSIGNED' || selectedCase.status === 'UNDER_INVESTIGATION' || selectedCase.status === 'OPEN') && (
                    <button
                      onClick={() => setIsEvidenceModalOpen(true)}
                      className="w-full rounded-lg bg-navy-800 py-2 text-xs font-bold text-white shadow hover:bg-navy-900 transition flex items-center justify-center gap-1.5"
                    >
                      📸 Submit Field Inspection & Evidence
                    </button>
                  )}

                  {/* Resolution Modal for Submitted / Under Review Cases */}
                  {(selectedCase.status === 'EVIDENCE_SUBMITTED' || selectedCase.status === 'UNDER_REVIEW' || isAdmin) && (
                    <button
                      onClick={() => setIsResolveModalOpen(true)}
                      className="w-full rounded-lg border border-border bg-white py-2 text-xs font-bold text-navy-800 shadow-sm hover:bg-navy-50 transition"
                    >
                      ⚖️ Resolve / Escalate Case
                    </button>
                  )}
                </div>
              </div>

              {/* Uploaded Evidence Preview Card (if available) */}
              {(selectedCase.evidence_photo_url || selectedCase.site_condition) && (
                <div className="rounded-xl border border-border bg-surface p-5 shadow-card space-y-3">
                  <p className="text-xs font-bold uppercase tracking-wider text-navy-800">📸 Field Inspection Record</p>

                  {selectedCase.evidence_photo_url && (
                    <div className="overflow-hidden rounded-lg border border-border">
                      <img
                        src={selectedCase.evidence_photo_url}
                        alt="Site Inspection Proof"
                        className="h-40 w-full object-cover"
                      />
                    </div>
                  )}

                  <div className="space-y-1.5 text-xs">
                    <p>
                      <strong>GPS Location:</strong>{' '}
                      {selectedCase.latitude
                        ? <span className="font-mono text-emerald-700">📍 {selectedCase.latitude.toFixed(4)}, {selectedCase.longitude.toFixed(4)}</span>
                        : <span className="text-rose-600 font-semibold">LOCATION NOT CAPTURED</span>}
                    </p>
                    {selectedCase.site_condition && (
                      <p><strong>Site Condition:</strong> {selectedCase.site_condition}</p>
                    )}
                    {selectedCase.financial_observation && (
                      <p><strong>Financial Observation:</strong> {selectedCase.financial_observation}</p>
                    )}
                    {selectedCase.investigator_recommendation && (
                      <p><strong>Recommendation:</strong> {selectedCase.investigator_recommendation}</p>
                    )}
                  </div>
                </div>
              )}

              {/* Immutable Audit Log Trail */}
              <div className="rounded-xl border border-border bg-surface p-5 shadow-card">
                <p className="mb-3 text-xs font-bold uppercase tracking-wider text-muted">📜 Immutable Audit History</p>
                {auditLoading && <p className="text-xs text-muted">Loading audit history…</p>}
                {!auditLoading && auditLogs.length === 0 && (
                  <p className="text-xs text-muted">No historical audit events logged yet.</p>
                )}
                <div className="space-y-2.5 max-h-56 overflow-y-auto pr-1 text-xs">
                  {auditLogs.map((log) => (
                    <div key={log.id} className="border-l-2 border-navy-500 pl-2.5 py-0.5">
                      <div className="flex justify-between text-[11px] text-muted">
                        <span className="font-bold text-navy-800">{log.action}</span>
                        <span>{formatDate(log.timestamp)}</span>
                      </div>
                      <p className="text-[11px] text-ink mt-0.5">{log.details || log.new_value || 'State updated'}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Modal: Field Inspection & Evidence Submission */}
      {isEvidenceModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-base font-bold text-ink">Conduct Field Inspection</h3>
            <p className="mt-1 text-xs text-muted">
              Submit verified on-site findings and evidence for Case <strong>{selectedCase?.caseId}</strong>.
            </p>

            <form onSubmit={handleSubmitEvidence} className="mt-4 space-y-3.5 text-xs">
              {/* Photo Upload */}
              <div>
                <label className="block font-semibold uppercase tracking-wider text-ink mb-1">
                  Site Photograph (Upload Proof)
                </label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handlePhotoUpload}
                  className="w-full text-xs text-muted"
                />
                {evidencePhoto && (
                  <img src={evidencePhoto} alt="Preview" className="mt-2 h-24 rounded border object-cover" />
                )}
              </div>

              {/* Genuine Location Capture */}
              <div className="rounded-lg border border-navy-200 bg-navy-50/70 p-3">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-navy-900">Genuine Device Geolocation:</span>
                  <button
                    type="button"
                    onClick={captureGenuineLocation}
                    className="rounded bg-navy-700 px-3 py-1 text-[11px] font-bold text-white shadow-sm hover:bg-navy-800"
                  >
                    📍 Capture Genuine GPS
                  </button>
                </div>
                <p className="mt-1.5 font-mono text-[11px]">
                  {gpsStatus === 'CAPTURED' && (
                    <span className="text-emerald-700 font-bold">
                      ✓ Coordinates Recorded: ({gpsLocation.lat.toFixed(5)}, {gpsLocation.lng.toFixed(5)})
                    </span>
                  )}
                  {gpsStatus === 'CAPTURING' && <span className="text-navy-700">Acquiring device GPS satellite lock…</span>}
                  {gpsStatus === 'NOT_CAPTURED' && <span className="text-amber-700">LOCATION NOT CAPTURED (Click above to record)</span>}
                  {gpsStatus === 'ERROR' && <span className="text-rose-600 font-bold">LOCATION NOT CAPTURED (Permission Denied)</span>}
                </p>
              </div>

              <div>
                <label className="block font-semibold uppercase tracking-wider text-ink">Observed Site Condition</label>
                <textarea
                  rows={2}
                  value={siteCondition}
                  onChange={(e) => setSiteCondition(e.target.value)}
                  className="mt-1 w-full rounded border border-border p-2 text-ink outline-none focus:border-navy-600"
                  required
                />
              </div>

              <div>
                <label className="block font-semibold uppercase tracking-wider text-ink">Financial Progress Observation</label>
                <textarea
                  rows={2}
                  value={financialObservation}
                  onChange={(e) => setFinancialObservation(e.target.value)}
                  className="mt-1 w-full rounded border border-border p-2 text-ink outline-none focus:border-navy-600"
                  required
                />
              </div>

              <div>
                <label className="block font-semibold uppercase tracking-wider text-ink">Investigator Recommendation</label>
                <textarea
                  rows={2}
                  value={recommendation}
                  onChange={(e) => setRecommendation(e.target.value)}
                  className="mt-1 w-full rounded border border-border p-2 text-ink outline-none focus:border-navy-600"
                  required
                />
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-border">
                <button
                  type="button"
                  onClick={() => setIsEvidenceModalOpen(false)}
                  className="rounded-lg border border-border px-4 py-2 text-ink font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="rounded-lg bg-navy-600 px-5 py-2 font-bold text-white shadow hover:bg-navy-700"
                >
                  {submitting ? 'Recording Evidence…' : 'Submit Inspection Report'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Resolve / Escalate Case */}
      {isResolveModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
            <h3 className="text-base font-bold text-ink">Resolve or Escalate Investigation</h3>
            <p className="mt-1 text-xs text-muted">Conclude the case findings with documented resolution notes.</p>

            <form onSubmit={handleResolve} className="mt-4 space-y-3.5 text-xs">
              <div>
                <label className="block font-semibold uppercase tracking-wider text-ink">Resolution Outcome</label>
                <select
                  value={resolutionType}
                  onChange={(e) => setResolutionType(e.target.value)}
                  className="mt-1 w-full rounded border border-border p-2 text-ink"
                >
                  <option value="RESOLVED">RESOLVED (Findings Addressed / Reconciled)</option>
                  <option value="ESCALATED">ESCALATED (Forwarded to State Nodal Authority / CAG)</option>
                  <option value="CLOSED_ACTION_TAKEN">CLOSED - ACTION TAKEN (Recovery / Notice Issued)</option>
                  <option value="CLOSED_NO_ACTION">CLOSED - NO ACTION (False Anomaly Reconciled)</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold uppercase tracking-wider text-ink">Resolution Notes & Findings</label>
                <textarea
                  rows={3}
                  value={resolutionNotes}
                  onChange={(e) => setResolutionNotes(e.target.value)}
                  className="mt-1 w-full rounded border border-border p-2 text-ink"
                  required
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsResolveModalOpen(false)}
                  className="rounded-lg border border-border px-4 py-2 font-semibold text-ink"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="rounded-lg bg-navy-600 px-4 py-2 font-bold text-white shadow hover:bg-navy-700"
                >
                  {submitting ? 'Updating…' : 'Record Resolution'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AppLayout>
  );
}
