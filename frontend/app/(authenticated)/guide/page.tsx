'use client';

import { useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Sparkles, Trash2, X } from 'lucide-react';
import { useGuide } from '@/components/providers/GuideProvider';
import { useIsMobile } from '@/hooks/useMediaQuery';
import {
  GuideChatMessage,
  GuideChatInput,
  GuideTypingIndicator,
  GuideSuggestionBar,
} from '@/components/guide';

export default function GuidePage() {
  const router = useRouter();
  const isMobile = useIsMobile();
  const {
    messages,
    isLoading,
    error,
    suggestions,
    sendMessage,
    clearConversation,
    dismissError,
    executeAction,
  } = useGuide();

  const lastMessageRef = useRef<HTMLDivElement>(null);
  const prevMessageCount = useRef(0);

  useEffect(() => {
    if (messages.length > prevMessageCount.current) {
      lastMessageRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    prevMessageCount.current = messages.length;
  }, [messages.length]);

  // Mobile layout - matches widget modal exactly
  if (isMobile) {
    return (
      <div className="flex flex-col h-[calc(100vh-120px)] bg-white">
        {/* Header - matches widget */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-[#e5e7eb]">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-full bg-[#00A693] flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <div className="flex flex-col">
              <span className="font-medium text-sm text-[#1a1a1a]">AI Guide</span>
              <span className="text-xs text-[#6b7280]">Fourth AI</span>
            </div>
          </div>
          <div className="flex items-center gap-1">
            {messages.length > 0 && (
              <Button
                variant="ghost"
                size="icon"
                onClick={clearConversation}
                className="text-[#6b7280] hover:text-[#1a1a1a] hover:bg-[#f3f4f6]"
                title="Clear conversation"
              >
                <Trash2 className="w-5 h-5" />
              </Button>
            )}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => router.back()}
              className="text-[#6b7280] hover:text-[#1a1a1a] hover:bg-[#f3f4f6]"
              title="Close"
            >
              <X className="w-5 h-5" />
            </Button>
          </div>
        </div>

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
              {messages.map((message, index) => (
                <div
                  key={message.id}
                  ref={index === messages.length - 1 ? lastMessageRef : null}
                >
                  <GuideChatMessage
                    message={message}
                    compact
                    onExecuteAction={executeAction}
                  />
                </div>
              ))}
              {isLoading && (
                <div className="py-3">
                  <GuideTypingIndicator compact />
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
              onSelect={sendMessage}
            />
          </div>
        )}

        {/* Input area */}
        <div className="p-3 border-t border-[#e5e7eb] bg-white">
          {error && (
            <div className="mb-2 p-2 bg-destructive/10 border border-destructive/20 rounded-lg flex items-center justify-between">
              <p className="text-xs text-destructive">{error}</p>
              <Button variant="ghost" size="sm" onClick={dismissError}>
                Dismiss
              </Button>
            </div>
          )}
          <GuideChatInput
            onSend={sendMessage}
            isLoading={isLoading}
            placeholder="Ask me anything..."
            compact
          />
        </div>
      </div>
    );
  }

  // Desktop layout - original card-based design
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-background">
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-[#00A693] to-[#008577]">
              <Sparkles className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-semibold">Fourth AI Guide</h1>
              <p className="text-sm text-muted-foreground">
                Your AI assistant for the Microsoft Agent Ecosystem
              </p>
            </div>
          </div>
          {messages.length > 0 && (
            <Button variant="outline" size="sm" onClick={clearConversation}>
              <Trash2 className="h-4 w-4 mr-2" />
              Clear
            </Button>
          )}
        </div>

        <Card className="h-[calc(100vh-220px)] flex flex-col">
          <div className="border-b py-2 px-4">
            <div className="flex items-center gap-1.5">
              <div className="w-1.5 h-1.5 rounded-full bg-green-500" />
              <span className="text-xs text-muted-foreground">
                Connected to Azure AI Foundry
              </span>
            </div>
          </div>

          <CardContent className="flex-1 overflow-y-auto p-4">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center">
                <div className="flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-[#00A693] to-[#008577] mb-4">
                  <Sparkles className="h-7 w-7 text-white" />
                </div>
                <h2 className="text-lg font-medium mb-2">
                  How can I help you today?
                </h2>
                <p className="text-sm text-muted-foreground max-w-md mb-4">
                  I can help you navigate the platform, explain features, guide you through workflows,
                  and query your data like tasks, agents, and meetings.
                </p>

                {/* HMLR Memory System Feature Highlight */}
                <div className="bg-gradient-to-r from-[#00A693]/10 to-[#008577]/10 border border-[#00A693]/20 rounded-lg p-4 max-w-lg mb-6">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-2 h-2 rounded-full bg-[#00A693] animate-pulse" />
                    <span className="text-xs font-medium text-[#00A693] uppercase tracking-wide">New: Intelligent Memory</span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    I now remember context across your conversations. I learn facts you share,
                    track topic switches seamlessly, and recall previous discussions to provide
                    more personalized and contextual assistance.
                  </p>
                  <div className="flex flex-wrap gap-2 mt-3">
                    <span className="text-xs px-2 py-1 bg-background rounded-md border">Topic Tracking</span>
                    <span className="text-xs px-2 py-1 bg-background rounded-md border">Fact Learning</span>
                    <span className="text-xs px-2 py-1 bg-background rounded-md border">Context Resumption</span>
                  </div>
                </div>

                <GuideSuggestionBar
                  suggestions={suggestions}
                  onSelect={sendMessage}
                  className="max-w-lg justify-center"
                />
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((message, index) => (
                  <div
                    key={message.id}
                    ref={index === messages.length - 1 ? lastMessageRef : null}
                  >
                    <GuideChatMessage
                      message={message}
                      onExecuteAction={executeAction}
                    />
                  </div>
                ))}
                {isLoading && <GuideTypingIndicator />}
              </div>
            )}
          </CardContent>

          <div className="border-t p-4">
            {error && (
              <div className="mb-3 p-2 bg-destructive/10 border border-destructive/20 rounded-lg flex items-center justify-between">
                <p className="text-sm text-destructive">{error}</p>
                <Button variant="ghost" size="sm" onClick={dismissError}>
                  Dismiss
                </Button>
              </div>
            )}
            <GuideChatInput
              onSend={sendMessage}
              isLoading={isLoading}
              placeholder="Ask about meetings, tasks, agents, or decisions..."
              autoFocus
            />
            <p className="text-xs text-muted-foreground mt-2">
              Press Enter to send, Shift+Enter for new line
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
}
