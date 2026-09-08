export function formatINR(amount) {
  if (amount === null || amount === undefined) return '—';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatDate(isoString) {
  if (!isoString) return '—';
  const d = new Date(isoString);
  if (Number.isNaN(d.getTime())) return '—';
  return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
}

export function formatPct(value) {
  if (value === null || value === undefined) return '—';
  return `${value}%`;
}

export function formatDelay(days) {
  if (!days || days <= 0) return 'On schedule';
  if (days < 30) return `${days}d overdue`;
  const months = Math.round(days / 30);
  return `${months}mo overdue`;
}
