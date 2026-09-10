import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import AppLayout from '../components/AppLayout';
import RiskExplanationPanel from '../components/RiskExplanationPanel';
import ProjectLocationMap from '../components/ProjectLocationMap';
import DataQualityBadge from '../components/DataQualityBadge';
import EmptyState from '../components/EmptyState';
import { fetchProjectById } from '../services/worksService';
import { requestInvestigation, adminDirectAssign } from '../services/casesService';
import { fetchUsers } from '../services/usersService';
import { useAuth } from '../hooks/useAuth';
import { formatINR, formatDate } from '../utils/formatters';

function Field({ label, value }) {
  return (
    <div>
      <p className="text-xs font-medium uppercase tracking-wide text-muted">{label}</p>
      <p className="mt-0.5 text-sm font-semibold text-ink">{value ?? '—'}</p>
    </div>
  );
}

export default function ProjectDetailPage() {
  const { projectId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Modals & Action state
  const [isRequestModalOpen, setIsRequestModalOpen] = useState(false);
  const [requestReason, setRequestReason] = useState('Anomalous burn rate and financial/physical progress divergence detected during algorithmic sampling. Field inspection required.');
  const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
  const [investigators, setInvestigators] = useState([]);
  const [selectedInvestigatorId, setSelectedInvestigatorId] = useState('');
  const [actionLoading, setActionLoading] = useState(false);
  const [actionSuccess, setActionSuccess] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchProjectById(projectId)
      .then((data) => !cancelled && setProject(data))
      .catch((err) => !cancelled && setError(err.message))
      .finally(() => !cancelled && setLoading(false));

    if (user?.role === 'admin') {
      fetchUsers('investigator').then((data) => {
        setInvestigators(data);
        if (data.length > 0) setSelectedInvestigatorId(data[0].id);
      }).catch(console.error);
    }

    return () => {
      cancelled = true;
    };
  }, [projectId, user?.role]);

  async function handleRequestInvestigation(e) {
    e.preventDefault();
    setActionLoading(true);
    try {
      await requestInvestigation({
        flagged_work_id: projectId,
        title: `Field Audit for ${projectId} (${project?.category || 'Civil Work'})`,
        description: `Recommended by ${project?.constituency || 'Constituency'}, ${project?.district || 'District'}`,
        request_reason: requestReason,
        risk_score: project?.riskScore || 85,
        risk_level: project?.riskLevel || 'HIGH',
        flagged_reasons: project?.reasons?.map((r) => r.text || r).join('; ')
      });
      setIsRequestModalOpen(false);
      setActionSuccess('Investigation requested successfully! Status: PENDING ADMIN APPROVAL.');
    } catch (err) {
      alert(err.response?.data?.detail || err.message || 'Failed to request investigation');
    } finally {
      setActionLoading(false);
    }
  }

  async function handleDirectAssign(e) {
    e.preventDefault();
    setActionLoading(true);
    try {
      await adminDirectAssign({
        flagged_work_id: projectId,
        title: `Direct Assignment for ${projectId}`,
        investigator_id: Number(selectedInvestigatorId),
        description: `Directly dispatched by System Administrator`,
        risk_score: project?.riskScore || 85,
        risk_level: project?.riskLevel || 'HIGH',
        flagged_reasons: project?.reasons?.map((r) => r.text || r).join('; ')
      });
      setIsAssignModalOpen(false);
      setActionSuccess('Project successfully assigned to investigator! Status: ASSIGNED.');
    } catch (err) {
      alert(err.response?.data?.detail || err.message || 'Failed to assign investigator');
    } finally {
      setActionLoading(false);
    }
  }

  return (
    <AppLayout title="Project Investigation" subtitle={projectId}>
      <div className="mb-4 flex items-center justify-between">
        <Link to="/dashboard" className="inline-flex items-center text-sm font-medium text-navy-600 hover:underline">
          ← Back to Flagged Works
        </Link>

        {/* Role-based action buttons */}
        <div className="flex gap-2">
          {user?.role === 'admin' && (
            <button
              onClick={() => setIsAssignModalOpen(true)}
              className="rounded-lg bg-navy-800 px-4 py-2 text-xs font-semibold text-white shadow hover:bg-navy-900 transition"
            >
              🛡️ Direct Assign Investigator
            </button>
          )}

          {user?.role !== 'admin' && (
            <button
              onClick={() => setIsRequestModalOpen(true)}
              className="rounded-lg bg-risk-high px-4 py-2 text-xs font-semibold text-white shadow hover:bg-red-700 transition"
            >
              🔍 Request Formal Investigation
            </button>
          )}
        </div>
      </div>

      {/* Crucial Anomaly != Fraud Disclaimer Banner */}
      <div className="mb-5 rounded-lg border border-amber-200 bg-amber-50 p-4 text-xs text-amber-900 shadow-sm flex items-start gap-3">
        <span className="text-xl">⚠️</span>
        <div>
          <p className="font-bold uppercase tracking-wider text-amber-950">Statutory Notice: ANOMALY ≠ FRAUD</p>
          <p className="mt-0.5 text-amber-900/90 leading-relaxed">
            CivicShield AI is an objective decision-support and risk-prioritization system. An anomaly flag indicates statistical, temporal, or expenditure deviations that warrant on-site verification per MPLADS 2023 Guidelines. It does <strong>not</strong> automatically accuse or establish guilt of fraudulent conduct.
          </p>
        </div>
      </div>

      {actionSuccess && (
        <div className="mb-4 rounded-lg border border-emerald-300 bg-emerald-50 p-3 text-xs text-emerald-800 flex items-center justify-between">
          <span>✅ {actionSuccess}</span>
          <button onClick={() => navigate('/cases')} className="font-bold underline ml-2">
            View in Case Management →
          </button>
        </div>
      )}

      {loading && <EmptyState title="Loading project details…" />}
      {error && <EmptyState tone="error" title="Couldn't load this project" description={error} />}

      {project && !loading && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="space-y-4 lg:col-span-2">
            <div className="rounded-xl border border-border bg-surface p-6 shadow-card">
              <div className="mb-4 flex items-start justify-between border-b border-border pb-4">
                <div>
                  <p className="font-mono text-base font-bold text-ink">{project.projectId}</p>
                  <p className="text-sm text-muted">{project.constituency}, {project.district}, {project.state}</p>
                </div>
                <DataQualityBadge dataQuality={project.dataQuality} />
              </div>

              <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
                <Field label="Sector Category" value={project.category} />
                <Field label="Implementing Agency" value={project.implementingAgency} />
                <Field label="Execution Status" value={project.status} />
                <Field label="Sanctioned Amount" value={formatINR(project.sanctionedAmount)} />
                <Field label="Released Amount" value={formatINR(project.releasedAmount)} />
                <Field label="Expenditure" value={formatINR(project.expenditure)} />
                <Field label="Fund Utilization" value={`${project.utilizationPct}%`} />
                <Field label="Physical Progress" value={`${project.progressPct}%`} />
                <Field label="Sanction Date" value={formatDate(project.startDate)} />
                <Field label="Target Completion" value={formatDate(project.expectedCompletionDate)} />
                <Field label="Actual Completion" value={formatDate(project.actualCompletionDate)} />
                <Field label="Days Overdue" value={project.delayDays > 0 ? `${project.delayDays} days` : 'Within SLA'} />
              </div>
            </div>

            <ProjectLocationMap project={project} />
          </div>

          <div className="space-y-4">
            <RiskExplanationPanel project={project} />
          </div>
        </div>
      )}

      {/* Investigator Request Modal */}
      {isRequestModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
            <h3 className="text-base font-bold text-ink">Request Formal Investigation</h3>
            <p className="mt-1 text-xs text-muted">
              Submit a prioritized field audit request to the System Administrator for Project <strong>{projectId}</strong>.
            </p>

            <form onSubmit={handleRequestInvestigation} className="mt-4 space-y-3.5">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-ink">Justification & Observations</label>
                <textarea
                  rows={4}
                  value={requestReason}
                  onChange={(e) => setRequestReason(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-border p-3 text-sm text-ink outline-none focus:border-navy-600 leading-relaxed"
                  required
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsRequestModalOpen(false)}
                  className="rounded-lg border border-border px-4 py-2 text-xs font-semibold text-ink hover:bg-navy-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={actionLoading}
                  className="rounded-lg bg-risk-high px-4 py-2 text-xs font-semibold text-white shadow hover:bg-red-700"
                >
                  {actionLoading ? 'Submitting…' : 'Submit Request to Admin'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Admin Direct Assignment Modal */}
      {isAssignModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
            <h3 className="text-base font-bold text-ink">Admin Direct Assignment</h3>
            <p className="mt-1 text-xs text-muted">
              Assign an on-site field investigator for Project <strong>{projectId}</strong>.
            </p>

            <form onSubmit={handleDirectAssign} className="mt-4 space-y-3.5">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-ink">Select Field Investigator</label>
                <select
                  value={selectedInvestigatorId}
                  onChange={(e) => setSelectedInvestigatorId(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-border p-2.5 text-sm text-ink outline-none focus:border-navy-600"
                  required
                >
                  {investigators.map((inv) => (
                    <option key={inv.id} value={inv.id}>
                      {inv.full_name || inv.username} ({inv.email})
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsAssignModalOpen(false)}
                  className="rounded-lg border border-border px-4 py-2 text-xs font-semibold text-ink hover:bg-navy-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={actionLoading}
                  className="rounded-lg bg-navy-800 px-4 py-2 text-xs font-semibold text-white shadow hover:bg-navy-900"
                >
                  {actionLoading ? 'Assigning…' : 'Confirm Assignment'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AppLayout>
  );
}
