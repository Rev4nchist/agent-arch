'use client';

import { useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Sparkles, MessageSquare, Trash2 } from 'lucide-react';
import { useGuide } from '@/components/providers/GuideProvider';
import {
  GuideChatMessage,
  GuideChatInput,
  GuideTypingIndicator,
  GuideSuggestionBar,
} from '@/components/guide';

export default function GuidePage() {
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
    // Only scroll when a NEW message appears, not during streaming
    if (messages.length > prevMessageCount.current) {
      // Scroll the new message into view at the top
      lastMessageRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    prevMessageCount.current = messages.length;
  }, [messages.length]);

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
          <CardHeader className="border-b py-3">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-500" />
              <span className="text-sm text-muted-foreground">
                Connected to Azure AI Foundry
              </span>
            </div>
          </CardHeader>

          <CardContent className="flex-1 overflow-y-auto p-4">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-[#00A693] to-[#008577] mb-4">
                  <MessageSquare className="h-8 w-8 text-white" />
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
              Press Enter to send, Shift+Enter for new line • Ctrl+K opens widget
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
}
