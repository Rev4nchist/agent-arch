'use client';

import React, { useState, useRef, useCallback, KeyboardEvent } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface GuideChatInputProps {
  onSend: (message: string) => void;
  isLoading?: boolean;
  placeholder?: string;
  compact?: boolean;
  autoFocus?: boolean;
}

export function GuideChatInput({
  onSend,
  isLoading = false,
  placeholder = 'Ask me anything...',
  compact = false,
  autoFocus = false,
}: GuideChatInputProps) {
  const [value, setValue] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = useCallback(() => {
    const trimmed = value.trim();
    if (!trimmed || isLoading) return;
    onSend(trimmed);
    setValue('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  }, [value, isLoading, onSend]);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit]
  );

  const handleInput = useCallback(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, compact ? 80 : 120)}px`;
    }
  }, [compact]);

  return (
    <div
      className={cn(
        'flex items-end gap-2 border rounded-xl bg-background',
        compact ? 'p-2' : 'p-3'
      )}
    >
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        onInput={handleInput}
        placeholder={placeholder}
        disabled={isLoading}
        autoFocus={autoFocus}
        rows={1}
        className={cn(
          'flex-1 resize-none bg-transparent border-0 outline-none placeholder:text-muted-foreground',
          compact ? 'text-sm min-h-[28px] max-h-[80px]' : 'text-base min-h-[36px] max-h-[120px]'
        )}
      />
      <Button
        onClick={handleSubmit}
        disabled={!value.trim() || isLoading}
        size={compact ? 'icon-sm' : 'icon'}
        className="flex-shrink-0 rounded-lg"
      >
        {isLoading ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <Send className="w-4 h-4" />
        )}
      </Button>
    </div>
  );
}
