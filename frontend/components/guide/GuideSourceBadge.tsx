'use client';

import React from 'react';
import { FileText, CheckSquare, Bot, Shield } from 'lucide-react';
import { ChatSource } from '@/lib/api';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface GuideSourceBadgeProps {
  source: ChatSource;
  compact?: boolean;
}

const sourceIcons: Record<ChatSource['type'], React.ElementType> = {
  meeting: FileText,
  task: CheckSquare,
  agent: Bot,
  governance: Shield,
};

const sourceColors: Record<ChatSource['type'], string> = {
  meeting: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  task: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
  agent: 'bg-violet-100 text-violet-700 dark:bg-violet-900/30 dark:text-violet-400',
  governance: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400',
};

export function GuideSourceBadge({ source, compact = false }: GuideSourceBadgeProps) {
  const Icon = sourceIcons[source.type] || FileText;
  const colorClass = sourceColors[source.type] || sourceColors.governance;

  return (
    <Badge
      variant="outline"
      className={cn(
        'border-transparent cursor-default',
        colorClass,
        compact ? 'text-[10px] px-1.5 py-0' : 'text-xs'
      )}
    >
      <Icon className={compact ? 'w-2.5 h-2.5' : 'w-3 h-3'} />
      <span className="truncate max-w-[120px]">{source.title}</span>
    </Badge>
  );
}
