import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import apiClient from '../services/apiClient';

function AnalyticsCards({ summary }) {
  if (!summary) return <div>Loading summary...</div>;
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      <div className="p-4 bg-white rounded shadow-md border-l-4 border-blue-500">
        <h3 className="text-gray-500 text-sm">Total Projects</h3>
        <p className="text-2xl font-bold">{summary.total_projects}</p>
      </div>
      <div className="p-4 bg-white rounded shadow-md border-l-4 border-green-500">
        <h3 className="text-gray-500 text-sm">Total Sanctioned Amount</h3>
        <p className="text-2xl font-bold">₹{(summary.total_budget / 10000000).toFixed(2)} Cr</p>
      </div>
      <div className="p-4 bg-white rounded shadow-md border-l-4 border-orange-500">
        <h3 className="text-gray-500 text-sm">Stalled Projects</h3>
        <p className="text-2xl font-bold">{summary.status_breakdown?.stalled || 0}</p>
      </div>
    </div>
  );
}

function RoleSpecificView({ role, summary, trends }) {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (role === 'INSPECTION_OFFICER') {
      setLoading(true);
      apiClient.get('/cases')
        .then(res => setCases(res.data))
        .catch(console.error)
        .finally(() => setLoading(false));
    }
  }, [role]);

  if (role === 'INSPECTION_OFFICER') {
    return (
      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-4 text-blue-800">New Assignments</h2>
        
        {loading ? (
          <div className="p-8 bg-gray-100 rounded text-center text-gray-500 shadow-inner">
             Loading assignments...
          </div>
        ) : cases.length === 0 ? (
          <div className="p-8 bg-gray-100 rounded text-center text-gray-500 shadow-inner">
            You currently have no new assignments.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {cases.map((c) => (
              <div key={c.case_id} className="p-6 bg-white rounded shadow-md border-l-4 border-blue-500 hover:shadow-lg transition">
                <div className="flex justify-between items-center mb-2">
                  <h3 className="font-bold text-lg text-gray-800">{c.project_id}</h3>
                  <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs font-semibold">{c.status}</span>
                </div>
                <p className="text-sm text-gray-600 mb-4">You have been assigned to inspect this flagged project.</p>
                <div className="flex space-x-2">
                  <button className="px-4 py-2 bg-blue-600 text-white rounded text-sm font-semibold hover:bg-blue-700">Accept Assignment</button>
                  <button className="px-4 py-2 border border-gray-300 rounded text-sm font-semibold hover:bg-gray-50">View Details</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  const roleTitle = 
    role === 'MINISTRY' ? 'National Overview' :
    role === 'STATE_AUTHORITY' ? 'State-Specific Overview' :
    role === 'DISTRICT_AUTHORITY' ? 'District-Specific Overview' : 'Overview';

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">{roleTitle}</h2>
      <AnalyticsCards summary={summary} />
      
      {/* Trend Chart Placeholder */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white p-4 rounded shadow-md">
          <h3 className="font-semibold text-gray-700 mb-4">Project Categories Trend</h3>
          <ul className="space-y-2">
            {trends && trends.map(t => (
              <li key={t.category} className="flex justify-between border-b pb-1">
                <span>{t.category}</span>
                <span className="font-bold">{t.count}</span>
              </li>
            ))}
          </ul>
        </div>
        
        {/* Leaflet Map Placeholder */}
        <div className="bg-white p-4 rounded shadow-md flex items-center justify-center min-h-[300px] text-gray-400">
          [ Leaflet Map Component Placeholder ]
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [summary, setSummary] = useState(null);
  const [trends, setTrends] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user && user.role !== 'INSPECTION_OFFICER') {
      setLoading(true);
      Promise.all([
        apiClient.get('/analytics/summary').then(res => setSummary(res.data)),
        apiClient.get('/analytics/trends').then(res => setTrends(res.data))
      ]).finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [user]);

  if (!user) return null;

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-display font-bold text-gray-800">Welcome, {user.username}</h1>
        <p className="text-gray-500">Role: <span className="font-semibold text-blue-600">{user.role}</span></p>
      </div>
      
      {loading ? (
        <div className="flex justify-center p-12 text-gray-500">
           <svg className="animate-spin h-8 w-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg>
        </div>
      ) : (
        <RoleSpecificView role={user.role} summary={summary} trends={trends} />
      )}
    </div>
  );
}
