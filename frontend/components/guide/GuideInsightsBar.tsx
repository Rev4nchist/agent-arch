'use client';

import React from 'react';
import { AlertTriangle, Info, Zap, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { InsightItem } from '@/lib/api';
import { cn } from '@/lib/utils';

interface GuideInsightsBarProps {
  insights: InsightItem[];
  isLoading: boolean;
  onDismiss: (id: string) => void;
  onAction: (query: string) => void;
  compact?: boolean;
}

const typeIcons = {
  warning: AlertTriangle,
  info: Info,
  action: Zap,
};

const typeColors = {
  warning: 'border-amber-500/30 bg-amber-500/10 text-amber-700 dark:text-amber-400',
  info: 'border-blue-500/30 bg-blue-500/10 text-blue-700 dark:text-blue-400',
  action: 'border-[#00A693]/30 bg-[#00A693]/10 text-[#00A693]',
};

export function GuideInsightsBar({
  insights,
  isLoading,
  onDismiss,
  onAction,
  compact = false,
}: GuideInsightsBarProps) {
  if (isLoading) {
    return (
      <div className="px-3 py-2">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <div className="w-3 h-3 rounded-full border-2 border-[#00A693] border-t-transparent animate-spin" />
          <span>Loading insights...</span>
        </div>
      </div>
    );
  }

  if (insights.length === 0) return null;

  return (
    <div className={cn('space-y-2', compact ? 'px-2 py-2' : 'px-3 py-2')}>
      <div className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
        Quick Insights
      </div>
      <div className={cn('space-y-1.5', compact && 'max-h-[120px] overflow-y-auto')}>
        {insights.slice(0, compact ? 2 : 4).map((insight) => {
          const Icon = typeIcons[insight.type];
          return (
            <div
              key={insight.id}
              className={cn(
                'flex items-start gap-2 p-2 rounded-lg border transition-colors',
                typeColors[insight.type],
                'group'
              )}
            >
              <Icon className={cn('flex-shrink-0 mt-0.5', compact ? 'w-3 h-3' : 'w-4 h-4')} />
              <div className="flex-1 min-w-0">
                <div className={cn('font-medium', compact ? 'text-xs' : 'text-sm')}>
                  {insight.title}
                  {insight.count !== undefined && (
                    <span className="ml-1 opacity-80">({insight.count})</span>
                  )}
                </div>
                {!compact && (
                  <div className="text-xs opacity-80 mt-0.5">{insight.description}</div>
                )}
                {insight.action_query && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onAction(insight.action_query!)}
                    className={cn(
                      'h-auto p-0 mt-1 text-xs font-medium underline-offset-2 hover:underline',
                      insight.type === 'action' && 'text-[#00A693]',
                      insight.type === 'warning' && 'text-amber-700 dark:text-amber-400',
                      insight.type === 'info' && 'text-blue-700 dark:text-blue-400'
                    )}
                  >
                    {insight.action_label || 'View details'}
                  </Button>
                )}
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => onDismiss(insight.id)}
                className="opacity-0 group-hover:opacity-100 h-5 w-5 -mt-0.5 -mr-0.5 transition-opacity"
              >
                <X className="w-3 h-3" />
              </Button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
