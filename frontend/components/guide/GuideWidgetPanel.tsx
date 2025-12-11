'use client';

import React, { useRef, useEffect } from 'react';
import { Minus, Maximize2, Minimize2, Trash2, Expand, Sparkles, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ChatMessage, InsightItem, ActionSuggestion } from '@/lib/api';
import { Suggestion } from '@/lib/guide-context';
import { cn } from '@/lib/utils';
import { useIsMobile } from '@/hooks/useMediaQuery';
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
  insights: InsightItem[];
  insightsLoading: boolean;
  isLoading: boolean;
  pageName: string;
  onSend: (message: string) => void;
  onMinimize: () => void;
  onExpand: () => void;
  onToggleExpanded: () => void;
  onClose: () => void;
  onClear: () => void;
  onDismissInsight: (id: string) => void;
  onInsightAction: (query: string) => void;
  onExecuteAction: (action: ActionSuggestion) => void;
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
  onClose,
  onClear,
  onDismissInsight,
  onInsightAction,
  onExecuteAction,
}: GuideWidgetPanelProps) {
  const isMobile = useIsMobile();
  const lastMessageRef = useRef<HTMLDivElement>(null);
  const prevMessageCount = useRef(0);

  useEffect(() => {
    if (messages.length > prevMessageCount.current) {
      lastMessageRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    prevMessageCount.current = messages.length;
  }, [messages.length]);

  if (!isOpen) return null;

  if (isMinimized) {
    return (
      <div
        className={cn(
          'fixed bottom-24 right-6 z-40',
          'w-72 bg-white border border-[#e5e7eb] rounded-xl shadow-lg',
          'animate-in slide-in-from-bottom-4 duration-200'
        )}
      >
        <button
          onClick={onExpand}
          className="w-full flex items-center justify-between p-3 hover:bg-[#f9fafb] rounded-xl transition-colors"
        >
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-[#00A693] flex items-center justify-center">
              <Sparkles className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="text-sm font-medium text-[#1a1a1a]">AI Guide</span>
          </div>
          <Maximize2 className="w-4 h-4 text-[#6b7280]" />
        </button>
      </div>
    );
  }

  return (
    <div
      className={cn(
        'fixed z-40 bg-white flex flex-col overflow-hidden',
        'animate-in slide-in-from-bottom-4 duration-200',
        'transition-all duration-300 ease-in-out',
        isMobile
          ? 'inset-x-0 top-[56px] bottom-[64px] border-t border-[#e5e7eb]'
          : isExpanded
            ? 'bottom-6 right-6 w-[800px] h-[700px] max-h-[85vh] border border-[#e5e7eb] rounded-xl shadow-xl'
            : 'bottom-24 right-6 w-[420px] h-[560px] max-h-[75vh] border border-[#e5e7eb] rounded-xl shadow-xl'
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-[#e5e7eb]">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-full bg-[#00A693] flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <div className="flex flex-col">
            <span className="font-medium text-sm text-[#1a1a1a]">AI Guide</span>
            <span className="text-xs text-[#6b7280]">{pageName}</span>
          </div>
        </div>
        <div className="flex items-center gap-1">
          {messages.length > 0 && (
            <Button
              variant="ghost"
              size={isMobile ? 'icon' : 'icon-sm'}
              onClick={onClear}
              className="text-[#6b7280] hover:text-[#1a1a1a] hover:bg-[#f3f4f6]"
              title="Clear conversation"
            >
              <Trash2 className={isMobile ? 'w-5 h-5' : 'w-4 h-4'} />
            </Button>
          )}
          {!isMobile && (
            <>
              <Button
                variant="ghost"
                size="icon-sm"
                onClick={onToggleExpanded}
                className="text-[#6b7280] hover:text-[#00A693] hover:bg-[#e8f5f1]"
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
                className="text-[#6b7280] hover:text-[#1a1a1a] hover:bg-[#f3f4f6]"
                title="Minimize"
              >
                <Minus className="w-4 h-4" />
              </Button>
            </>
          )}
          <Button
            variant="ghost"
            size={isMobile ? 'icon' : 'icon-sm'}
            onClick={onClose}
            className="text-[#6b7280] hover:text-[#1a1a1a] hover:bg-[#f3f4f6]"
            title="Close"
          >
            <X className={isMobile ? 'w-5 h-5' : 'w-4 h-4'} />
          </Button>
        </div>
      </div>

      {/* Insights bar when no messages */}
      {messages.length === 0 && (insights.length > 0 || insightsLoading) && (
        <div className="border-b border-[#e5e7eb]">
          <GuideInsightsBar
            insights={insights}
            isLoading={insightsLoading}
            onDismiss={onDismissInsight}
            onAction={onInsightAction}
            compact={!isExpanded}
          />
        </div>
      )}

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto bg-white">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center px-4 py-6">
            <div className="w-12 h-12 rounded-full bg-[#00A693] flex items-center justify-center mb-3">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <h3 className="font-semibold text-base text-[#1a1a1a] mb-1">How can I help?</h3>
            <p className="text-sm text-[#6b7280] max-w-[280px] leading-relaxed mb-3">
              Ask me anything about the platform, your tasks, meetings, or agents.
            </p>

            {/* Intelligent Memory blurb */}
            <div className="bg-gradient-to-r from-[#00A693]/10 to-[#008577]/10 border border-[#00A693]/20 rounded-lg p-3 max-w-[320px] mb-4">
              <div className="flex items-center gap-2 mb-1">
                <div className="w-1.5 h-1.5 rounded-full bg-[#00A693] animate-pulse" />
                <span className="text-xs font-medium text-[#00A693] uppercase tracking-wide">Intelligent Memory</span>
              </div>
              <p className="text-xs text-muted-foreground">
                I remember context across conversations, learn facts you share, and provide personalized assistance.
              </p>
              <div className="flex flex-wrap gap-1.5 mt-2">
                <span className="text-[10px] px-1.5 py-0.5 bg-background rounded border">Topic Tracking</span>
                <span className="text-[10px] px-1.5 py-0.5 bg-background rounded border">Fact Learning</span>
                <span className="text-[10px] px-1.5 py-0.5 bg-background rounded border">Context Resumption</span>
              </div>
            </div>
          </div>
        ) : (
          <div className="px-4 py-2">
            {messages.map((msg, index) => (
              <div
                key={msg.id}
                ref={index === messages.length - 1 ? lastMessageRef : null}
              >
                <GuideChatMessage
                  message={msg}
                  compact={!isExpanded}
                  onExecuteAction={onExecuteAction}
                />
              </div>
            ))}
            {isLoading && (
              <div className="py-3">
                <GuideTypingIndicator compact={!isExpanded} />
              </div>
            )}
          </div>
        )}
      </div>

      {/* Suggestions - when no messages */}
      {messages.length === 0 && suggestions.length > 0 && (
        <div className="px-4 pb-2">
          <GuideSuggestionBar
            suggestions={suggestions}
            onSelect={onSend}
            compact={!isExpanded}
          />
        </div>
      )}

      {/* Input area */}
      <div className="p-3 border-t border-[#e5e7eb] bg-white">
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
