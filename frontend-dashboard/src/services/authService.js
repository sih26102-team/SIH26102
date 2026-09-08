import { api, USE_MOCK, mockDelay } from './api';

export async function login(username, password) {
  if (USE_MOCK) {
    await mockDelay(500);
    if (!username || !password) {
      const err = new Error('Username and password are required');
      err.code = 'VALIDATION';
      throw err;
    }
    return {
      accessToken: `mock-token-${btoa(username)}`,
      user: {
        name: username,
        role: 'Audit & Investigation Personnel',
      },
    };
  }

  const { data } = await api.post('/auth/login', { username, password });
  return {
    accessToken: data.access_token,
    user: data.user,
  };
}

export function logout() {
  localStorage.removeItem('mplads_token');
  localStorage.removeItem('mplads_user');
}
