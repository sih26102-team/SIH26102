import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import AppLayout from '../components/AppLayout';
import RiskExplanationPanel from '../components/RiskExplanationPanel';
import ProjectLocationMap from '../components/ProjectLocationMap';
import DataQualityBadge from '../components/DataQualityBadge';
import EmptyState from '../components/EmptyState';
import { fetchProjectById } from '../services/worksService';
import { formatINR, formatDate } from '../utils/formatters';

function Field({ label, value }) {
  return (
    <div>
      <p className="text-xs font-medium uppercase tracking-wide text-muted">{label}</p>
      <p className="mt-0.5 text-sm text-ink">{value ?? '—'}</p>
    </div>
  );
}

export default function ProjectDetailPage() {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchProjectById(projectId)
      .then((data) => !cancelled && setProject(data))
      .catch((err) => !cancelled && setError(err.message))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [projectId]);

  return (
    <AppLayout title="Project Investigation" subtitle={projectId}>
      <Link to="/dashboard" className="mb-4 inline-block text-sm font-medium text-navy-600 hover:underline">
        ← Back to flagged works
      </Link>

      {loading && <EmptyState title="Loading project…" />}
      {error && <EmptyState tone="error" title="Couldn't load this project" description={error} />}

      {project && !loading && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="space-y-4 lg:col-span-2">
            <div className="rounded-lg border border-border bg-surface p-5 shadow-card">
              <div className="mb-4 flex items-start justify-between">
                <div>
                  <p className="font-mono text-sm font-semibold text-ink">{project.projectId}</p>
                  <p className="text-sm text-muted">{project.constituency}, {project.district}, {project.state}</p>
                </div>
                <DataQualityBadge dataQuality={project.dataQuality} />
              </div>

              <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
                <Field label="Category" value={project.category} />
                <Field label="Implementing agency" value={project.implementingAgency} />
                <Field label="Status" value={project.status} />
                <Field label="Sanctioned amount" value={formatINR(project.sanctionedAmount)} />
                <Field label="Released amount" value={formatINR(project.releasedAmount)} />
                <Field label="Expenditure" value={formatINR(project.expenditure)} />
                <Field label="Fund utilization" value={`${project.utilizationPct}%`} />
                <Field label="Physical progress" value={`${project.progressPct}%`} />
                <Field label="Start date" value={formatDate(project.startDate)} />
                <Field label="Expected completion" value={formatDate(project.expectedCompletionDate)} />
                <Field label="Actual completion" value={formatDate(project.actualCompletionDate)} />
                <Field label="Days overdue" value={project.delayDays > 0 ? project.delayDays : 'On schedule'} />
              </div>
            </div>

            {project.isSynthetic && (
              <p className="rounded border border-dashed border-border bg-navy-50 px-3 py-2 text-xs text-muted">
                This record is synthetic demonstration data, not a real MPLADS project.
              </p>
            )}

            <ProjectLocationMap project={project} />
          </div>

          <div className="space-y-4">
            <RiskExplanationPanel project={project} />
          </div>
        </div>
      )}
    </AppLayout>
  );
}
