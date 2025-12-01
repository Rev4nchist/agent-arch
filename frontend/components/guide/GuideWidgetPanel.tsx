'use client';

import React, { useRef, useEffect } from 'react';
import { Minus, Maximize2, Minimize2, Trash2, Expand } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ChatMessage, InsightItem, ActionSuggestion } from '@/lib/api';
import { Suggestion } from '@/lib/guide-context';
import { cn } from '@/lib/utils';
import { GuideChatMessage } from './GuideChatMessage';
import { GuideChatInput } from './GuideChatInput';
import { GuideTypingIndicator } from './GuideTypingIndicator';
import { GuideSuggestionBar } from './GuideSuggestionBar';
import { GuideInsightsBar } from './GuideInsightsBar';

interface GuideWidgetPanelProps {
  isOpen: boolean;
  isMinimized: boolean;
  isExpanded: boolean;
  messages: ChatMessage[];
  suggestions: Suggestion[];
  insights: InsightItem[];  // Phase 5.3
  insightsLoading: boolean;  // Phase 5.3
  isLoading: boolean;
  pageName: string;
  onSend: (message: string) => void;
  onMinimize: () => void;
  onExpand: () => void;
  onToggleExpanded: () => void;
  onClear: () => void;
  onDismissInsight: (id: string) => void;  // Phase 5.3
  onInsightAction: (query: string) => void;  // Phase 5.3
  onExecuteAction: (action: ActionSuggestion) => void;  // Phase 5.4
}

export function GuideWidgetPanel({
  isOpen,
  isMinimized,
  isExpanded,
  messages,
  suggestions,
  insights,
  insightsLoading,
  isLoading,
  pageName,
  onSend,
  onMinimize,
  onExpand,
  onToggleExpanded,
  onClear,
  onDismissInsight,
  onInsightAction,
  onExecuteAction,
}: GuideWidgetPanelProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (!isOpen) return null;

  if (isMinimized) {
    return (
      <div
        className={cn(
          'fixed bottom-24 right-6 z-40',
          'w-72 bg-background border rounded-xl shadow-xl',
          'animate-in slide-in-from-bottom-4 duration-200'
        )}
      >
        <button
          onClick={onExpand}
          className="w-full flex items-center justify-between p-3 hover:bg-accent rounded-xl transition-colors"
        >
          <span className="text-sm font-medium">AI Guide</span>
          <Maximize2 className="w-4 h-4 text-muted-foreground" />
        </button>
      </div>
    );
  }

  return (
    <div
      className={cn(
        'fixed z-40',
        'bg-background border rounded-xl shadow-xl',
        'flex flex-col overflow-hidden',
        'animate-in slide-in-from-bottom-4 duration-200',
        'transition-all duration-300 ease-in-out',
        isExpanded
          ? 'bottom-6 right-6 w-[800px] h-[700px] max-h-[85vh]'
          : 'bottom-24 right-6 w-96 h-[500px] max-h-[70vh]'
      )}
    >
      <div className="flex items-center justify-between px-4 py-3 border-b bg-[#00A693]/10">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-[#00A693]" />
          <span className="font-medium text-sm text-[#00A693]">AI Guide</span>
          <span className="text-xs text-muted-foreground">• {pageName}</span>
        </div>
        <div className="flex items-center gap-1">
          {messages.length > 0 && (
            <Button
              variant="ghost"
              size="icon-sm"
              onClick={onClear}
              className="text-muted-foreground hover:text-foreground"
              title="Clear conversation"
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          )}
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={onToggleExpanded}
            className="text-muted-foreground hover:text-[#00A693]"
            title={isExpanded ? 'Collapse' : 'Expand'}
          >
            {isExpanded ? (
              <Minimize2 className="w-4 h-4" />
            ) : (
              <Expand className="w-4 h-4" />
            )}
          </Button>
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={onMinimize}
            className="text-muted-foreground hover:text-foreground"
            title="Minimize"
          >
            <Minus className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Phase 5.3: Show insights when no messages */}
      {messages.length === 0 && (insights.length > 0 || insightsLoading) && (
        <div className="border-b">
          <GuideInsightsBar
            insights={insights}
            isLoading={insightsLoading}
            onDismiss={onDismissInsight}
            onAction={onInsightAction}
            compact={!isExpanded}
          />
        </div>
      )}

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-[#00A693] to-[#008577] flex items-center justify-center mb-3">
              <span className="text-white text-xl">✨</span>
            </div>
            <h3 className="font-medium mb-1">How can I help?</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Ask me anything about the platform, your tasks, meetings, or agents.
            </p>
          </div>
        ) : (
          messages.map((msg) => (
            <GuideChatMessage
              key={msg.id}
              message={msg}
              compact={!isExpanded}
              onExecuteAction={onExecuteAction}
            />
          ))
        )}
        {isLoading && <GuideTypingIndicator compact={!isExpanded} />}
        <div ref={messagesEndRef} />
      </div>

      {messages.length === 0 && suggestions.length > 0 && (
        <div className="px-4 pb-2">
          <GuideSuggestionBar
            suggestions={suggestions}
            onSelect={onSend}
            compact={!isExpanded}
          />
        </div>
      )}

      <div className="p-3 border-t">
        <GuideChatInput
          onSend={onSend}
          isLoading={isLoading}
          placeholder="Ask me anything..."
          compact={!isExpanded}
        />
      </div>
    </div>
  );
}
