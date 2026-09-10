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

  const [searchTerm, setSearchTerm] = useState('');

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
        username: username.trim(),
        full_name: fullName.trim(),
        email: email.trim(),
        password: password,
        role: 'investigator'
      });
      setSuccessMsg(`Investigator "${fullName}" (@${username}) provisioned successfully. They can now log in.`);
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

  async function handleToggle(inv) {
    try {
      const updated = await toggleUserStatus(inv.id);
      loadUsers();
      if (updated?.is_active) {
        setSuccessMsg(`Account "${inv.username}" reactivated. Investigator can now sign in.`);
      } else {
        setSuccessMsg(`Account "${inv.username}" disabled. Login access has been immediately revoked.`);
      }
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to toggle status');
    }
  }

  const filteredInvestigators = investigators.filter((inv) => {
    if (!searchTerm) return true;
    const q = searchTerm.toLowerCase();
    return (
      (inv.full_name && inv.full_name.toLowerCase().includes(q)) ||
      (inv.username && inv.username.toLowerCase().includes(q)) ||
      (inv.email && inv.email.toLowerCase().includes(q))
    );
  });

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
      subtitle="Authorized Admin Console: Provision, monitor, and manage field audit personnel"
    >
      <div className="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <p className="text-sm text-muted">
            Provision and control official investigator accounts. Deactivating an account revokes login access immediately.
          </p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="rounded-lg bg-navy-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-navy-700 transition self-start sm:self-auto flex items-center gap-1.5"
        >
          <span>+</span> Provision New Investigator
        </button>
      </div>

      {successMsg && (
        <div className="mb-4 rounded-lg bg-emerald-50 border border-emerald-200 p-3 text-xs text-emerald-800 flex justify-between items-center">
          <span>✅ {successMsg}</span>
          <button onClick={() => setSuccessMsg(null)} className="font-bold text-emerald-900 hover:text-black ml-2">✕</button>
        </div>
      )}

      {/* Quick Search Box */}
      <div className="mb-4 flex items-center justify-between gap-4">
        <div className="relative w-full max-w-sm">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by name, username, or email…"
            className="w-full rounded-lg border border-border bg-white px-3.5 py-2 text-xs text-ink placeholder:text-muted outline-none focus:border-navy-600 shadow-sm"
          />
        </div>
        <span className="text-xs text-muted font-medium">
          Showing {filteredInvestigators.length} of {investigators.length} personnel
        </span>
      </div>

      {loading && <EmptyState title="Loading investigators..." />}
      {error && <EmptyState tone="error" title="Error" description={error} />}

      {!loading && (
        <div className="overflow-hidden rounded-xl border border-border bg-white shadow-card">
          <div className="max-h-[600px] overflow-y-auto">
            <table className="w-full border-collapse text-left text-sm">
              <thead className="sticky top-0 z-10 bg-navy-50">
                <tr className="border-b border-border text-xs font-semibold uppercase tracking-wider text-navy-800">
                  <th className="px-5 py-3.5">Officer Name</th>
                  <th className="px-5 py-3.5">Username</th>
                  <th className="px-5 py-3.5">Official Email</th>
                  <th className="px-5 py-3.5">Role</th>
                  <th className="px-5 py-3.5">Account Status</th>
                  <th className="px-5 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filteredInvestigators.map((inv) => (
                  <tr key={inv.id} className="hover:bg-navy-50/50 transition">
                    <td className="px-5 py-3.5 font-medium text-ink">
                      <div>
                        <p>{inv.full_name || inv.name || '—'}</p>
                        {inv.designation && <p className="text-[11px] text-muted">{inv.designation}</p>}
                      </div>
                    </td>
                    <td className="px-5 py-3.5 font-mono text-xs text-muted">{inv.username}</td>
                    <td className="px-5 py-3.5 text-xs text-ink">{inv.email}</td>
                    <td className="px-5 py-3.5">
                      <span className="inline-flex rounded bg-navy-100 px-2.5 py-0.5 text-[11px] font-semibold text-navy-800 uppercase tracking-wider">
                        {inv.role}
                      </span>
                    </td>
                    <td className="px-5 py-3.5">
                      <span
                        className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-bold ${
                          inv.is_active
                            ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                            : 'bg-rose-100 text-rose-800 border border-rose-300'
                        }`}
                      >
                        <span className={`h-1.5 w-1.5 rounded-full ${inv.is_active ? 'bg-emerald-600' : 'bg-rose-600'}`} />
                        {inv.is_active ? 'Active' : 'Disabled'}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <button
                        onClick={() => handleToggle(inv)}
                        className={`rounded px-3 py-1 text-xs font-bold shadow-sm transition ${
                          inv.is_active
                            ? 'border border-rose-300 bg-rose-50 text-rose-700 hover:bg-rose-100'
                            : 'border border-emerald-300 bg-emerald-50 text-emerald-700 hover:bg-emerald-100'
                        }`}
                      >
                        {inv.is_active ? 'Disable Account' : 'Reactivate Account'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
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
