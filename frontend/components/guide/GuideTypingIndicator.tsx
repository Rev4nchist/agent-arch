'use client';

import React from 'react';
import { Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

interface GuideTypingIndicatorProps {
  compact?: boolean;
}

export function GuideTypingIndicator({ compact = false }: GuideTypingIndicatorProps) {
  return (
    <div className={cn('flex gap-3', compact && 'gap-2')}>
      <div
        className={cn(
          'flex-shrink-0 rounded-full flex items-center justify-center',
          'bg-gradient-to-br from-violet-500 to-purple-600 text-white',
          compact ? 'w-7 h-7' : 'w-8 h-8'
        )}
      >
        <Sparkles className={compact ? 'w-3.5 h-3.5' : 'w-4 h-4'} />
      </div>

      <div
        className={cn(
          'bg-muted rounded-2xl rounded-tl-sm flex items-center gap-1',
          compact ? 'px-3 py-2' : 'px-4 py-3'
        )}
      >
        <span
          className="w-2 h-2 bg-muted-foreground/60 rounded-full animate-bounce"
          style={{ animationDelay: '0ms' }}
        />
        <span
          className="w-2 h-2 bg-muted-foreground/60 rounded-full animate-bounce"
          style={{ animationDelay: '150ms' }}
        />
        <span
          className="w-2 h-2 bg-muted-foreground/60 rounded-full animate-bounce"
          style={{ animationDelay: '300ms' }}
        />
      </div>
    </div>
  );
}
