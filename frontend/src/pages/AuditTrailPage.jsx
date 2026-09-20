import { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function AuditTrailPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/audit-logs')
      .then(res => {
        setLogs(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-8 text-center text-gray-500">Loading immutable audit trail...</div>;

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">System Audit Trail</h1>
      <p className="mb-6 text-gray-600">This log is mathematically immutable and strictly append-only. Only authorized authorities can view this page.</p>

      <div className="bg-white shadow rounded-lg overflow-hidden">
        <table className="min-w-full leading-normal">
          <thead>
            <tr>
              <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Timestamp</th>
              <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Actor ID</th>
              <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Action</th>
              <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Target Entity</th>
              <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Metadata / Details</th>
            </tr>
          </thead>
          <tbody>
            {logs.map(log => (
              <tr key={log.audit_id}>
                <td className="px-5 py-3 border-b border-gray-200 text-sm">{new Date(log.timestamp).toLocaleString()}</td>
                <td className="px-5 py-3 border-b border-gray-200 text-sm font-semibold">{log.actor_user_id || 'SYSTEM'}</td>
                <td className="px-5 py-3 border-b border-gray-200 text-sm">
                  <span className="px-2 py-1 bg-gray-200 text-gray-800 rounded font-bold text-xs">{log.action}</span>
                </td>
                <td className="px-5 py-3 border-b border-gray-200 text-sm">{log.entity_type} {log.entity_id}</td>
                <td className="px-5 py-3 border-b border-gray-200 text-sm text-gray-600 truncate max-w-xs">{log.metadata_json}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {logs.length === 0 && <div className="p-8 text-center text-gray-500">No audit events found.</div>}
      </div>
    </div>
  );
}
