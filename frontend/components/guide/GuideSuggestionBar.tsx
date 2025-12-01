'use client';

import React from 'react';
import { Suggestion } from '@/lib/guide-context';
import { GuideSuggestionChip } from './GuideSuggestionChip';
import { cn } from '@/lib/utils';

interface GuideSuggestionBarProps {
  suggestions: Suggestion[];
  onSelect: (text: string) => void;
  compact?: boolean;
  className?: string;
}

export function GuideSuggestionBar({
  suggestions,
  onSelect,
  compact = false,
  className,
}: GuideSuggestionBarProps) {
  if (suggestions.length === 0) return null;

  return (
    <div className={cn('w-full', className)}>
      <div
        className={cn(
          'flex gap-2 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-muted scrollbar-track-transparent',
          compact && 'gap-1.5'
        )}
      >
        {suggestions.map((suggestion) => (
          <GuideSuggestionChip
            key={suggestion.id}
            suggestion={suggestion}
            onClick={onSelect}
            compact={compact}
          />
        ))}
      </div>
    </div>
  );
}
