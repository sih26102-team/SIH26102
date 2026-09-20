import { api, USE_MOCK, mockDelay } from './api';
import SEED_DATA from '../data/seed_accounts.json';

const initialAdmins = SEED_DATA.admins.map((a) => ({
  ...a,
  is_active: true,
  created_at: '2026-08-01T10:00:00Z'
}));

const initialInvestigators = SEED_DATA.investigators.map((inv, idx) => ({
  ...inv,
  is_active: idx % 12 !== 0, // majority active, few pending verification for realism
  created_at: new Date(Date.now() - (idx * 86400000 * 2)).toISOString()
}));

let mockUsers = [
  {
    id: 1,
    username: 'admin.demo',
    email: 'admin.demo@civicshield.gov.in',
    full_name: 'CivicShield System Administrator',
    designation: 'Chief Audit Officer',
    role: 'admin',
    is_active: true,
    created_at: '2026-08-01T10:00:00Z'
  },
  {
    id: 2,
    username: 'investigator.demo',
    email: 'investigator.demo@civicshield.gov.in',
    full_name: 'Senior Field Investigator',
    designation: 'Special Vigilance Officer',
    role: 'investigator',
    is_active: true,
    created_at: '2026-08-15T12:30:00Z'
  },
  ...initialAdmins,
  ...initialInvestigators
];

const STORAGE_KEY = 'civicshield_provisioned_users';

export function getUsersStore() {
  const stored = typeof window !== 'undefined' ? localStorage.getItem(STORAGE_KEY) : null;
  if (stored) {
    try {
      const parsed = JSON.parse(stored);
      if (Array.isArray(parsed) && parsed.length > 0) return parsed;
    } catch {
      // ignore parse errors
    }
  }
  return mockUsers;
}

export function saveUsersStore(users) {
  if (typeof window !== 'undefined') {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(users));
    } catch {
      // ignore storage full errors
    }
  }
}

export async function fetchUsers(role = null) {
  if (USE_MOCK) {
    await mockDelay(200);
    const store = getUsersStore();
    return role ? store.filter((u) => u.role === role) : store;
  }
  try {
    const { data } = await api.get('/users/', { params: role ? { role } : {} });
    if (Array.isArray(data) && data.length > 0) {
      return data;
    }
    const store = getUsersStore();
    return role ? store.filter((u) => u.role === role) : store;
  } catch (err) {
    console.warn('API /users/ fetch failed, loading provisioned users store:', err.message);
    const store = getUsersStore();
    return role ? store.filter((u) => u.role === role) : store;
  }
}

export async function createInvestigator(userData) {
  const store = getUsersStore();
  const newUser = {
    id: store.length + 100,
    username: userData.username.trim().toLowerCase(),
    email: userData.email.trim().toLowerCase(),
    full_name: userData.full_name || userData.username,
    designation: 'Field Investigation Officer',
    role: 'investigator',
    is_active: true,
    password: userData.password,
    created_at: new Date().toISOString()
  };

  try {
    const { data } = await api.post('/users/', userData);
    const merged = { ...newUser, ...data };
    const updatedStore = [merged, ...store.filter((u) => u.username !== merged.username)];
    saveUsersStore(updatedStore);
    return merged;
  } catch (err) {
    console.warn('API /users/ provision failed, saving locally:', err.message);
    const updatedStore = [newUser, ...store.filter((u) => u.username !== newUser.username)];
    saveUsersStore(updatedStore);
    return newUser;
  }
}

export async function toggleUserStatus(userId) {
  const store = getUsersStore();
  const user = store.find((u) => u.id === Number(userId) || u.username === String(userId));

  try {
    const { data } = await api.patch(`/users/${userId}/toggle-status`);
    if (user) {
      user.is_active = data.is_active;
      saveUsersStore([...store]);
    }
    return data;
  } catch (err) {
    console.warn('API /users/ toggle failed, applying locally:', err.message);
    if (user) {
      user.is_active = !user.is_active;
      saveUsersStore([...store]);
    }
    return user;
  }
}
