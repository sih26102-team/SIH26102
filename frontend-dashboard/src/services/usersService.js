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

export async function fetchUsers(role = null) {
  if (USE_MOCK) {
    await mockDelay(250);
    return role ? mockUsers.filter((u) => u.role === role) : mockUsers;
  }
  try {
    const { data } = await api.get('/users/', { params: role ? { role } : {} });
    return data;
  } catch (err) {
    console.warn('API /users/ fetch failed, falling back to mock users:', err.message);
    return mockUsers;
  }
}

export async function createInvestigator(userData) {
  if (USE_MOCK) {
    await mockDelay(350);
    const newUser = {
      id: mockUsers.length + 1,
      username: userData.username,
      email: userData.email,
      full_name: userData.full_name || userData.username,
      role: 'investigator',
      is_active: true,
      created_at: new Date().toISOString()
    };
    mockUsers.push(newUser);
    return newUser;
  }
  const { data } = await api.post('/users/', userData);
  return data;
}

export async function toggleUserStatus(userId) {
  if (USE_MOCK) {
    await mockDelay(200);
    const user = mockUsers.find((u) => u.id === Number(userId));
    if (user) {
      user.is_active = !user.is_active;
    }
    return user;
  }
  const { data } = await api.patch(`/users/${userId}/toggle-status`);
  return data;
}
