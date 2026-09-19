import { useToast } from '../contexts/ToastContext';
import { useState } from 'react';
import apiClient from '../services/apiClient';

export default function InspectionForm({ caseId, project, risk }) {
  const { showToast } = useToast();
  const [checklist, setChecklist] = useState({
    locationVerified: false,
    physicalWorkExists: false,
    progressVerified: false,
    consistentProgress: false,
    recordsAvailable: false,
    implementationStatusVerified: false,
    photographCaptured: false,
    locationCaptured: false,
    observationsRecorded: false
  });

  const [observations, setObservations] = useState({
    physicalProgressObserved: '',
    siteCondition: '',
    financialObservation: '',
    generalObservation: '',
    recommendation: ''
  });

  const [photo, setPhoto] = useState(null);
  const [location, setLocation] = useState({ lat: 0, lng: 0, timestamp: null });

  const captureLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((pos) => {
        setLocation({
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
          timestamp: new Date().toISOString()
        });
        setChecklist(prev => ({ ...prev, locationCaptured: true }));
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('latitude', location.lat);
    formData.append('longitude', location.lng);
    formData.append('physical_progress_observed', observations.physicalProgressObserved || 0);
    formData.append('site_condition', observations.siteCondition);
    formData.append('financial_observation', observations.financialObservation);
    formData.append('general_observation', observations.generalObservation);
    formData.append('recommendation', observations.recommendation);
    formData.append('checklist', JSON.stringify(checklist));
    if (photo) formData.append('photo', photo);

    try {
      await apiClient.post(`/inspections/${caseId}/submit`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      showToast("Evidence successfully submitted!");
      window.location.reload();
    } catch (err) {
      console.error(err);
      showToast("Failed to submit inspection.");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-6 bg-white rounded shadow-md mt-8">
      <h2 className="text-2xl font-bold mb-4">Field Inspection Report</h2>
      
      {/* 1. AI Risk & Verifications */}
      <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 rounded">
        <h3 className="font-bold text-red-700">AI Risk Reasons</h3>
        <ul className="list-disc ml-5 text-sm text-red-600 mb-4">
          {risk?.reasons?.map((r, i) => <li key={i}>{r}</li>)}
        </ul>
        <h3 className="font-bold text-red-700">Recommended Verification</h3>
        <ul className="list-disc ml-5 text-sm text-red-600">
          {risk?.recommended_verification?.map((r, i) => <li key={i}>{r}</li>)}
        </ul>
      </div>

      {/* 2. Checklist */}
      <div className="mb-6">
        <h3 className="font-bold mb-2">Inspection Checklist</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {Object.keys(checklist).map(key => (
            <label key={key} className="flex items-center space-x-2">
              <input type="checkbox" checked={checklist[key]} onChange={(e) => setChecklist(prev => ({...prev, [key]: e.target.checked}))} />
              <span className="text-sm">{key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}</span>
            </label>
          ))}
        </div>
      </div>

      {/* 3. Location & Photo */}
      <div className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <h3 className="font-bold mb-2">Location Capture</h3>
          <button type="button" onClick={captureLocation} className="px-4 py-2 bg-blue-100 text-blue-700 rounded hover:bg-blue-200">
            Capture GPS Coordinates
          </button>
          {location.timestamp && (
            <p className="text-xs text-gray-500 mt-2">Lat: {location.lat}, Lng: {location.lng}</p>
          )}
        </div>
        <div>
          <h3 className="font-bold mb-2">Photo Upload</h3>
          <input type="file" accept="image/*" onChange={e => {
            setPhoto(e.target.files[0]);
            setChecklist(prev => ({ ...prev, photographCaptured: true }));
          }} className="text-sm" />
        </div>
      </div>

      {/* 4. Structured Observations */}
      <div className="mb-6 space-y-4">
        <h3 className="font-bold">Structured Observations</h3>
        <div>
          <label className="block text-sm font-semibold text-gray-700">Physical Progress Observed (%)</label>
          <input type="number" min="0" max="100" value={observations.physicalProgressObserved} onChange={e => setObservations({...observations, physicalProgressObserved: e.target.value})} className="w-full border rounded p-2" required />
        </div>
        <div>
          <label className="block text-sm font-semibold text-gray-700">Site Condition</label>
          <textarea value={observations.siteCondition} onChange={e => setObservations({...observations, siteCondition: e.target.value})} className="w-full border rounded p-2" required></textarea>
        </div>
        <div>
          <label className="block text-sm font-semibold text-gray-700">Financial Observation</label>
          <textarea value={observations.financialObservation} onChange={e => setObservations({...observations, financialObservation: e.target.value})} className="w-full border rounded p-2" required></textarea>
        </div>
        <div>
          <label className="block text-sm font-semibold text-gray-700">General Observation</label>
          <textarea value={observations.generalObservation} onChange={e => setObservations({...observations, generalObservation: e.target.value})} className="w-full border rounded p-2" required></textarea>
        </div>
        <div>
          <label className="block text-sm font-semibold text-gray-700">Recommendation</label>
          <textarea value={observations.recommendation} onChange={e => setObservations({...observations, recommendation: e.target.value})} className="w-full border rounded p-2" required></textarea>
        </div>
      </div>

      <button type="submit" className="w-full py-3 bg-green-600 text-white font-bold rounded shadow hover:bg-green-700">
        Submit Evidence
      </button>
    </form>
  );
}
