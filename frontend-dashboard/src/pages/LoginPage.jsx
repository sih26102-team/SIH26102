import LoginForm from '../components/LoginForm';

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-navy-900 px-4">
      <div className="w-full max-w-md rounded-lg bg-surface p-8 shadow-card">
        <div className="mb-6 flex items-center gap-3">
          <img src="/civicshield-logo.png" alt="CivicShield logo" className="h-14 w-14 rounded-lg object-..." />
          <div>
            <h1 className="font-display text-lg font-semibold text-ink">CivicShield</h1>
            <p className="text-xs text-muted">SIH26102 · AI-assisted anomaly review</p>
          </div>
        </div>
        <LoginForm />
      </div>
    </div>
  );
}
