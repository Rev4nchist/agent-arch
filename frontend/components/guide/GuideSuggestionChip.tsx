'use client';

import React from 'react';
import { Suggestion } from '@/lib/guide-context';
import { cn } from '@/lib/utils';

interface GuideSuggestionChipProps {
  suggestion: Suggestion;
  onClick: (text: string) => void;
  compact?: boolean;
}

export function GuideSuggestionChip({
  suggestion,
  onClick,
  compact = false,
}: GuideSuggestionChipProps) {
  return (
    <button
      onClick={() => onClick(suggestion.text)}
      className={cn(
        'inline-flex items-center whitespace-nowrap rounded-full border border-border/50',
        'bg-background hover:bg-accent hover:border-accent',
        'text-muted-foreground hover:text-foreground',
        'transition-colors cursor-pointer',
        compact ? 'px-2.5 py-1 text-xs' : 'px-3 py-1.5 text-sm'
      )}
    >
      {suggestion.text}
    </button>
  );
}
