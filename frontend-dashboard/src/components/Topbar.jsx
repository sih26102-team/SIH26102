import { useAuth } from '../hooks/useAuth.jsx';
import { useNavigate } from 'react-router-dom';

export default function Topbar({ title, subtitle, onMenuClick }) {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();

  function handleSignOut() {
    signOut();
    navigate('/login');
  }

  return (
    <header className="flex items-center justify-between border-b border-border bg-surface px-4 py-4 sm:px-6">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onMenuClick}
          className="text-ink md:hidden"
          aria-label="Open menu"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M4 6h16M4 12h16M4 18h16" strokeLinecap="round" />
          </svg>
        </button>
        <div>
          <h1 className="font-display text-base font-semibold text-ink sm:text-lg">{title}</h1>
          {subtitle && <p className="text-xs text-muted sm:text-sm">{subtitle}</p>}
        </div>
      </div>
      <div className="flex items-center gap-3">
        <div className="hidden text-right sm:block">
          <p className="text-sm font-medium text-ink">{user?.name}</p>
          <p className="text-xs text-muted">{user?.role}</p>
        </div>
        <button
          type="button"
          onClick={handleSignOut}
          className="rounded border border-border px-3 py-1.5 text-xs font-semibold text-muted transition hover:border-navy-600 hover:text-navy-600"
        >
          Sign out
        </button>
      </div>
    </header>
  );
}
