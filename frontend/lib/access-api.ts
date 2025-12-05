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

export const accessApi = {
  verify: (email: string) =>
    apiFetch<AccessVerifyResponse>(`/api/access/verify?email=${encodeURIComponent(email)}`),

  requestAccess: (data: AccessRequestCreate) =>
    apiFetch<AccessRequest>('/api/access/request', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  listRequests: (status?: AccessRequestStatus) => {
    const qs = status ? `?status=${status}` : '';
    return apiFetch<AccessRequestListResponse>(`/api/access/requests${qs}`);
  },

  approveRequest: (requestId: string, reviewerEmail: string, role: UserRole = 'user') =>
    apiFetch<{ request: AccessRequest; user: AllowedUser }>(
      `/api/access/requests/${requestId}/approve?reviewer_email=${encodeURIComponent(reviewerEmail)}&role=${role}`,
      { method: 'POST' }
    ),

  denyRequest: (requestId: string, reviewerEmail: string) =>
    apiFetch<AccessRequest>(
      `/api/access/requests/${requestId}/deny?reviewer_email=${encodeURIComponent(reviewerEmail)}`,
      { method: 'POST' }
    ),

  listUsers: (role?: UserRole, status?: UserStatus) => {
    const params = new URLSearchParams();
    if (role) params.append('role', role);
    if (status) params.append('status', status);
    const qs = params.toString();
    return apiFetch<AllowedUserListResponse>(`/api/access/users${qs ? `?${qs}` : ''}`);
  },

  createUser: (data: AllowedUserCreate, approverEmail: string) =>
    apiFetch<AllowedUser>(`/api/access/users?approver_email=${encodeURIComponent(approverEmail)}`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateUser: (userId: string, data: Partial<AllowedUserCreate & { status?: UserStatus }>) =>
    apiFetch<AllowedUser>(`/api/access/users/${userId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  deleteUser: (userId: string) =>
    apiFetch<{ message: string }>(`/api/access/users/${userId}`, {
      method: 'DELETE',
    }),

  getPendingCount: () =>
    apiFetch<{ count: number }>('/api/access/pending-count'),

  seedAdmins: () =>
    apiFetch<{ message: string; users?: string[] }>('/api/access/seed-admins', {
      method: 'POST',
    }),
};
