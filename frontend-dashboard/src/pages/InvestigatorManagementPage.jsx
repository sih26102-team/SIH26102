import { useState, useEffect } from 'react';
import AppLayout from '../components/AppLayout';
import EmptyState from '../components/EmptyState';
import { useAuth } from '../hooks/useAuth';
import { fetchUsers, createInvestigator, toggleUserStatus } from '../services/usersService';

export default function InvestigatorManagementPage() {
  const { user } = useAuth();
  const [investigators, setInvestigators] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState(null);

  // Form State
  const [username, setUsername] = useState('');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('CivicShield@Demo2026!');

  function loadUsers() {
    setLoading(true);
    fetchUsers('investigator')
      .then((data) => setInvestigators(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadUsers();
  }, []);

  async function handleCreate(e) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await createInvestigator({
        username,
        full_name: fullName,
        email,
        password,
        role: 'investigator'
      });
      setSuccessMsg(`Investigator account "${username}" created successfully.`);
      setIsModalOpen(false);
      setUsername('');
      setFullName('');
      setEmail('');
      loadUsers();
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to create investigator');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleToggle(id) {
    try {
      await toggleUserStatus(id);
      loadUsers();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to toggle status');
    }
  }

  if (user?.role !== 'admin') {
    return (
      <AppLayout title="Access Denied" subtitle="Administrator privileges required">
        <EmptyState
          tone="error"
          title="Unauthorized Section"
          description="Only system administrators are authorized to manage investigator accounts."
        />
      </AppLayout>
    );
  }

  return (
    <AppLayout
      title="Investigator Management"
      subtitle="Authorized Admin Console: Provision and monitor field audit personnel"
    >
      <div className="mb-6 flex items-center justify-between">
        <div>
          <p className="text-sm text-muted">
            Provision official investigator accounts. Public registration is prohibited per security policy.
          </p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="rounded-lg bg-navy-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-navy-700 transition"
        >
          + Provision New Investigator
        </button>
      </div>

      {successMsg && (
        <div className="mb-4 rounded-lg bg-emerald-50 border border-emerald-200 p-3 text-xs text-emerald-800">
          ✅ {successMsg}
        </div>
      )}

      {loading && <EmptyState title="Loading investigators..." />}
      {error && <EmptyState tone="error" title="Error" description={error} />}

      {!loading && (
        <div className="overflow-hidden rounded-xl border border-border bg-white shadow-card">
          <table className="w-full border-collapse text-left text-sm">
            <thead>
              <tr className="border-b border-border bg-navy-50 text-xs font-semibold uppercase tracking-wider text-navy-800">
                <th className="px-5 py-3.5">Officer Name</th>
                <th className="px-5 py-3.5">Username</th>
                <th className="px-5 py-3.5">Official Email</th>
                <th className="px-5 py-3.5">Role</th>
                <th className="px-5 py-3.5">Account Status</th>
                <th className="px-5 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {investigators.map((inv) => (
                <tr key={inv.id} className="hover:bg-navy-50/50 transition">
                  <td className="px-5 py-3.5 font-medium text-ink">{inv.full_name || inv.name || '—'}</td>
                  <td className="px-5 py-3.5 font-mono text-xs text-muted">{inv.username}</td>
                  <td className="px-5 py-3.5 text-xs text-ink">{inv.email}</td>
                  <td className="px-5 py-3.5">
                    <span className="inline-flex rounded bg-navy-100 px-2.5 py-0.5 text-xs font-medium text-navy-800 uppercase">
                      {inv.role}
                    </span>
                  </td>
                  <td className="px-5 py-3.5">
                    <span
                      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ${
                        inv.is_active
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-rose-100 text-rose-800'
                      }`}
                    >
                      <span className={`h-1.5 w-1.5 rounded-full ${inv.is_active ? 'bg-emerald-500' : 'bg-rose-500'}`} />
                      {inv.is_active ? 'Active' : 'Disabled'}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <button
                      onClick={() => handleToggle(inv.id)}
                      className={`text-xs font-semibold hover:underline ${
                        inv.is_active ? 'text-rose-600' : 'text-emerald-600'
                      }`}
                    >
                      {inv.is_active ? 'Disable Account' : 'Reactivate'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Creation Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
            <h3 className="text-base font-bold text-ink">Provision Field Investigator Account</h3>
            <p className="mt-1 text-xs text-muted">
              Credentials will be generated and associated with the official investigator role.
            </p>

            <form onSubmit={handleCreate} className="mt-4 space-y-3.5">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-ink">Official Full Name</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. Ramesh V. Sharma"
                  className="mt-1 w-full rounded-lg border border-border px-3 py-2 text-sm text-ink outline-none focus:border-navy-600"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-ink">Username</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="e.g. ramesh.sharma"
                  className="mt-1 w-full rounded-lg border border-border px-3 py-2 text-sm text-ink outline-none focus:border-navy-600"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-ink">Official Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="e.g. ramesh@civicshield.gov.in"
                  className="mt-1 w-full rounded-lg border border-border px-3 py-2 text-sm text-ink outline-none focus:border-navy-600"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-ink">Temporary Password</label>
                <input
                  type="text"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-border px-3 py-2 text-sm text-ink outline-none focus:border-navy-600 font-mono"
                  required
                />
              </div>

              <div className="mt-5 flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="rounded-lg border border-border px-4 py-2 text-xs font-semibold text-ink hover:bg-navy-50 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="rounded-lg bg-navy-600 px-4 py-2 text-xs font-semibold text-white shadow hover:bg-navy-700 transition"
                >
                  {submitting ? 'Creating...' : 'Create Account'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AppLayout>
  );
}
