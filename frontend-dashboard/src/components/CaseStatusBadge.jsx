const STATUS_STYLES = {
  // Uppercase backend statuses
  'REQUESTED': 'bg-amber-100 text-amber-800 border border-amber-300',
  'ASSIGNED': 'bg-blue-100 text-blue-800 border border-blue-300',
  'UNDER_INVESTIGATION': 'bg-indigo-100 text-indigo-800 border border-indigo-300',
  'EVIDENCE_SUBMITTED': 'bg-purple-100 text-purple-800 border border-purple-300',
  'UNDER_REVIEW': 'bg-amber-100 text-amber-800 border border-amber-300',
  'RESOLVED': 'bg-emerald-100 text-emerald-800 border border-emerald-300',
  'ESCALATED': 'bg-rose-100 text-rose-800 border border-rose-300',
  'REJECTED': 'bg-red-100 text-red-800 border border-red-300',
  'CLOSED_ACTION_TAKEN': 'bg-emerald-100 text-emerald-800 border border-emerald-300',
  'CLOSED_NO_ACTION': 'bg-gray-100 text-gray-700 border border-gray-300',

  // Title case legacy
  'Open': 'bg-navy-50 text-navy-600',
  'Under Review': 'bg-amber-100 text-amber-800',
  'Escalated': 'bg-rose-100 text-rose-800',
  'Resolved': 'bg-emerald-100 text-emerald-800',
  'Closed - No Action': 'bg-gray-100 text-muted',
  'Closed - Action Taken': 'bg-emerald-100 text-emerald-800',
};

export default function CaseStatusBadge({ status }) {
  const norm = String(status || '').toUpperCase().replace(/ /g, '_');
  const classes = STATUS_STYLES[status] || STATUS_STYLES[norm] || 'bg-gray-100 text-muted';
  const label = String(status || 'UNKNOWN').replace(/_/g, ' ');

  return (
    <span className={`inline-block rounded px-2 py-0.5 text-[11px] font-bold tracking-wide uppercase ${classes}`}>
      {label}
    </span>
  );
}
