'use client';

import React from 'react';
import { Copy, Check, Database } from 'lucide-react';
import { ChatMessage, ActionSuggestion } from '@/lib/api';
import { cn } from '@/lib/utils';
import { GuideSourceBadge } from './GuideSourceBadge';
import { GuideActionSuggestions } from './GuideActionSuggestions';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface GuideChatMessageProps {
  message: ChatMessage;
  compact?: boolean;
  onExecuteAction?: (action: ActionSuggestion) => void;
}

function CodeBlock({ children, className }: { children: string; className?: string }) {
  const [copied, setCopied] = React.useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(children);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative group my-3">
      <pre className="bg-[#1e1e1e] text-[#d4d4d4] rounded-lg p-4 overflow-x-auto text-sm font-mono">
        <code className={className}>{children}</code>
      </pre>
      <button
        onClick={handleCopy}
        className="absolute top-2 right-2 p-1.5 rounded-md bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-white/20"
        title="Copy code"
      >
        {copied ? (
          <Check className="w-4 h-4 text-green-400" />
        ) : (
          <Copy className="w-4 h-4 text-gray-400" />
        )}
      </button>
    </div>
  );
}

export function GuideChatMessage({ message, compact = false, onExecuteAction }: GuideChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div
      className={cn(
        'flex w-full',
        isUser ? 'justify-end' : 'justify-start',
        compact ? 'py-2' : 'py-3'
      )}
    >
      <div
        className={cn(
          'flex flex-col',
          isUser ? 'items-end max-w-[85%]' : 'items-start max-w-full w-full'
        )}
      >
        {/* User message - minimal teal accent pill */}
        {isUser ? (
          <div className="bg-[#e8f5f1] text-[#1a1a1a] rounded-2xl px-4 py-2.5 text-[15px] leading-relaxed">
            {message.content}
          </div>
        ) : (
          /* Assistant message - clean, no background */
          <div className="w-full">
            {/* Subtle left border accent */}
            <div className={cn(
              "border-l-2 border-[#00A693]/30 pl-4",
              compact ? "pl-3" : "pl-4"
            )}>
              {/* Markdown rendered content */}
              <div className="prose prose-sm max-w-none text-[#1a1a1a] leading-relaxed">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    // Headings
                    h1: ({ children }) => (
                      <h1 style={{ fontWeight: 600 }} className="text-lg text-[#1a1a1a] mt-4 mb-2 first:mt-0">{children}</h1>
                    ),
                    h2: ({ children }) => (
                      <h2 style={{ fontWeight: 600 }} className="text-base text-[#1a1a1a] mt-3 mb-2 first:mt-0">{children}</h2>
                    ),
                    h3: ({ children }) => (
                      <h3 style={{ fontWeight: 600 }} className="text-sm text-[#1a1a1a] mt-2 mb-1 first:mt-0">{children}</h3>
                    ),
                    // Paragraphs
                    p: ({ children }) => (
                      <p className="text-[15px] text-[#1a1a1a] leading-[1.6] mb-3 last:mb-0">{children}</p>
                    ),
                    // Bold and italic
                    strong: ({ children }) => (
                      <strong style={{ fontWeight: 600 }} className="text-[#1a1a1a]">{children}</strong>
                    ),
                    em: ({ children }) => (
                      <em className="italic">{children}</em>
                    ),
                    // Lists
                    ul: ({ children }) => (
                      <ul className="list-none space-y-1.5 mb-3 last:mb-0">{children}</ul>
                    ),
                    ol: ({ children }) => (
                      <ol className="list-decimal list-inside space-y-1.5 mb-3 last:mb-0 marker:text-[#6b7280]">{children}</ol>
                    ),
                    li: ({ children }) => (
                      <li className="text-[15px] text-[#1a1a1a] leading-[1.6] flex items-start gap-2">
                        <span className="text-[#00A693] mt-1.5 text-xs">●</span>
                        <span className="flex-1">{children}</span>
                      </li>
                    ),
                    // Inline code
                    code: ({ className, children, ...props }) => {
                      const isBlock = className?.includes('language-');
                      if (isBlock) {
                        return <CodeBlock className={className}>{String(children)}</CodeBlock>;
                      }
                      return (
                        <code className="bg-[#f3f4f6] text-[#1a1a1a] px-1.5 py-0.5 rounded text-sm font-mono" {...props}>
                          {children}
                        </code>
                      );
                    },
                    // Code blocks
                    pre: ({ children }) => <>{children}</>,
                    // Links
                    a: ({ href, children }) => (
                      <a
                        href={href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-[#00A693] hover:underline"
                      >
                        {children}
                      </a>
                    ),
                    // Blockquotes
                    blockquote: ({ children }) => (
                      <blockquote className="border-l-2 border-[#e5e7eb] pl-3 italic text-[#6b7280] my-3">
                        {children}
                      </blockquote>
                    ),
                    // Horizontal rules
                    hr: () => <hr className="border-[#e5e7eb] my-4" />,
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              </div>

              {/* Sources - minimal badges */}
              {message.sources && message.sources.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-3 pt-3 border-t border-[#e5e7eb]">
                  {message.sources.map((source) => (
                    <GuideSourceBadge key={source.id} source={source} compact={compact} />
                  ))}
                </div>
              )}

              {/* Data basis indicator */}
              {message.data_basis && message.data_basis.items_shown > 0 && (
                <div className="flex items-center gap-1.5 mt-2 text-xs text-[#6b7280]">
                  <Database className="w-3 h-3" />
                  <span>
                    Based on {message.data_basis.items_shown === message.data_basis.total_items
                      ? `${message.data_basis.total_items} items`
                      : `${message.data_basis.items_shown} of ${message.data_basis.total_items} items`
                    }
                  </span>
                </div>
              )}

              {/* Quick actions */}
              {message.suggestions && message.suggestions.length > 0 && onExecuteAction && (
                <div className="mt-3">
                  <GuideActionSuggestions
                    suggestions={message.suggestions}
                    onExecute={onExecuteAction}
                    compact={compact}
                  />
                </div>
              )}
            </div>
          </div>
        )}

        {/* Timestamp - subtle */}
        <span className={cn(
          "text-[#9ca3af] mt-1.5",
          compact ? "text-[10px]" : "text-xs",
          isUser ? "mr-1" : "ml-4"
        )}>
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
