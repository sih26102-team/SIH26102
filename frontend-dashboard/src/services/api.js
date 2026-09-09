import axios from 'axios';

const rawBaseUrl = import.meta.env.VITE_API_BASE_URL;
const baseURL = rawBaseUrl === '/' || !rawBaseUrl ? '' : rawBaseUrl;

export const api = axios.create({
  baseURL,
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

export const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

// Mock delay helper
export function mockDelay(ms = 350) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
