// Use empty string for relative URLs when running through reverse proxy
// Endpoints already include /api prefix
const API_URL = process.env.NEXT_PUBLIC_API_URL === undefined
  ? 'http://localhost:8001'  // Fallback for non-Docker dev
  : process.env.NEXT_PUBLIC_API_URL;  // Use env value (can be empty string for reverse proxy)
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || 'dev-test-key-123';

export interface Meeting {
  id: string;
  title: string;
  date: string;
  type: 'Governance' | 'AI Architect' | 'Licensing' | 'Technical' | 'Review';
  facilitator: string;
  attendees: string[];
  agenda?: string;
  status: 'Scheduled' | 'Completed' | 'Cancelled';
  transcript?: string;
  transcript_url?: string;
  transcript_text?: string;
  summary?: string;
  action_items?: string[];
  decisions?: string[];
  topics?: string[];
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: 'Pending' | 'In-Progress' | 'Done' | 'Blocked' | 'Deferred';
  priority: 'Critical' | 'High' | 'Medium' | 'Low';
  category?: 'Agent' | 'Governance' | 'Technical' | 'Licensing' | 'AI Architect';
  assigned_to?: string;
  due_date?: string;
  created_from_meeting?: string;
  related_agent?: string;
  dependencies: string[];
  notes?: string;
  complexity?: 'beginner' | 'intermediate' | 'advanced';
  learning_friendly?: boolean;
  skills_required?: string[];
  owner_name?: string;
  owner_contact?: string;
  team?: string;
  created_at: string;
  updated_at: string;
}

export type IntegrationStatus = 'Not Started' | 'In Progress' | 'Blocked' | 'Partially Integrated' | 'Fully Integrated' | 'Integration Issues';

export interface Agent {
  id: string;
  name: string;
  description: string;
  tier: 'Tier1_Individual' | 'Tier2_Department' | 'Tier3_Enterprise';
  status: 'Idea' | 'Design' | 'Development' | 'Testing' | 'Staging' | 'Production' | 'Deprecated';
  integration_status?: IntegrationStatus;
  owner: string;
  department?: string;
  data_sources: string[];
  use_case?: string;
  integration_notes?: string;
  related_tasks: string[];
  target_deployment_date?: string;
  deployment_blockers?: string[];
  next_milestone?: string;
  owner_contact?: string;
  team?: string;
  created_at: string;
  updated_at: string;
}

export interface Proposal {
  id: string;
  title: string;
  description: string;
  category: 'Agent' | 'Governance' | 'Technical' | 'Licensing' | 'AI Architect';
  status: 'Proposed' | 'Reviewing' | 'Agreed' | 'Deferred';
  proposer: string;
  department: string;
  team_member?: string;
  rationale?: string;
  impact?: string;
  created_at: string;
  updated_at: string;
}

export interface Decision {
  id: string;
  title: string;
  description: string;
  category: 'Governance' | 'Architecture' | 'Licensing' | 'Budget' | 'Security';
  decision_date: string;
  decision_maker: string;
  rationale?: string;
  impact?: string;
  meeting?: string;
  proposal_id?: string;
  created_at: string;
  updated_at: string;
}

export interface TranscriptUploadResponse {
  blob_url: string;
  file_name: string;
  file_size: number;
  upload_timestamp: string;
}

export interface TranscriptProcessResponse {
  meeting_id: string;
  summary: string;
  action_items: Array<{
    title: string;
    description?: string;
    assigned_to?: string;
    due_date?: string;
    priority: string;
  }>;
  decisions: Array<{
    title: string;
    description?: string;
    decision_maker?: string;
    category?: string;
    rationale?: string;
  }>;
  topics: string[];
  tasks_created: number;
  task_ids: string[];
  status: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: ChatSource[];
  data_basis?: DataBasis;
  suggestions?: ActionSuggestion[];  // Phase 5.4: Quick actions
  timestamp: Date;
}

export interface ChatSource {
  id: string;
  title: string;
  type: 'meeting' | 'task' | 'agent' | 'governance';
  snippet?: string;
}

