import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-3 bg-bg text-center">
      <p className="font-display text-3xl font-semibold text-ink">404</p>
      <p className="text-sm text-muted">That page doesn't exist.</p>
      <Link to="/dashboard" className="text-sm font-medium text-navy-600 hover:underline">
        Back to dashboard
      </Link>
    </div>
  );
}
