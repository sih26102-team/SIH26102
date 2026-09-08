import axios from 'axios';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('mplads_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

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

export const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false';


// instead of resolving instantly, which hides loading-state bugs.
export function mockDelay(ms = 350) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
