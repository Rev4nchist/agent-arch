// Use empty string for relative URLs when running through reverse proxy
// Endpoints already include /api prefix
// In production: uses NEXT_PUBLIC_API_URL from .env.production
// In local dev: set NEXT_PUBLIC_API_URL in .env.local to your local API
const API_URL = process.env.NEXT_PUBLIC_API_URL || '';
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
  from_submission_id?: string;
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
  type: 'meeting' | 'task' | 'agent' | 'governance' | 'docs' | 'platform';
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
  action_type: 'query' | 'filter' | 'navigate' | 'create' | 'export' | 'show_detail' | 'view' | 'open_loop';
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

export type SuggestionSource = 'static' | 'intent' | 'open_loop' | 'common_query' | 'topic_interest' | 'entity' | 'context';

export interface PersonalizedSuggestion {
  id: string;
  text: string;
  source: SuggestionSource;
  priority: number;
  confidence: number;
  metadata?: Record<string, unknown>;
}

export interface PersonalizedSuggestionsResponse {
  suggestions: PersonalizedSuggestion[];
  is_personalized: boolean;
  fallback_reason?: string;
  page_type: string;
}

// Streaming response chunk types
export interface StreamMetadataChunk {
  type: 'metadata';
  sources: string[];
  intent: string;
  confidence: string;
  suggestions: ActionSuggestion[];
  data_basis: DataBasis | null;
}

export interface StreamContentChunk {
  type: 'content';
  token: string;
}

export interface StreamDoneChunk {
  type: 'done';
}

export type StreamChunk = StreamMetadataChunk | StreamContentChunk | StreamDoneChunk;

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

export type SubmissionCategory = 'Bug Report' | 'Feature Request' | 'Improvement Idea' | 'Question';
export type SubmissionStatus = 'Submitted' | 'Under Review' | 'In Progress' | 'Completed' | 'Declined';
export type SubmissionPriority = 'Critical' | 'High' | 'Medium' | 'Low';

export interface SubmissionComment {
  id: string;
  user: string;
  content: string;
  created_at: string;
  updated_at?: string;
}

export interface Submission {
  id: string;
  title: string;
  description: string;
  category: SubmissionCategory;
  priority: SubmissionPriority;
  status: SubmissionStatus;
  submitted_by: string;
  submitted_at: string;
  upvotes: string[];
  upvote_count: number;
  comments: SubmissionComment[];
  assigned_to?: string;
  tags: string[];
  linked_task_id?: string;
  resolved_at?: string;
  resolution_notes?: string;
  updated_at: string;
}

export interface SubmissionCreate {
  title: string;
  description: string;
  category: SubmissionCategory;
  priority: SubmissionPriority;
  submitted_by: string;
  tags?: string[];
}

export interface SubmissionUpdate {
  title?: string;
  description?: string;
  category?: SubmissionCategory;
  priority?: SubmissionPriority;
  status?: SubmissionStatus;
  assigned_to?: string;
  tags?: string[];
  resolution_notes?: string;
}

export interface SubmissionFilters {
  status?: SubmissionStatus;
  category?: SubmissionCategory;
  priority?: SubmissionPriority;
  assigned_to?: string;
  submitted_by?: string;
  sort_by?: 'upvotes' | 'date' | 'priority';
  limit?: number;
  offset?: number;
}

export interface SubmissionListResponse {
  items: Submission[];
  total: number;
}

export interface SubmissionStats {
  total: number;
  by_status: Record<string, number>;
  by_category: Record<string, number>;
  by_priority: Record<string, number>;
}

export interface SubmissionConvertResponse {
  submission: Submission;
  task: Task;
}

export type BudgetCategory = 'Azure Service' | 'Software License' | 'Custom Allocation';
export type BudgetStatus = 'On Track' | 'Warning' | 'Critical' | 'Exceeded';
export type LicenseType = 'Subscription' | 'Pay-as-you-go' | 'Perpetual' | 'Enterprise';
export type LicenseStatus = 'Active' | 'Expiring' | 'Expired' | 'Suspended';

export interface Budget {
  id: string;
  name: string;
  category: BudgetCategory;
  resource_groups: string[];
  azure_service_type?: string;
  amount: number;
  spent: number;
  currency: string;
  period: string;
  status: BudgetStatus;
  threshold_warning: number;
  threshold_critical: number;
  start_date?: string;
  end_date?: string;
  notes?: string;
  owner?: string;
  created_at: string;
  updated_at: string;
}

