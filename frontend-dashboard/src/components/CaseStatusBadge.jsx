const STATUS_STYLES = {
  'Open': 'bg-navy-50 text-navy-600',
  'Under Review': 'bg-risk-medium-bg text-risk-medium',
  'Escalated': 'bg-risk-high-bg text-risk-high',
  'Closed - No Action': 'bg-gray-100 text-muted',
  'Closed - Action Taken': 'bg-risk-low-bg text-risk-low',
};

export default function CaseStatusBadge({ status }) {
  const classes = STATUS_STYLES[status] || 'bg-gray-100 text-muted';
  return (
    <span className={`inline-block rounded-sm px-2 py-0.5 text-xs font-medium ${classes}`}>
      {status}
    </span>
  );
}
