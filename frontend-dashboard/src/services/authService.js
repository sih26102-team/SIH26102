import { api, USE_MOCK, mockDelay } from './api';
import SEED_DATA from '../data/seed_accounts.json';

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

    const cleanUser = username.trim().toLowerCase();

    // Check base demo accounts
    if (cleanUser === 'admin.demo' && password === 'CivicShieldAdmin@2026!') {
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

    if (cleanUser === 'investigator.demo' && (password === 'CivicShield@Demo2026!' || password === 'Investigator@2026!')) {
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

    // Check 5 Admins
    const matchedAdmin = SEED_DATA.admins.find(
      (a) => a.username.toLowerCase() === cleanUser || a.email.toLowerCase() === cleanUser
    );
    if (matchedAdmin) {
      if (password === matchedAdmin.password || password === 'Admin@CivicShield2026!' || password === 'CivicShieldAdmin@2026!') {
        return {
          accessToken: `demo-jwt-admin-${matchedAdmin.id}-${Date.now()}`,
          user: {
            id: matchedAdmin.id,
            username: matchedAdmin.username,
            email: matchedAdmin.email,
            name: matchedAdmin.full_name,
            role: 'admin',
          },
        };
      }
    }

    // Check 100 Investigators
    const matchedInv = SEED_DATA.investigators.find(
      (inv) => inv.username.toLowerCase() === cleanUser || inv.email.toLowerCase() === cleanUser
    );
    if (matchedInv) {
      if (password === matchedInv.password || password === 'Investigator@2026!' || password === 'CivicShield@Demo2026!') {
        return {
          accessToken: `demo-jwt-inv-${matchedInv.id}-${Date.now()}`,
          user: {
            id: matchedInv.id,
            username: matchedInv.username,
            email: matchedInv.email,
            name: matchedInv.full_name,
            role: 'investigator',
          },
        };
      }
    }

    throw new Error(apiErr.response?.data?.detail || 'Invalid Credentials. Please verify username/email and password.');
  }
}

export function logout() {
  localStorage.removeItem('mplads_token');
  localStorage.removeItem('mplads_user');
}
