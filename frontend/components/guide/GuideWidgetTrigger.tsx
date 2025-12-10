'use client';

import React from 'react';
import { Sparkles, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface GuideWidgetTriggerProps {
  isOpen: boolean;
  onClick: () => void;
  hasUnread?: boolean;
}

export function GuideWidgetTrigger({
  isOpen,
  onClick,
  hasUnread = false,
}: GuideWidgetTriggerProps) {
  return (
    <Button
      onClick={onClick}
      size="icon-lg"
      className={cn(
        'fixed bottom-20 right-4 lg:bottom-6 lg:right-6 z-40 rounded-full shadow-lg',
        'w-14 h-14 transition-all duration-300',
        'bg-gradient-to-br from-[#00A693] to-[#008577] hover:from-[#008577] hover:to-[#006B5A]',
        'text-white border-0',
        isOpen && 'rotate-90'
      )}
      aria-label={isOpen ? 'Close AI Guide' : 'Open AI Guide'}
    >
      {isOpen ? (
        <X className="w-6 h-6" />
      ) : (
        <>
          <Sparkles className="w-6 h-6" />
          {hasUnread && (
            <span className="absolute top-0 right-0 w-3 h-3 bg-red-500 rounded-full border-2 border-white" />
          )}
        </>
      )}
    </Button>
  );
}