export interface PageContext {
  current_page?: string;
  selected_ids?: string[];
  active_filters?: Record<string, string>;
  visible_entity_type?: string;
}

export interface GuideQueryRequest {
  query: string;
  context?: string;
  page_context?: PageContext;
  conversation_history?: Array<{ role: string; content: string }>;
  session_id?: string;  // Phase 5.2: Session-based conversation memory
}

export interface DataBasis {
  items_shown: number;
  total_items: number;
  entity_types: string[];
}

// Phase 5.4: Quick action suggestions
export interface ActionSuggestion {
  label: string;
  action_type: 'query' | 'filter' | 'navigate' | 'create' | 'export' | 'show_detail';
  params: Record<string, string | number | undefined>;
}

export interface GuideQueryResponse {
  response: string;
  sources: string[];
  data_basis?: DataBasis;
  suggestions?: ActionSuggestion[];  // Phase 5.4
  intent?: string;
  confidence?: string;
}

// Phase 5.3: Proactive insights
export interface InsightItem {
  id: string;
  type: 'warning' | 'info' | 'action';
  title: string;
  description: string;
  count?: number;
  action_label?: string;
  action_query?: string;
}

export interface InsightsResponse {
  page: string;
  insights: InsightItem[];
  generated_at: string;
}

export interface SearchResult {
  id: string;
  title: string;
  content: string;
  type: string;
  score: number;
  metadata?: Record<string, unknown>;
  status?: string;
  priority?: string;
  category?: string;
}

export type AuditAction = 'view' | 'create' | 'update' | 'delete' | 'query';
export type AuditEntityType = 'task' | 'agent' | 'meeting' | 'decision' | 'proposal' | 'resource' | 'tech_radar' | 'code_pattern';

export interface AuditLog {
  id: string;
  user_id: string;
  user_name?: string;
  action: AuditAction;
  entity_type: AuditEntityType;
  entity_id: string;
  entity_title?: string;
  timestamp: string;
  ip_address?: string;
  user_agent?: string;
  details?: Record<string, unknown>;
  old_value?: Record<string, unknown>;
  new_value?: Record<string, unknown>;
}

export interface AuditLogListResponse {
  items: AuditLog[];
  total: number;
  limit: number;
  offset: number;
}

export interface AuditSummary {
  total_logs: number;
  by_action: Record<string, number>;
  by_entity: Record<string, number>;
  by_user: Record<string, number>;
}

export interface AuditQueryParams {
  user_id?: string;
  entity_type?: AuditEntityType;
  entity_id?: string;
  action?: AuditAction;
  start_date?: string;
  end_date?: string;
  limit?: number;
  offset?: number;
}

async function apiFetch<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
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

