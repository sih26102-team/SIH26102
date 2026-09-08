import LoginForm from '../components/LoginForm';

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-navy-900 px-4">
      <div className="w-full max-w-md rounded-lg bg-surface p-8 shadow-card">
        <div className="mb-6 flex items-center gap-3">
          <svg width="36" height="36" viewBox="0 0 32 32" aria-hidden="true">
            <circle cx="16" cy="16" r="14" fill="#0D1B2E" />
            <circle cx="16" cy="16" r="10" fill="none" stroke="#E2E6EA" strokeWidth="3" />
            <path d="M16 6 A10 10 0 0 1 24.7 21" fill="none" stroke="#C0392B" strokeWidth="3" strokeLinecap="round" />
          </svg>
          <div>
            <h1 className="font-display text-lg font-semibold text-ink">MPLADS Investigation Console</h1>
            <p className="text-xs text-muted">SIH26102 · AI-assisted anomaly review</p>
          </div>
        </div>
        <LoginForm />
      </div>
    </div>
  );
}
