import { useState } from 'react';
import { useAuth } from '../hooks/useAuth.jsx';
import { useNavigate } from 'react-router-dom';

const ROLES = [
  { id: 'ministry', name: 'Ministry / Central Monitoring', desc: 'National-level monitoring and analytics.' },
  { id: 'state', name: 'State Nodal Authority', desc: 'State-level monitoring and oversight.' },
  { id: 'district', name: 'District Authority', desc: 'District-level project monitoring, investigation and case management.' },
  { id: 'inspector', name: 'Authorized Inspection Officer', desc: 'Assigned project inspection and evidence submission.' },
];

export default function LoginForm() {
  const { signIn, loading, error } = useAuth();
  const navigate = useNavigate();
  const [selectedRole, setSelectedRole] = useState(null);
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

  if (!selectedRole) {
    return (
      <div className="w-full max-w-md space-y-4">
        <h2 className="text-xl font-bold text-navy-900 mb-4">Select your role</h2>
        <div className="space-y-3">
          {ROLES.map(role => (
            <button
              key={role.id}
              onClick={() => setSelectedRole(role)}
              className="w-full text-left p-4 rounded-xl border border-navy-200 bg-white hover:border-navy-600 hover:shadow-md transition group"
            >
              <div className="font-semibold text-navy-900 group-hover:text-navy-700">{role.name}</div>
              <div className="text-xs text-muted mt-1">{role.desc}</div>
            </button>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-md space-y-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="text-xs font-semibold text-muted uppercase tracking-wider">Selected Role:</div>
          <div className="text-navy-900 font-bold">{selectedRole.name}</div>
        </div>
        <button 
          onClick={() => setSelectedRole(null)} 
          className="text-sm text-navy-600 hover:text-navy-800 font-medium"
        >
          &larr; Change Role
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4 rounded-xl border border-border bg-white p-6 shadow-sm">
        <div>
          <label htmlFor="username" className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-ink">
            Official ID
          </label>
          <input
            id="username"
            type="text"
            autoComplete="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Official ID"
            className="w-full rounded border border-border bg-white px-3.5 py-2.5 text-sm text-ink outline-none transition focus:border-navy-600 focus:ring-2 focus:ring-navy-100"
            required
          />
        </div>

        <div>
          <label htmlFor="password" className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-ink">
            Password
          </label>
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
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
          {loading ? 'Authenticating...' : 'Authenticate & Sign In'}
        </button>
      </form>
    </div>
  );
}
