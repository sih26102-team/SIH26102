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
      // error is already surfaced via useAuth().error
    }
  }

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-5">
      <div>
        <label htmlFor="username" className="mb-1.5 block text-sm font-medium text-ink">
          Username
        </label>
        <input
          id="username"
          type="text"
          autoComplete="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="officer.id"
          className="w-full rounded border border-border bg-white px-3 py-2.5 text-sm text-ink outline-none transition focus:border-navy-600 focus:ring-2 focus:ring-navy-100"
          required
        />
      </div>

      <div>
        <label htmlFor="password" className="mb-1.5 block text-sm font-medium text-ink">
          Password
        </label>
        <input
          id="password"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="••••••••"
          className="w-full rounded border border-border bg-white px-3 py-2.5 text-sm text-ink outline-none transition focus:border-navy-600 focus:ring-2 focus:ring-navy-100"
          required
        />
      </div>

      {error && (
        <p role="alert" className="rounded bg-risk-high-bg px-3 py-2 text-sm text-risk-high">
          {error}
        </p>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full rounded bg-navy-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-navy-700 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {loading ? 'Signing in…' : 'Sign in'}
      </button>

      <p className="text-center text-xs text-muted">
        Access is limited to authorized monitoring officials, audit personnel,
        scheme administrators, and implementing authorities.
      </p>
    </form>
  );
}
// LoginForm.jsx — owner: Chandana
