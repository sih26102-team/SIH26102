import axios from 'axios';

/**
 * Single axios instance for talking to backend-data-api (Mokshagna) and
 * backend-case-management (Poornesh). Both are expected to sit behind the
 * same gateway/base URL per docker-compose - update VITE_API_BASE_URL in
 * .env if that changes.
 */
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
});

// Attach the JWT (see hooks/useAuth.js) to every outgoing request.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('mplads_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// A 401 from either backend means the token expired or was rejected -
// clear it and let ProtectedRoute bounce the user back to /login.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('mplads_token');
      localStorage.removeItem('mplads_user');
    }
    return Promise.reject(error);
  }
);

/**
 * USE_MOCK controls whether services read from the in-browser synthetic
 * dataset (utils/mockData.js) or hit the real FastAPI backends. Default is
 * true so the frontend runs standalone before the other four modules are
 * wired up. Flip VITE_USE_MOCK=false in .env once backend-data-api and
 * backend-case-management are reachable.
 */
export const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false';

// Small helper so mock services can simulate realistic network latency
// instead of resolving instantly, which hides loading-state bugs.
export function mockDelay(ms = 350) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
