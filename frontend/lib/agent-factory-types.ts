export type DataClassification = 'Public' | 'Internal' | 'Confidential' | 'Restricted';
export type EnterpriseConnector = 'jira' | 'salesforce' | 'sharepoint' | 'servicenow' | 'dynamics365';

export interface GatekeeperState {
  currentQuestion: 0 | 1 | 2 | 'complete';
  answers: [boolean | null, boolean | null, boolean | null];
  recommendation: 'copilot' | 'azure' | null;
}

export interface WizardBasicInfo {
  name: string;
  description: string;
  department: string;
  owner: string;
}

export interface WizardInstructions {
  systemPrompt: string;
  templateId?: string;
}

export interface WizardTools {
  fileSearch: boolean;
  codeInterpreter: boolean;
  connectors: EnterpriseConnector[];
}

export interface WizardKnowledge {
  files: File[];
  uploadedIds: string[];
}

export interface WizardGovernance {
  classification: DataClassification;
  costCenter: string;
  requiresApproval: boolean;
}

export interface WizardData {
  basicInfo: WizardBasicInfo;
  instructions: WizardInstructions;
  tools: WizardTools;
  knowledge: WizardKnowledge;
  governance: WizardGovernance;
}

export type WizardStep = 1 | 2 | 3 | 4 | 5 | 6;

export interface WizardState {
  currentStep: WizardStep;
  data: WizardData;
  validation: Record<WizardStep, boolean>;
  isSubmitting: boolean;
  error: string | null;
}

export type WizardAction =
  | { type: 'SET_STEP'; step: WizardStep }
  | { type: 'NEXT_STEP' }
  | { type: 'PREV_STEP' }
  | { type: 'UPDATE_BASIC_INFO'; data: Partial<WizardBasicInfo> }
  | { type: 'UPDATE_INSTRUCTIONS'; data: Partial<WizardInstructions> }
  | { type: 'UPDATE_TOOLS'; data: Partial<WizardTools> }
  | { type: 'UPDATE_KNOWLEDGE'; data: Partial<WizardKnowledge> }
  | { type: 'UPDATE_GOVERNANCE'; data: Partial<WizardGovernance> }
  | { type: 'SET_VALIDATION'; step: WizardStep; isValid: boolean }
  | { type: 'SET_SUBMITTING'; isSubmitting: boolean }
  | { type: 'SET_ERROR'; error: string | null }
  | { type: 'RESET' };

export interface AgentProvisionRequest {
  name: string;
  description: string;
  department: string;
  owner: string;
  instructions: string;
  tools: string[];
  connectors: EnterpriseConnector[];
  knowledgeFileIds: string[];
  governance: {
    classification: DataClassification;
    costCenter: string;
    requiresApproval: boolean;
  };
}

export interface AgentProvisionResponse {
  agent_id: string;
  status: 'provisioning' | 'ready' | 'error';
  message?: string;
}

export interface AttachKnowledgeResponse {
  files_received: number;
  file_ids: string[];
  status: 'indexing' | 'ready' | 'mock_indexed';
}

export interface ProvisionStatusResponse {
  status: 'provisioning' | 'ready' | 'error';
  progress: number;
  message?: string;
}

export interface CopilotRequest {
  workflow_name: string;
  department: string;
  requestor: string;
  business_justification: string;
  estimated_users: string;
  target_timeline: string;
  attachments?: File[];
}

export const GATEKEEPER_QUESTIONS = [
  {
    id: 0,
    question: "Does this workflow require real-time decision-making with unclear outcomes?",
    description: "Complex scenarios where the agent needs to reason, adapt, and make judgment calls rather than follow a fixed script.",
    yesIndicates: 'azure' as const,
  },
  {
    id: 1,
    question: "Will it need to access enterprise data (Jira, Salesforce, etc.)?",
    description: "Connecting to business systems, searching documents, or taking actions on behalf of users.",
    yesIndicates: 'azure' as const,
  },
  {
    id: 2,
    question: "Will different users need personalized responses?",
    description: "Responses that vary based on the user's role, history, or specific context.",
    yesIndicates: 'azure' as const,
  },
] as const;

export const WIZARD_STEPS = [
  { id: 1, title: 'Basic Info', description: 'Name and ownership' },
  { id: 2, title: 'Instructions', description: 'Agent behavior' },
  { id: 3, title: 'Tools', description: 'Capabilities' },
  { id: 4, title: 'Knowledge', description: 'Documents' },
  { id: 5, title: 'Governance', description: 'Security & compliance' },
  { id: 6, title: 'Review', description: 'Confirm & create' },
] as const;

export const ENTERPRISE_CONNECTORS: { id: EnterpriseConnector; name: string; description: string }[] = [
  { id: 'jira', name: 'Jira', description: 'Issue tracking and project management' },
  { id: 'salesforce', name: 'Salesforce', description: 'CRM and customer data' },
  { id: 'sharepoint', name: 'SharePoint', description: 'Document libraries and team sites' },
  { id: 'servicenow', name: 'ServiceNow', description: 'IT service management' },
  { id: 'dynamics365', name: 'Dynamics 365', description: 'Business applications' },
];

export const DATA_CLASSIFICATIONS: { id: DataClassification; name: string; description: string }[] = [
  { id: 'Public', name: 'Public', description: 'Information that can be shared externally' },
  { id: 'Internal', name: 'Internal', description: 'General internal business information' },
  { id: 'Confidential', name: 'Confidential', description: 'Sensitive business information' },
  { id: 'Restricted', name: 'Restricted', description: 'Highly sensitive, regulated data' },
];

export const INSTRUCTION_TEMPLATES = [
  { id: 'customer-support', name: 'Customer Support', prompt: 'You are a helpful customer support agent. Answer questions about our products and services professionally and accurately. If you don\'t know something, acknowledge it and offer to escalate to a human agent.' },
  { id: 'data-analyst', name: 'Data Analyst', prompt: 'You are a data analysis assistant. Help users understand data, create queries, and interpret results. Provide clear explanations and visualizations when helpful.' },
  { id: 'knowledge-base', name: 'Knowledge Base', prompt: 'You are a knowledge base assistant. Search through company documents to answer questions accurately. Always cite your sources and acknowledge when information might be outdated.' },
  { id: 'custom', name: 'Custom', prompt: '' },
];