export interface BudgetCreate {
  name: string;
  category: BudgetCategory;
  resource_groups?: string[];
  azure_service_type?: string;
  amount: number;
  currency?: string;
  period?: string;
  threshold_warning?: number;
  threshold_critical?: number;
  start_date?: string;
  end_date?: string;
  notes?: string;
  owner?: string;
}

export interface License {
  id: string;
  name: string;
  vendor: string;
  license_type: LicenseType;
  seats?: number;
  cost_per_seat?: number;
  monthly_cost: number;
  annual_cost?: number;
  renewal_date?: string;
  status: LicenseStatus;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface LicenseCreate {
  name: string;
  vendor: string;
  license_type: LicenseType;
  seats?: number;
  cost_per_seat?: number;
  monthly_cost: number;
  annual_cost?: number;
  renewal_date?: string;
  notes?: string;
}

export interface CostSummary {
  total_cost: number;
  currency: string;
  resource_groups_count: number;
  period: string;
  period_start: string;
  period_end: string;
  by_resource_group: Array<{ name: string; cost: number }>;
  top_services: Array<{ name: string; cost: number }>;
}

export interface ResourceGroupCost {
  resource_group: string;
  total_cost: number;
  currency: string;
  services: Array<{ name: string; cost: number; currency: string }>;
  period_start?: string;
  period_end?: string;
  error?: string;
}

export interface BudgetDashboard {
  azure_costs: CostSummary;
  budgets: Budget[];
  licenses: License[];
  totals: {
    azure_spend: number;
    license_spend: number;
    total_monthly: number;
    total_budget: number;
  };
}



export type FeatureUpdateCategory = 'New Feature' | 'Improvement' | 'Bug Fix' | 'Announcement';

export interface FeatureUpdate {
  id: string;
  title: string;
  description: string;
  category: FeatureUpdateCategory;
  version?: string;
  related_pages: string[];
  published_at: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface FeatureUpdateCreate {
  title: string;
  description: string;
  category: FeatureUpdateCategory;
  version?: string;
  related_pages?: string[];
  published_at?: string;
  created_by: string;
}

export interface FeatureUpdateUpdate {
  title?: string;
  description?: string;
  category?: FeatureUpdateCategory;
  version?: string;
  related_pages?: string[];
  published_at?: string;
}

export interface FeatureUpdateListResponse {
  items: FeatureUpdate[];
  total: number;
}
export interface MemorySummary {
  total_facts: number;
  verified_facts: number;
  active_topics: number;
  open_loops: number;
}

export interface MemoryFact {
  fact_id: number;
  key: string;
  value: string;
  category: string;
  confidence: number;
  verified: boolean;
  evidence_snippet?: string;
  created_at?: string;
}

export interface FactsListResponse {
  facts: MemoryFact[];
  total: number;
}

export interface MemoryProfile {
  user_id: string;
  preferences: Record<string, unknown>;
  common_queries: string[];
  known_entities: Array<{ name: string; type: string; context?: string }>;
  interaction_patterns: Record<string, unknown>;
  last_updated?: string;
}

export interface TopicSummary {
  id: string;
  session_id: string;
  topic_label: string;
  status: string;
  turn_count: number;
  open_loops: string[];
  last_activity: string;
}

export interface TopicTurn {
  index: number;
  query: string;
  response_summary: string;
  intent?: string;
  entities: string[];
  timestamp?: string;
}

export interface TopicDetail {
  id: string;
  session_id: string;
  topic_label: string;
  summary: string;
  status: string;
  keywords: string[];
  open_loops: string[];
  decisions_made: string[];
  turn_count: number;
  turns: TopicTurn[];
  created_at: string;
  last_activity: string;
}

export interface TopicsListResponse {
  topics: TopicSummary[];
  total: number;
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
    delete: (id: string) =>
      apiFetch<{ success: boolean }>(`/api/tasks/${id}`, {
        method: 'DELETE',
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
    factory: {
      provision: (data: {
        name: string;
        description: string;
        department: string;
        owner: string;
        instructions: string;
        tools: string[];
        connectors: string[];
        knowledge_file_ids: string[];
        governance: {
          classification: 'Public' | 'Internal' | 'Confidential' | 'Restricted';
          cost_center?: string;
          requires_approval: boolean;
        };
      }) =>
        apiFetch<{ agent_id: string; status: string; message?: string }>(
          '/api/agents/factory/provision',
          {
            method: 'POST',
            body: JSON.stringify(data),
          }
        ),
      getStatus: (agentId: string) =>
        apiFetch<{ status: string; progress: number; message?: string }>(
          `/api/agents/factory/${agentId}/status`
        ),
      attachKnowledge: async (agentId: string, files: File[]) => {
        const formData = new FormData();
        files.forEach((file) => formData.append('files', file));
        const response = await fetch(`${API_URL}/api/agents/factory/${agentId}/knowledge`, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${API_KEY}`,
          },
          body: formData,
        });
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json() as Promise<{
          files_received: number;
          file_ids: string[];
          vector_store_id: string;
          status: string;
        }>;
      },
      createThread: (agentId: string) =>
        apiFetch<{ thread_id: string; agent_id: string; created_at: string }>(
          `/api/agents/factory/${agentId}/threads`,
          { method: 'POST' }
        ),
      executeRun: (agentId: string, threadId: string, message: string) =>
        apiFetch<{ run_id: string; thread_id: string; status: string; response: string }>(
          `/api/agents/factory/${agentId}/threads/${threadId}/runs`,
          {
            method: 'POST',
            body: JSON.stringify({ message }),
          }
        ),
    },
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
    update: (id: string, data: Partial<Omit<Decision, 'id' | 'created_at' | 'updated_at'>>) =>
      apiFetch<Decision>(`/api/decisions/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      apiFetch<void>(`/api/decisions/${id}`, {
        method: 'DELETE',
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
    queryStream: async function* (
      query: string,
      context?: string,
      pageContext?: PageContext,
      sessionId?: string,
      userId?: string
    ): AsyncGenerator<StreamChunk, void, unknown> {
      const response = await fetch(`${API_URL}/api/agent/query/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${API_KEY}`,
        },
        body: JSON.stringify({
          query,
          context,
          page_context: pageContext,
          session_id: sessionId,
          user_id: userId,
        }),
      });

      if (!response.ok) {
        throw new Error(`Stream API error: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');

      try {
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          const lines = buffer.split('\n');
          buffer = lines[lines.length - 1];

          for (let i = 0; i < lines.length - 1; i++) {
            const line = lines[i];
            if (line.startsWith('data: ')) {
              const dataStr = line.slice(6);
              if (dataStr && dataStr.trim()) {
                try {
                  yield JSON.parse(dataStr) as StreamChunk;
                } catch {
                  // Skip malformed JSON
                }
              }
            }
          }
        }

        if (buffer.startsWith('data: ')) {
          const dataStr = buffer.slice(6);
          if (dataStr && dataStr.trim()) {
            try {
              yield JSON.parse(dataStr) as StreamChunk;
            } catch {
              // Skip malformed JSON
            }
          }
        }
      } finally {
        reader.releaseLock();
      }
    },
    search: (query: string, docType?: string, top?: number) =>
      apiFetch<SearchResult[]>('/api/search', {
        method: 'POST',
        body: JSON.stringify({ query, doc_type: docType, top: top || 5 }),
      }),
    // Phase 5.3: Proactive insights
    getInsights: (page: string) =>
      apiFetch<InsightsResponse>(`/api/agent/insights?page=${encodeURIComponent(page)}`),
    // HMLR Personalized suggestions
    getSuggestions: (pageType: string, userId?: string, sessionId?: string) => {
      const params = new URLSearchParams({ page_type: pageType });
      if (userId) params.append('user_id', userId);
      if (sessionId) params.append('session_id', sessionId);
      return apiFetch<PersonalizedSuggestionsResponse>(`/api/guide/suggestions?${params.toString()}`);
    },
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
  submissions: {
    list: (filters?: SubmissionFilters) => {
      const queryParams = new URLSearchParams();
      if (filters?.status) queryParams.append('status', filters.status);
      if (filters?.category) queryParams.append('category', filters.category);
      if (filters?.priority) queryParams.append('priority', filters.priority);
      if (filters?.assigned_to) queryParams.append('assigned_to', filters.assigned_to);
      if (filters?.submitted_by) queryParams.append('submitted_by', filters.submitted_by);
      if (filters?.sort_by) queryParams.append('sort_by', filters.sort_by);
      if (filters?.limit) queryParams.append('limit', filters.limit.toString());
      if (filters?.offset) queryParams.append('offset', filters.offset.toString());
      const qs = queryParams.toString();
      return apiFetch<SubmissionListResponse>(`/api/submissions${qs ? `?${qs}` : ''}`);
    },
    get: (id: string) => apiFetch<Submission>(`/api/submissions/${id}`),
    create: (data: SubmissionCreate) =>
      apiFetch<Submission>('/api/submissions', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    update: (id: string, data: SubmissionUpdate) =>
      apiFetch<Submission>(`/api/submissions/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      apiFetch<{ message: string }>(`/api/submissions/${id}`, {
        method: 'DELETE',
      }),
    upvote: (id: string, user: string) =>
      apiFetch<Submission>(`/api/submissions/${id}/upvote?user=${encodeURIComponent(user)}`, {
        method: 'POST',
      }),
    addComment: (id: string, user: string, content: string) =>
      apiFetch<Submission>(`/api/submissions/${id}/comments`, {
        method: 'POST',
        body: JSON.stringify({ user, content }),
      }),
    updateComment: (id: string, commentId: string, content: string) =>
      apiFetch<Submission>(`/api/submissions/${id}/comments/${commentId}?content=${encodeURIComponent(content)}`, {
        method: 'PUT',
      }),
    deleteComment: (id: string, commentId: string) =>
      apiFetch<Submission>(`/api/submissions/${id}/comments/${commentId}`, {
        method: 'DELETE',
      }),
    convertToTask: (id: string, category?: string) => {
      const queryParams = category ? `?category=${encodeURIComponent(category)}` : '';
      return apiFetch<SubmissionConvertResponse>(`/api/submissions/${id}/convert-to-task${queryParams}`, {
        method: 'POST',
      });
    },
    getStats: () => apiFetch<SubmissionStats>('/api/submissions/stats'),
  },
  memories: {
    getSummary: (userId: string) =>
      apiFetch<MemorySummary>(`/api/memories/summary?user_id=${encodeURIComponent(userId)}`),
    getFacts: (userId: string, params?: { category?: string; search?: string; limit?: number; offset?: number }) => {
      const queryParams = new URLSearchParams();
      queryParams.append('user_id', userId);
      if (params?.category) queryParams.append('category', params.category);
      if (params?.search) queryParams.append('search', params.search);
      if (params?.limit) queryParams.append('limit', params.limit.toString());
      if (params?.offset) queryParams.append('offset', params.offset.toString());
      return apiFetch<FactsListResponse>(`/api/memories/facts?${queryParams.toString()}`);
    },
    verifyFact: (factId: number, userId: string) =>
      apiFetch<{ success: boolean }>(`/api/memories/facts/${factId}/verify?user_id=${encodeURIComponent(userId)}`, {
        method: 'PUT',
      }),
    deleteFact: (factId: number, userId: string) =>
      apiFetch<{ success: boolean }>(`/api/memories/facts/${factId}?user_id=${encodeURIComponent(userId)}`, {
        method: 'DELETE',
      }),
    getProfile: (userId: string) =>
      apiFetch<MemoryProfile>(`/api/memories/profile?user_id=${encodeURIComponent(userId)}`),
    updatePreferences: (userId: string, preferences: Record<string, unknown>) =>
      apiFetch<{ success: boolean }>(`/api/memories/profile/preferences?user_id=${encodeURIComponent(userId)}`, {
        method: 'PATCH',
        body: JSON.stringify({ preferences }),
      }),
    deleteCommonQuery: (userId: string, idx: number) =>
      apiFetch<{ success: boolean }>(`/api/memories/profile/common-queries/${idx}?user_id=${encodeURIComponent(userId)}`, {
        method: 'DELETE',
      }),
    deleteKnownEntity: (userId: string, idx: number) =>
      apiFetch<{ success: boolean }>(`/api/memories/profile/known-entities/${idx}?user_id=${encodeURIComponent(userId)}`, {
        method: 'DELETE',
      }),
    getTopics: (userId: string, params?: { limit?: number; offset?: number }) => {
      const queryParams = new URLSearchParams();
      queryParams.append('user_id', userId);
      if (params?.limit) queryParams.append('limit', params.limit.toString());
      if (params?.offset) queryParams.append('offset', params.offset.toString());
      return apiFetch<TopicsListResponse>(`/api/memories/topics?${queryParams.toString()}`);
    },
    getTopicDetail: (topicId: string, sessionId: string) =>
      apiFetch<TopicDetail>(`/api/memories/topics/${topicId}?session_id=${encodeURIComponent(sessionId)}`),
    deleteOpenLoop: (topicId: string, sessionId: string, idx: number) =>
      apiFetch<{ success: boolean }>(`/api/memories/topics/${topicId}/open-loops/${idx}?session_id=${encodeURIComponent(sessionId)}`, {
        method: 'DELETE',
      }),
  },
  budget: {
    getDashboard: () => apiFetch<BudgetDashboard>('/api/budget/dashboard'),
    getCostSummary: () => apiFetch<CostSummary>('/api/budget/costs/summary'),
    getResourceGroupCosts: (forceRefresh?: boolean) =>
      apiFetch<ResourceGroupCost[]>(`/api/budget/costs/resource-groups${forceRefresh ? '?force_refresh=true' : ''}`),
    getResourceGroupCost: (resourceGroup: string) =>
      apiFetch<ResourceGroupCost>(`/api/budget/costs/resource-groups/${encodeURIComponent(resourceGroup)}`),
    getCostsByService: () =>
      apiFetch<{ services: Array<{ name: string; cost: number }> }>('/api/budget/costs/by-service'),
    getCostTrend: (resourceGroup?: string, days?: number) => {
      const params = new URLSearchParams();
      if (resourceGroup) params.append('resource_group', resourceGroup);
      if (days) params.append('days', days.toString());
      const qs = params.toString();
      return apiFetch<{ trend: Array<{ date: string; cost: number }>; days: number; resource_group?: string }>(
        `/api/budget/costs/trend${qs ? `?${qs}` : ''}`
      );
    },
    getResourceGroups: () =>
      apiFetch<{ resource_groups: string[] }>('/api/budget/resource-groups'),
    listBudgets: () => apiFetch<Budget[]>('/api/budget/budgets'),
    getBudget: (id: string) => apiFetch<Budget>(`/api/budget/budgets/${id}`),
    createBudget: (data: BudgetCreate) =>
      apiFetch<Budget>('/api/budget/budgets', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    updateBudget: (id: string, data: BudgetCreate) =>
      apiFetch<Budget>(`/api/budget/budgets/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    deleteBudget: (id: string) =>
      apiFetch<{ message: string }>(`/api/budget/budgets/${id}`, {
        method: 'DELETE',
      }),
    listLicenses: () => apiFetch<License[]>('/api/budget/licenses'),
    getLicense: (id: string) => apiFetch<License>(`/api/budget/licenses/${id}`),
    createLicense: (data: LicenseCreate) =>
      apiFetch<License>('/api/budget/licenses', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    updateLicense: (id: string, data: LicenseCreate) =>
      apiFetch<License>(`/api/budget/licenses/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    deleteLicense: (id: string) =>
      apiFetch<{ message: string }>(`/api/budget/licenses/${id}`, {
        method: 'DELETE',
      }),
  },

  featureUpdates: {
    list: (params?: { category?: FeatureUpdateCategory; limit?: number; offset?: number }) => {
      const queryParams = new URLSearchParams();
      if (params?.category) queryParams.append('category', params.category);
      if (params?.limit) queryParams.append('limit', params.limit.toString());
      if (params?.offset) queryParams.append('offset', params.offset.toString());
      const queryString = queryParams.toString();
      return apiFetch<FeatureUpdateListResponse>('/api/feature-updates' + (queryString ? '?' + queryString : ''));
    },
    get: (id: string) => apiFetch<FeatureUpdate>('/api/feature-updates/' + id),
    create: (data: FeatureUpdateCreate) =>
      apiFetch<FeatureUpdate>('/api/feature-updates', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    update: (id: string, data: FeatureUpdateUpdate) =>
      apiFetch<FeatureUpdate>('/api/feature-updates/' + id, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      apiFetch<{ message: string }>('/api/feature-updates/' + id, {
        method: 'DELETE',
      }),
  },
};
