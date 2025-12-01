'use client';

import React, { createContext, useContext, useState, useCallback, useRef, useEffect, ReactNode } from 'react';
import { usePathname } from 'next/navigation';
import { ChatMessage, ChatSource, DataBasis, InsightItem, ActionSuggestion, api, PageContext as ApiPageContext } from '@/lib/api';
import { useRouter } from 'next/navigation';
import { getPageContext, getSuggestionsForPage, PageContext, Suggestion } from '@/lib/guide-context';

function generateId(): string {
  return Math.random().toString(36).substring(2, 15);
}

// Phase 5.2: Generate session ID for conversation memory
function generateSessionId(): string {
  return `session_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;
}

interface GuideContextState {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  isWidgetOpen: boolean;
  isMinimized: boolean;
  isExpanded: boolean;
  currentPage: PageContext;
  suggestions: Suggestion[];
  insights: InsightItem[];  // Phase 5.3
  insightsLoading: boolean;  // Phase 5.3
  sendMessage: (query: string) => Promise<void>;
  clearConversation: () => void;
  toggleWidget: () => void;
  minimizeWidget: () => void;
  expandWidget: () => void;
  toggleExpanded: () => void;
  closeWidget: () => void;
  dismissError: () => void;
  dismissInsight: (id: string) => void;  // Phase 5.3
  runInsightAction: (query: string) => void;  // Phase 5.3
  executeAction: (action: ActionSuggestion) => void;  // Phase 5.4
}

const GuideContext = createContext<GuideContextState | null>(null);

interface GuideProviderProps {
  children: ReactNode;
}

export function GuideProvider({ children }: GuideProviderProps) {
  const pathname = usePathname();
  const router = useRouter();  // Phase 5.4
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isWidgetOpen, setIsWidgetOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  // Phase 5.2: Session ID for conversation memory (persists until widget closes)
  const sessionIdRef = useRef<string>(generateSessionId());

  // Phase 5.3: Proactive insights
  const [insights, setInsights] = useState<InsightItem[]>([]);
  const [insightsLoading, setInsightsLoading] = useState(false);
  const insightsCacheRef = useRef<{ page: string; data: InsightItem[]; timestamp: number } | null>(null);

  const currentPage = getPageContext(pathname);
  const suggestions = getSuggestionsForPage(pathname);

  // Phase 5.3: Fetch insights when widget opens (with 60s cache)
  useEffect(() => {
    if (!isWidgetOpen || isMinimized) return;

    const fetchInsights = async () => {
      const pageName = pathname.replace(/^\//, '') || 'dashboard';
      const now = Date.now();

      // Check cache (60 second TTL)
      if (
        insightsCacheRef.current &&
        insightsCacheRef.current.page === pageName &&
        now - insightsCacheRef.current.timestamp < 60000
      ) {
        setInsights(insightsCacheRef.current.data);
        return;
      }

      setInsightsLoading(true);
      try {
        const response = await api.guide.getInsights(pageName);
        setInsights(response.insights);
        insightsCacheRef.current = { page: pageName, data: response.insights, timestamp: now };
      } catch (err) {
        console.error('Failed to fetch insights:', err);
        setInsights([]);
      } finally {
        setInsightsLoading(false);
      }
    };

    fetchInsights();
  }, [isWidgetOpen, isMinimized, pathname]);

  const sendMessage = useCallback(async (query: string) => {
    if (!query.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: generateId(),
      role: 'user',
      content: query.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const contextString = [
        `Current page: ${currentPage.displayName}`,
        `Page type: ${currentPage.pageType}`,
        currentPage.contextPrompt,
      ].join('\n');

      const pageContextForApi: ApiPageContext = {
        current_page: pathname,
        visible_entity_type: currentPage.pageType,
      };

      // Phase 5.2: Include session ID for conversation memory
      const response = await api.guide.query(query, contextString, pageContextForApi, sessionIdRef.current);

      const sources: ChatSource[] = response.sources?.map((s, i) => {
        const [type, ...titleParts] = s.split(': ');
        return {
          id: `source-${i}`,
          title: titleParts.join(': ') || s,
          type: (type.toLowerCase() as 'meeting' | 'task' | 'agent' | 'governance') || 'governance',
        };
      }) || [];

      const assistantMessage: ChatMessage = {
        id: generateId(),
        role: 'assistant',
        content: response.response,
        sources: sources.length > 0 ? sources : undefined,
        data_basis: response.data_basis,
        suggestions: response.suggestions,  // Phase 5.4: Quick actions
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to get response';
      setError(errorMsg);

      const errorMessage: ChatMessage = {
        id: generateId(),
        role: 'assistant',
        content: 'I apologize, but I encountered an error processing your request. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, currentPage]);

  const clearConversation = useCallback(() => {
    setMessages([]);
    setError(null);
    // Phase 5.2: Generate new session ID when conversation is cleared
    sessionIdRef.current = generateSessionId();
  }, []);

  const toggleWidget = useCallback(() => {
    if (isWidgetOpen) {
      setIsWidgetOpen(false);
      setIsMinimized(false);
    } else {
      setIsWidgetOpen(true);
      setIsMinimized(false);
    }
  }, [isWidgetOpen]);

  const minimizeWidget = useCallback(() => {
    setIsMinimized(true);
  }, []);

  const expandWidget = useCallback(() => {
    setIsMinimized(false);
  }, []);

  const toggleExpanded = useCallback(() => {
    setIsExpanded((prev) => !prev);
  }, []);

  const closeWidget = useCallback(() => {
    setIsWidgetOpen(false);
    setIsMinimized(false);
    setIsExpanded(false);
    // Phase 5.2: Generate new session ID when widget is closed (new conversation)
    sessionIdRef.current = generateSessionId();
  }, []);

  const dismissError = useCallback(() => {
    setError(null);
  }, []);

  // Phase 5.3: Dismiss a specific insight
  const dismissInsight = useCallback((id: string) => {
    setInsights((prev) => prev.filter((insight) => insight.id !== id));
  }, []);

  // Phase 5.3: Run the action query from an insight
  const runInsightAction = useCallback((query: string) => {
    if (query) {
      sendMessage(query);
    }
  }, [sendMessage]);

  // Phase 5.4: Execute a quick action from response suggestions
  const executeAction = useCallback((action: ActionSuggestion) => {
    switch (action.action_type) {
      case 'query':
        // Run another query
        if (action.params.query) {
          sendMessage(String(action.params.query));
        }
        break;

      case 'navigate':
        // Navigate to a page
        if (action.params.page) {
          router.push(`/${action.params.page}`);
        } else if (action.params.id && action.params.entity) {
          router.push(`/${action.params.entity}s/${action.params.id}`);
        }
        break;

      case 'filter':
        // Dispatch a custom event for the current page to handle
        if (action.params.entity && action.params.field) {
          const filterEvent = new CustomEvent('guide-filter-action', {
            detail: {
              entity: action.params.entity,
              field: action.params.field,
              value: action.params.value,
            },
          });
          window.dispatchEvent(filterEvent);
        }
        break;

      case 'show_detail':
        // Dispatch event to show detail modal
        if (action.params.id) {
          const detailEvent = new CustomEvent('guide-show-detail', {
            detail: {
              id: action.params.id,
              entity: action.params.entity,
            },
          });
          window.dispatchEvent(detailEvent);
        }
        break;

      case 'export':
        // Dispatch event for export
        const exportEvent = new CustomEvent('guide-export-action', {
          detail: {
            entity: action.params.entity,
            format: action.params.format || 'csv',
          },
        });
        window.dispatchEvent(exportEvent);
        break;

      case 'create':
        // Note: create is intentionally not implemented (read-only actions only)
        // Just show a message that creation should be done via the UI
        console.log('Create actions should be performed via the UI');
        break;

      default:
        console.warn('Unknown action type:', action.action_type);
    }
  }, [router, sendMessage]);

  const value: GuideContextState = {
    messages,
    isLoading,
    error,
    isWidgetOpen,
    isMinimized,
    isExpanded,
    currentPage,
    suggestions,
    insights,  // Phase 5.3
    insightsLoading,  // Phase 5.3
    sendMessage,
    clearConversation,
    toggleWidget,
    minimizeWidget,
    expandWidget,
    toggleExpanded,
    closeWidget,
    dismissError,
    dismissInsight,  // Phase 5.3
    runInsightAction,  // Phase 5.3
    executeAction,  // Phase 5.4
  };

  return (
    <GuideContext.Provider value={value}>
      {children}
    </GuideContext.Provider>
  );
}

export function useGuide(): GuideContextState {
  const context = useContext(GuideContext);
  if (!context) {
    throw new Error('useGuide must be used within a GuideProvider');
  }
  return context;
}
