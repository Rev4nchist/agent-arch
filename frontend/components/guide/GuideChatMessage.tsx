'use client';

import React from 'react';
import { User, Sparkles, Database } from 'lucide-react';
import { ChatMessage, ChatSource, DataBasis, ActionSuggestion } from '@/lib/api';
import { cn } from '@/lib/utils';
import { GuideSourceBadge } from './GuideSourceBadge';
import { GuideActionSuggestions } from './GuideActionSuggestions';

interface GuideChatMessageProps {
  message: ChatMessage;
  compact?: boolean;
  onExecuteAction?: (action: ActionSuggestion) => void;  // Phase 5.4
}

export function GuideChatMessage({ message, compact = false, onExecuteAction }: GuideChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div
      className={cn(
        'flex gap-3',
        isUser ? 'flex-row-reverse' : 'flex-row',
        compact ? 'gap-2' : 'gap-3'
      )}
    >
      <div
        className={cn(
          'flex-shrink-0 rounded-full flex items-center justify-center',
          compact ? 'w-7 h-7' : 'w-8 h-8',
          isUser
            ? 'bg-[#1E3A5F] text-white'
            : 'bg-gradient-to-br from-[#00A693] to-[#008577] text-white'
        )}
      >
        {isUser ? (
          <User className={compact ? 'w-3.5 h-3.5' : 'w-4 h-4'} />
        ) : (
          <Sparkles className={compact ? 'w-3.5 h-3.5' : 'w-4 h-4'} />
        )}
      </div>

      <div
        className={cn(
          'flex flex-col max-w-[80%]',
          isUser ? 'items-end' : 'items-start'
        )}
      >
        <div
          className={cn(
            'rounded-2xl px-4 py-2',
            compact ? 'px-3 py-1.5 text-sm' : 'px-4 py-2',
            isUser
              ? 'bg-[#1E3A5F] text-white rounded-tr-sm'
              : 'bg-muted rounded-tl-sm'
          )}
        >
          <p className="whitespace-pre-wrap break-words">{message.content}</p>
        </div>

        {message.sources && message.sources.length > 0 && (
          <div className={cn('flex flex-wrap gap-1.5 mt-2', compact && 'gap-1')}>
            {message.sources.map((source) => (
              <GuideSourceBadge key={source.id} source={source} compact={compact} />
            ))}
          </div>
        )}

        {!isUser && message.data_basis && message.data_basis.items_shown > 0 && (
          <div
            className={cn(
              'flex items-center gap-1.5 mt-1.5 px-2 py-1 rounded-md bg-muted/50 border border-border/50',
              compact ? 'text-[10px]' : 'text-xs'
            )}
            title={`Entity types: ${message.data_basis.entity_types.join(', ')}`}
          >
            <Database className={compact ? 'w-3 h-3' : 'w-3.5 h-3.5'} />
            <span className="text-muted-foreground">
              Based on {message.data_basis.items_shown === message.data_basis.total_items
                ? `${message.data_basis.total_items} items`
                : `${message.data_basis.items_shown} of ${message.data_basis.total_items} items`
              }
            </span>
          </div>
        )}

        {/* Phase 5.4: Quick action suggestions */}
        {!isUser && message.suggestions && message.suggestions.length > 0 && onExecuteAction && (
          <GuideActionSuggestions
            suggestions={message.suggestions}
            onExecute={onExecuteAction}
            compact={compact}
          />
        )}

        <span
          className={cn(
            'text-muted-foreground mt-1',
            compact ? 'text-[10px]' : 'text-xs'
          )}
        >
          {formatTime(message.timestamp)}
        </span>
      </div>
    </div>
  );
}

function formatTime(date: Date): string {
  return new Date(date).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });
}
