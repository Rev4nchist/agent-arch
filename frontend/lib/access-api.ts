const API_URL = process.env.NEXT_PUBLIC_API_URL || '';
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || 'dev-test-key-123';

export type UserRole = 'admin' | 'user';
export type UserStatus = 'active' | 'pending' | 'denied';
export type AccessRequestStatus = 'pending' | 'approved' | 'denied';

export interface AllowedUser {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  status: UserStatus;
  approved_by?: string;
  approved_at?: string;
  created_at: string;
}

export interface AccessRequest {
  id: string;
  email: string;
  name: string;
  reason?: string;
  status: AccessRequestStatus;
  reviewed_by?: string;
  reviewed_at?: string;
  created_at: string;
}

export interface AccessVerifyResponse {
  authorized: boolean;
  role?: UserRole;
  user_id?: string;
  name?: string;
}

export interface AllowedUserCreate {
  email: string;
  name: string;
  role?: UserRole;
}

export interface AccessRequestCreate {
  email: string;
  name: string;
  reason?: string;
}

export interface AllowedUserListResponse {
  items: AllowedUser[];
  total: number;
}

export interface AccessRequestListResponse {
  items: AccessRequest[];
  total: number;
}

async function apiFetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`,
      ...options?.headers,
    },
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.statusText}`);
  }

  return res.json();
}

async function adminApiFetch<T>(endpoint: string, userEmail: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`,
      'X-User-Email': userEmail,
      ...options?.headers,
    },
  });

  if (!res.ok) {
    const errorText = await res.text().catch(() => res.statusText);
    throw new Error(`API error: ${errorText}`);
  }

  return res.json();
}

export const accessApi = {
  verify: (email: string) =>
    apiFetch<AccessVerifyResponse>(`/api/access/verify?email=${encodeURIComponent(email)}`),

  requestAccess: (data: AccessRequestCreate) =>
    apiFetch<AccessRequest>('/api/access/request', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  listRequests: (adminEmail: string, status?: AccessRequestStatus) => {
    const qs = status ? `?status=${status}` : '';
    return adminApiFetch<AccessRequestListResponse>(`/api/access/requests${qs}`, adminEmail);
  },

  approveRequest: (requestId: string, adminEmail: string, role: UserRole = 'user') =>
    adminApiFetch<{ request: AccessRequest; user: AllowedUser }>(
      `/api/access/requests/${requestId}/approve?role=${role}`,
      adminEmail,
      { method: 'POST' }
    ),

  denyRequest: (requestId: string, adminEmail: string) =>
    adminApiFetch<AccessRequest>(
      `/api/access/requests/${requestId}/deny`,
      adminEmail,
      { method: 'POST' }
    ),

  listUsers: (adminEmail: string, role?: UserRole, status?: UserStatus) => {
    const params = new URLSearchParams();
    if (role) params.append('role', role);
    if (status) params.append('status', status);
    const qs = params.toString();
    return adminApiFetch<AllowedUserListResponse>(`/api/access/users${qs ? `?${qs}` : ''}`, adminEmail);
  },

  createUser: (data: AllowedUserCreate, adminEmail: string) =>
    adminApiFetch<AllowedUser>('/api/access/users', adminEmail, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateUser: (userId: string, data: Partial<AllowedUserCreate & { status?: UserStatus }>, adminEmail: string) =>
    adminApiFetch<AllowedUser>(`/api/access/users/${userId}`, adminEmail, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  deleteUser: (userId: string, adminEmail: string) =>
    adminApiFetch<{ message: string }>(`/api/access/users/${userId}`, adminEmail, {
      method: 'DELETE',
    }),

  getPendingCount: (adminEmail: string) =>
    adminApiFetch<{ count: number }>('/api/access/pending-count', adminEmail),

  seedAdmins: (adminEmail: string) =>
    adminApiFetch<{ message: string; users?: string[] }>('/api/access/seed-admins', adminEmail, {
      method: 'POST',
    }),
};
