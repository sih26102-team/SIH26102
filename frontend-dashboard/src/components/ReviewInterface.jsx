import { useToast } from '../contexts/ToastContext';
import { useState, useEffect } from 'react';
import apiClient from '../services/apiClient';

export default function ReviewInterface({ caseId }) {
  const { showToast } = useToast();
  const [data, setData] = useState(null);
  const [resolutionNote, setResolutionNote] = useState('');
  
  useEffect(() => {
    apiClient.get(`/cases/${caseId}`).then(res => setData(res.data)).catch(console.error);
  }, [caseId]);

  const handleReview = async (status) => {
    try {
      await apiClient.post(`/cases/${caseId}/review`, { status, resolution: resolutionNote });
      showToast(`Case successfully marked as ${status}`);
      window.location.reload();
    } catch (err) {
      showToast("Failed to record review decision.");
    }
  };

  if (!data) return <div>Loading review data...</div>;

  const latestInspection = data.inspections?.[0];

  return (
    <div className="mt-8 p-6 bg-white rounded shadow-md border-t-4 border-indigo-600">
      <h2 className="text-2xl font-bold mb-4 text-indigo-900">District Authority Case Review</h2>
      
      {/* 1. Original AI Assessment */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="p-4 bg-gray-50 rounded border">
          <h3 className="font-bold border-b pb-2 mb-2">Original AI Assessment</h3>
          <p><strong>Score:</strong> {data.risk_result?.risk_score} / 100</p>
          <p><strong>Level:</strong> {data.risk_result?.risk_level}</p>
          <div className="mt-2 text-sm text-gray-700">
            <strong>Reasons:</strong>
            <ul className="list-disc ml-4">
              {data.risk_result?.reasons?.map((r, i) => <li key={i}>{r}</li>)}
            </ul>
          </div>
          <div className="mt-2 text-sm text-gray-700">
            <strong>Recommended Verification:</strong>
            <ul className="list-disc ml-4">
              {data.risk_result?.recommended_verification?.map((r, i) => <li key={i}>{r}</li>)}
            </ul>
          </div>
        </div>

        {/* 2. Field Evidence & Observations */}
        <div className="p-4 bg-blue-50 rounded border">
          <h3 className="font-bold border-b pb-2 mb-2">Field Evidence & Observations</h3>
          {latestInspection ? (
            <div className="text-sm space-y-2">
              <p><strong>Date:</strong> {new Date(latestInspection.inspection_date).toLocaleString()}</p>
              <p><strong>Physical Progress:</strong> {latestInspection.physical_progress_observed}%</p>
              <p><strong>Site Condition:</strong> {latestInspection.site_condition}</p>
              <p><strong>Financial Observation:</strong> {latestInspection.financial_observation}</p>
              <p><strong>General Observation:</strong> {latestInspection.general_observation}</p>
              <p><strong>Recommendation:</strong> {latestInspection.recommendation}</p>
              <p><strong>Location:</strong> {latestInspection.latitude}, {latestInspection.longitude}</p>
              <div className="mt-4">
                <strong>Checklist Verified:</strong>
                <pre className="text-xs bg-white p-2 mt-1 rounded overflow-x-auto">
                  {JSON.stringify(JSON.parse(latestInspection.checklist_responses), null, 2)}
                </pre>
              </div>
            </div>
          ) : <p className="text-gray-500 text-sm">No field inspection submitted yet.</p>}
        </div>
      </div>

      {/* 3. Append-only History */}
      <div className="mb-6 p-4 border rounded bg-gray-50">
        <h3 className="font-bold mb-2">Append-Only Inspection History</h3>
        <div className="max-h-40 overflow-y-auto text-sm space-y-2">
          {data.inspections?.map((insp, idx) => (
            <div key={idx} className="p-2 bg-white border rounded">
              <span className="font-semibold">{new Date(insp.inspection_date).toLocaleString()}</span> - Officer ID {insp.officer_id} - {insp.recommendation}
            </div>
          ))}
          {(!data.inspections || data.inspections.length === 0) && <span className="text-gray-500">No history available.</span>}
        </div>
      </div>

      {/* 4. Decision Action */}
      {data.case.status === 'EVIDENCE_SUBMITTED' ? (
        <div className="p-4 bg-indigo-50 border border-indigo-200 rounded">
          <h3 className="font-bold text-indigo-900 mb-2">Authority Decision</h3>
          <textarea 
            className="w-full p-2 border rounded mb-4" 
            placeholder="Enter resolution notes or escalation reasoning..."
            value={resolutionNote}
            onChange={(e) => setResolutionNote(e.target.value)}
          ></textarea>
          <div className="flex space-x-4">
            <button onClick={() => handleReview('VERIFIED')} className="px-6 py-2 bg-green-600 text-white rounded font-bold hover:bg-green-700">VERIFIED / RESOLVED</button>
            <button onClick={() => handleReview('ACTION_REQUIRED')} className="px-6 py-2 bg-red-600 text-white rounded font-bold hover:bg-red-700">ACTION REQUIRED / ESCALATED</button>
          </div>
        </div>
      ) : (
        <div className="p-4 bg-gray-200 rounded text-center text-gray-700 font-bold">
          Case Status: {data.case.status} - {data.case.resolution}
        </div>
      )}
    </div>
  );
}
