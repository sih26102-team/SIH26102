import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth.jsx';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import InsightsPage from './pages/InsightsPage';
import ProjectDetailPage from './pages/ProjectDetailPage';
import CasesPage from './pages/CasesPage';
import InvestigatorManagementPage from './pages/InvestigatorManagementPage';
import NotFoundPage from './pages/NotFoundPage';
import { ToastProvider, useToast } from './contexts/ToastContext';
import apiClient from './services/apiClient';
import { useEffect } from 'react';

function AxiosInterceptor() {
  const { showToast } = useToast();
  
  useEffect(() => {
    const interceptor = apiClient.interceptors.response.use(
      response => response,
      error => {
        if (error.response) {
            const status = error.response.status;
            let msg = error.response.data?.detail || "An unexpected error occurred.";
            if (status === 401) msg = "Your session is invalid or has expired.";
            if (status === 403) msg = "You do not have permission to perform this action.";
            if (status >= 500) msg = "The server encountered an error. Please try again later.";
            showToast(msg, 'error');
        } else {
            showToast("Network error. Please check your connection.", 'error');
        }
        return Promise.reject(error);
      }
    );
    return () => apiClient.interceptors.response.eject(interceptor);
  }, [showToast]);

  return null;
}

export default function App() {
  return (
    <ToastProvider>
      <AxiosInterceptor />
      <AuthProvider>
        <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/login" element={<LoginPage />} />

          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/insights"
            element={
              <ProtectedRoute>
                <InsightsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects/:projectId"
            element={
              <ProtectedRoute>
                <ProjectDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/cases"
            element={
              <ProtectedRoute>
                <CasesPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/investigators"
            element={
              <ProtectedRoute>
                <InvestigatorManagementPage />
              </ProtectedRoute>
            }
          />

          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
    </ToastProvider>
  );
}
