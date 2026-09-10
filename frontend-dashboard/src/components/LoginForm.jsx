import { useState } from 'react';
import { useAuth } from '../hooks/useAuth.jsx';
import { useNavigate } from 'react-router-dom';

export default function LoginForm() {
  const { signIn, loading, error } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      await signIn(username, password);
      navigate('/dashboard');
    } catch {
      // error is surfaced via useAuth().error
    }
  }

  function applyDemoCredentials(role) {
    if (role === 'mohith_admin') {
      setUsername('mohith.annam@nic.in');
      setPassword('Mohith@Admin2026!');
    } else if (role === 'arun_investigator') {
      setUsername('arun.kumar@nic.in');
      setPassword('Investigator@2026!');
    } else if (role === 'admin') {
      setUsername('admin.demo');
      setPassword('CivicShieldAdmin@2026!');
    } else {
      setUsername('investigator.demo');
      setPassword('CivicShield@Demo2026!');
    }
  }

  return (
    <div className="w-full max-w-md space-y-6">
      <form onSubmit={handleSubmit} className="space-y-4 rounded-xl border border-border bg-white p-6 shadow-sm">
        <div>
          <label htmlFor="username" className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-ink">
            Official Identifier / Username
          </label>
          <input
            id="username"
            type="text"
            autoComplete="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="e.g. mohith.annam@nic.in or arun.kumar@nic.in"
            className="w-full rounded border border-border bg-white px-3.5 py-2.5 text-sm text-ink outline-none transition focus:border-navy-600 focus:ring-2 focus:ring-navy-100"
            required
          />
        </div>

        <div>
          <label htmlFor="password" className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-ink">
            Secure Password
          </label>
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••••••"
            className="w-full rounded border border-border bg-white px-3.5 py-2.5 text-sm text-ink outline-none transition focus:border-navy-600 focus:ring-2 focus:ring-navy-100"
            required
          />
        </div>

        {error && (
          <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-3 text-xs text-red-700">
            <strong>Authentication Failed:</strong> {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-navy-600 px-4 py-2.5 text-sm font-semibold text-white shadow transition hover:bg-navy-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? 'Authenticating Official…' : 'Authenticate & Sign In'}
        </button>

        <p className="text-center text-[11px] text-muted leading-relaxed">
          <strong>Access Restricted:</strong> Public registration is strictly prohibited. Accounts are provisioned exclusively by authorized System Administrators.
        </p>
      </form>

      {/* Quick Demo Credentials Panel for Presentation */}
      <div className="rounded-lg border border-dashed border-navy-200 bg-navy-50/80 p-4 text-xs text-navy-900">
        <p className="font-semibold text-navy-800 mb-2">⚡ 1-Click Presentation Credentials:</p>
        <div className="grid grid-cols-2 gap-2">
          <button
            type="button"
            onClick={() => applyDemoCredentials('mohith_admin')}
            className="rounded border border-navy-300 bg-white p-2 text-left font-medium text-navy-700 shadow-sm hover:bg-navy-100 transition"
          >
            🛡️ <strong>Admin (NIC)</strong><br />
            <span className="text-[10px] text-muted font-mono truncate block">mohith.annam@nic.in</span>
          </button>
          <button
            type="button"
            onClick={() => applyDemoCredentials('arun_investigator')}
            className="rounded border border-navy-300 bg-white p-2 text-left font-medium text-navy-700 shadow-sm hover:bg-navy-100 transition"
          >
            🔍 <strong>Investigator (NIC)</strong><br />
            <span className="text-[10px] text-muted font-mono truncate block">arun.kumar@nic.in</span>
          </button>
        </div>
      </div>
    </div>
  );
}