export const api = {
  meetings: {
    list: () => apiFetch<Meeting[]>('/api/meetings'),
    get: (id: string) => apiFetch<Meeting>(`/api/meetings/${id}`),
    create: (data: Omit<Meeting, 'id' | 'created_at' | 'updated_at'>) =>
      apiFetch<Meeting>('/api/meetings', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },
  tasks: {
    list: () => apiFetch<Task[]>('/api/tasks'),
    get: (id: string) => apiFetch<Task>(`/api/tasks/${id}`),
    create: (data: Omit<Task, 'id' | 'created_at' | 'updated_at'>) =>
      apiFetch<Task>('/api/tasks', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    update: (id: string, data: Partial<Omit<Task, 'id' | 'created_at' | 'updated_at'>>) =>
      apiFetch<Task>(`/api/tasks/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
  },
  agents: {
    list: () => apiFetch<Agent[]>('/api/agents'),
    get: (id: string) => apiFetch<Agent>(`/api/agents/${id}`),
    create: (data: Omit<Agent, 'id' | 'created_at' | 'updated_at'>) =>
      apiFetch<Agent>('/api/agents', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },
  proposals: {
    list: () => apiFetch<Proposal[]>('/api/proposals'),
    get: (id: string) => apiFetch<Proposal>(`/api/proposals/${id}`),
    create: (data: Omit<Proposal, 'id' | 'created_at' | 'updated_at'>) =>
      apiFetch<Proposal>('/api/proposals', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    update: (id: string, data: Partial<Omit<Proposal, 'id' | 'created_at' | 'updated_at'>>) =>
      apiFetch<Proposal>(`/api/proposals/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
  },
  decisions: {
    list: () => apiFetch<Decision[]>('/api/decisions'),
    get: (id: string) => apiFetch<Decision>(`/api/decisions/${id}`),
    create: (data: Omit<Decision, 'id' | 'created_at' | 'updated_at'>) =>
      apiFetch<Decision>('/api/decisions', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    createFromProposal: (proposalId: string, data: Partial<Omit<Decision, 'id' | 'created_at' | 'updated_at' | 'proposal_id'>>) =>
      apiFetch<Decision>('/api/decisions/from-proposal', {
        method: 'POST',
        body: JSON.stringify({ proposal_id: proposalId, ...data }),
      }),
  },
  transcripts: {
    upload: async (file: File, meetingId?: string): Promise<TranscriptUploadResponse> => {
      const formData = new FormData();
      formData.append('file', file);
      if (meetingId) {
        formData.append('meeting_id', meetingId);
      }

      const res = await fetch(`${API_URL}/api/transcripts/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${API_KEY}`,
        },
        body: formData,
      });

      if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(error.detail || 'Upload failed');
      }

      return res.json();
    },
    process: (meetingId: string, blobUrl: string) =>
      apiFetch<TranscriptProcessResponse>('/api/transcripts/process', {
        method: 'POST',
        body: JSON.stringify({ meeting_id: meetingId, blob_url: blobUrl }),
      }),
  },
  health: () => apiFetch<{ status: string; environment: string }>('/health'),
  guide: {
    query: (query: string, context?: string, pageContext?: PageContext, sessionId?: string) =>
      apiFetch<GuideQueryResponse>('/api/agent/query', {
        method: 'POST',
        body: JSON.stringify({ query, context, page_context: pageContext, session_id: sessionId }),
      }),
    search: (query: string, docType?: string, top?: number) =>
      apiFetch<SearchResult[]>('/api/search', {
        method: 'POST',
        body: JSON.stringify({ query, doc_type: docType, top: top || 5 }),
      }),
    // Phase 5.3: Proactive insights
    getInsights: (page: string) =>
      apiFetch<InsightsResponse>(`/api/agent/insights?page=${encodeURIComponent(page)}`),
  },
  audit: {
    list: (params?: AuditQueryParams) => {
      const queryParams = new URLSearchParams();
      if (params?.user_id) queryParams.append('user_id', params.user_id);
      if (params?.entity_type) queryParams.append('entity_type', params.entity_type);
      if (params?.entity_id) queryParams.append('entity_id', params.entity_id);
      if (params?.action) queryParams.append('action', params.action);
      if (params?.start_date) queryParams.append('start_date', params.start_date);
      if (params?.end_date) queryParams.append('end_date', params.end_date);
      if (params?.limit) queryParams.append('limit', params.limit.toString());
      if (params?.offset) queryParams.append('offset', params.offset.toString());
      const qs = queryParams.toString();
      return apiFetch<AuditLogListResponse>(`/api/audit${qs ? `?${qs}` : ''}`);
    },
    getRecent: (limit?: number) =>
      apiFetch<AuditLog[]>(`/api/audit/recent?limit=${limit || 100}`),
    getEntityHistory: (entityType: AuditEntityType, entityId: string, limit?: number) =>
      apiFetch<AuditLog[]>(`/api/audit/entity/${entityType}/${entityId}?limit=${limit || 50}`),
    getUserActivity: (userId: string, limit?: number) =>
      apiFetch<AuditLog[]>(`/api/audit/user/${userId}?limit=${limit || 50}`),
    getSummary: () => apiFetch<AuditSummary>('/api/audit/summary'),
  },
};
