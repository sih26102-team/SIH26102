import { useEffect, useState } from 'react';
import AppLayout from '../components/AppLayout';
import TrendChart from '../components/TrendChart';
import FlaggedMap from '../components/FlaggedMap';
import { fetchTrend, fetchFlaggedWorks } from '../services/worksService';

export default function InsightsPage() {
  const [trend, setTrend] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    Promise.all([fetchTrend(), fetchFlaggedWorks()])
      .then(([trendData, projectData]) => {
        if (cancelled) return;
        setTrend(trendData);
        setProjects(projectData);
      })
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <AppLayout title="Insights" subtitle="Trend and geographic view across flagged projects">
      <div className="space-y-6">
        <TrendChart data={trend} loading={loading} />
        <FlaggedMap projects={projects} loading={loading} />
      </div>
    </AppLayout>
  );
}
