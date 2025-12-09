'use client';

import React from 'react';
import { ArrowRight, Filter, ExternalLink, Search, Download, Eye, List, Bell } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ActionSuggestion } from '@/lib/api';
import { cn } from '@/lib/utils';

interface GuideActionSuggestionsProps {
  suggestions: ActionSuggestion[];
  onExecute: (action: ActionSuggestion) => void;
  compact?: boolean;
}

const actionIcons = {
  query: Search,
  filter: Filter,
  navigate: ExternalLink,
  show_detail: Eye,
  view: List,
  export: Download,
  create: ArrowRight,
  open_loop: Bell,
};

const actionColors = {
  query: 'hover:bg-blue-500/10 hover:text-blue-600 dark:hover:text-blue-400',
  filter: 'hover:bg-purple-500/10 hover:text-purple-600 dark:hover:text-purple-400',
  navigate: 'hover:bg-[#00A693]/10 hover:text-[#00A693]',
  show_detail: 'hover:bg-amber-500/10 hover:text-amber-600 dark:hover:text-amber-400',
  view: 'hover:bg-indigo-500/10 hover:text-indigo-600 dark:hover:text-indigo-400',
  export: 'hover:bg-green-500/10 hover:text-green-600 dark:hover:text-green-400',
  create: 'hover:bg-gray-500/10',
  open_loop: 'hover:bg-orange-500/10 hover:text-orange-600 dark:hover:text-orange-400',
};

export function GuideActionSuggestions({
  suggestions,
  onExecute,
  compact = false,
}: GuideActionSuggestionsProps) {
  // Split suggestions: open_loop chips first, then regular (exclude create/filter)
  const openLoopActions = suggestions.filter((s) => s.action_type === 'open_loop');
  const regularActions = suggestions.filter(
    (s) => s.action_type !== 'create' && s.action_type !== 'filter' && s.action_type !== 'open_loop'
  );

  // Apply different limits: open_loop (2 page / 1 modal) + regular (6 page / 3 modal)
  const openLoopLimit = compact ? 1 : 2;
  const regularLimit = compact ? 3 : 6;

  const displayActions = [
    ...openLoopActions.slice(0, openLoopLimit),
    ...regularActions.slice(0, regularLimit)
  ];

  if (displayActions.length === 0) return null;

  return (
    <div className={cn('flex flex-wrap gap-1.5', compact ? 'mt-2' : 'mt-3')}>
      {displayActions.map((action, index) => {
        const Icon = actionIcons[action.action_type] || ArrowRight;
        const colorClass = actionColors[action.action_type] || '';

        return (
          <Button
            key={`${action.action_type}-${index}`}
            variant="outline"
            size="sm"
            onClick={() => onExecute(action)}
            className={cn(
              'h-7 px-2 text-xs font-medium border-muted-foreground/20',
              'transition-colors duration-150',
              colorClass
            )}
          >
            <Icon className="w-3 h-3 mr-1" />
            {action.label}
          </Button>
        );
      })}
    </div>
  );
}
