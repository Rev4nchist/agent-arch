export interface PageContextConfig {
  pageType: string;
  displayName: string;
  contextPrompt: string;
  suggestions: string[];
}

export interface PageContext {
  route: string;
  pageType: string;
  displayName: string;
  contextPrompt: string;
  metadata: Record<string, unknown>;
}

export interface Suggestion {
  id: string;
  text: string;
  pageType: string;
}

export const PAGE_CONTEXT_MAP: Record<string, PageContextConfig> = {
  '/': {
    pageType: 'dashboard',
    displayName: 'Dashboard',
    contextPrompt: 'User is on the main dashboard viewing platform statistics, recent activity, and quick action cards.',
    suggestions: [
      'What can I ask you about?',
      'What are my most urgent tasks?',
      'Summarize recent meeting outcomes',
      'Show agents needing attention',
    ],
  },
  '/meetings': {
    pageType: 'meetings',
    displayName: 'Meetings Hub',
    contextPrompt: 'User is viewing the meetings hub with scheduled and completed sessions, transcripts, and meeting summaries.',
    suggestions: [
      'What topics were discussed in recent meetings?',
      'Find action items from governance meetings',
      'Who facilitated the most meetings?',
      'Show meetings with unprocessed transcripts',
    ],
  },
  '/tasks': {
    pageType: 'tasks',
    displayName: 'Tasks',
    contextPrompt: 'User is viewing the task management board with tasks organized by status (Pending, In-Progress, Done, Blocked, Deferred).',
    suggestions: [
      'What high priority tasks are pending?',
      'Show blocked tasks needing resolution',
      'Find tasks due this week',
      'Which tasks are assigned to me?',
    ],
  },
  '/agents': {
    pageType: 'agents',
    displayName: 'AI Agents',
    contextPrompt: 'User is viewing the AI agents registry showing agent definitions, tiers, development status, and data sources.',
    suggestions: [
      'Which agents are in development?',
      'Show enterprise tier agents',
      'Find agents related to governance',
      'What agents need testing?',
    ],
  },
  '/decisions': {
    pageType: 'decisions',
    displayName: 'Proposals & Decisions',
    contextPrompt: 'User is viewing governance proposals and approved decisions with status tracking and decision rationale.',
    suggestions: [
      'What can I ask you about?',
      'What proposals are awaiting review?',
      'Show recent architecture decisions',
      'Find licensing-related proposals',
    ],
  },
  '/governance': {
    pageType: 'governance',
    displayName: 'Governance',
    contextPrompt: 'User is viewing governance policies, guidelines, and compliance requirements for the agent ecosystem.',
    suggestions: [
      'What are the key governance policies?',
      'Show compliance requirements',
      'Find security guidelines',
      'What approval thresholds exist?',
    ],
  },
  '/budget': {
    pageType: 'budget',
    displayName: 'Budget & Licensing',
    contextPrompt: 'User is viewing budget allocation, licensing information, and cost tracking for the agent platform.',
    suggestions: [
      'What is the current budget allocation?',
      'Show active licenses',
      'Find cost optimization opportunities',
      'What are the licensing constraints?',
    ],
  },
  '/resources': {
    pageType: 'resources',
    displayName: 'Resources Library',
    contextPrompt: 'User is browsing the educational resources library with documents, links, and reference materials.',
    suggestions: [
      'Find documents about agent frameworks',
      'Show governance resources',
      'What technical guides are available?',
      'Find architecture documentation',
    ],
  },
  '/resources/library': {
    pageType: 'resources',
    displayName: 'Resources Library',
    contextPrompt: 'User is browsing the educational resources library with documents, links, and reference materials organized by category.',
    suggestions: [
      'Find documents about agent frameworks',
      'Show governance resources',
      'What technical guides are available?',
      'Find architecture documentation',
    ],
  },
  '/tech-radar': {
    pageType: 'tech-radar',
    displayName: 'Tech Radar',
    contextPrompt: 'User is viewing the technology radar with tools and technologies categorized as Adopt, Trial, Assess, or Hold.',
    suggestions: [
      'What technologies should we adopt?',
      'Show technologies on hold',
      'Find tools being assessed',
      'What teams are using which technologies?',
    ],
  },
  '/architecture': {
    pageType: 'architecture',
    displayName: 'Architecture Lab',
    contextPrompt: 'User is viewing the architecture lab with code patterns, deployment guides, and architectural references.',
    suggestions: [
      'Show code patterns for agents',
      'Find deployment guides',
      'What architecture patterns exist?',
      'Show hybrid deployment options',
    ],
  },
  '/guide': {
    pageType: 'guide',
    displayName: 'AI Guide',
    contextPrompt: 'User is on the full AI Guide chat interface for in-depth platform queries and assistance.',
    suggestions: [
      'What can I ask you about?',
      'Help me understand the agent tiers',
      'Summarize platform activity this week',
      'How do I create a new agent?',
    ],
  },
};

export const DEFAULT_CONTEXT: PageContextConfig = {
  pageType: 'unknown',
  displayName: 'Page',
  contextPrompt: 'User is navigating the Microsoft Agent Ecosystem platform.',
  suggestions: [
    'What can I help you with?',
    'Show me recent activity',
    'Find pending tasks',
    'Summarize recent meetings',
  ],
};

export function getPageContext(pathname: string): PageContext {
  const baseRoute = '/' + (pathname.split('/')[1] || '');
  const config = PAGE_CONTEXT_MAP[pathname] || PAGE_CONTEXT_MAP[baseRoute] || DEFAULT_CONTEXT;

  return {
    route: pathname,
    pageType: config.pageType,
    displayName: config.displayName,
    contextPrompt: config.contextPrompt,
    metadata: {},
  };
}

export function getSuggestionsForPage(pathname: string): Suggestion[] {
  const baseRoute = '/' + (pathname.split('/')[1] || '');
  const config = PAGE_CONTEXT_MAP[pathname] || PAGE_CONTEXT_MAP[baseRoute] || DEFAULT_CONTEXT;

  return config.suggestions.map((text, index) => ({
    id: `suggestion-${config.pageType}-${index}`,
    text,
    pageType: config.pageType,
  }));
}
