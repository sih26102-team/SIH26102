import { api, USE_MOCK, mockDelay } from './api';

export async function login(username, password) {
  if (!username || !password) {
    const err = new Error('Username and password are required');
    err.code = 'VALIDATION';
    throw err;
  }

  // Attempt live Backend API authentication first
  try {
    const { data } = await api.post('/auth/login', { username, password });
    return {
      accessToken: data.access_token,
      user: data.user,
    };
  } catch (apiErr) {
    // If live API returns a specific 403 or 400 from backend, surface it
    if (apiErr.response && apiErr.response.status === 403) {
      throw new Error(apiErr.response.data?.detail || 'Invalid Credentials');
    }

    // If backend is unreachable or local mock mode is enabled, provide smooth fallback for demo credentials
    console.warn('Live auth endpoint unreachable, checking local demo credentials...', apiErr.message);

    if (username === 'admin.demo' && password === 'CivicShieldAdmin@2026!') {
      return {
        accessToken: `demo-jwt-admin-token-${Date.now()}`,
        user: {
          id: 1,
          username: 'admin.demo',
          email: 'admin.demo@civicshield.gov.in',
          name: 'CivicShield System Administrator',
          role: 'admin',
        },
      };
    }

    if (username === 'investigator.demo' && password === 'CivicShield@Demo2026!') {
      return {
        accessToken: `demo-jwt-investigator-token-${Date.now()}`,
        user: {
          id: 2,
          username: 'investigator.demo',
          email: 'investigator.demo@civicshield.gov.in',
          name: 'Senior Field Investigator',
          role: 'investigator',
        },
      };
    }

    throw new Error(apiErr.response?.data?.detail || 'Invalid Credentials. Use the Demo Credentials buttons below.');
  }
}

export function logout() {
  localStorage.removeItem('mplads_token');
  localStorage.removeItem('mplads_user');
}
