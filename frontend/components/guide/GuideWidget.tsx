'use client';

import React, { useEffect, useCallback } from 'react';
import { usePathname } from 'next/navigation';
import { useGuide } from '@/components/providers/GuideProvider';
import { GuideWidgetTrigger } from './GuideWidgetTrigger';
import { GuideWidgetPanel } from './GuideWidgetPanel';

const HIDDEN_ON_ROUTES = ['/landing'];

export function GuideWidget() {
  const pathname = usePathname();
  const {
    messages,
    isLoading,
    isWidgetOpen,
    isMinimized,
    isExpanded,
    currentPage,
    suggestions,
    insights,
    insightsLoading,
    sendMessage,
    clearConversation,
    toggleWidget,
    minimizeWidget,
    expandWidget,
    toggleExpanded,
    dismissInsight,
    runInsightAction,
    executeAction,
  } = useGuide();

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        toggleWidget();
      }
      if (e.key === 'Escape' && isWidgetOpen) {
        toggleWidget();
      }
    },
    [toggleWidget, isWidgetOpen]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  // Hide widget on landing page
  if (HIDDEN_ON_ROUTES.includes(pathname)) {
    return null;
  }

  return (
    <>
      <GuideWidgetPanel
        isOpen={isWidgetOpen}
        isMinimized={isMinimized}
        isExpanded={isExpanded}
        messages={messages}
        suggestions={suggestions}
        insights={insights}
        insightsLoading={insightsLoading}
        isLoading={isLoading}
        pageName={currentPage.displayName}
        onSend={sendMessage}
        onMinimize={minimizeWidget}
        onExpand={expandWidget}
        onToggleExpanded={toggleExpanded}
        onClose={toggleWidget}
        onClear={clearConversation}
        onDismissInsight={dismissInsight}
        onInsightAction={runInsightAction}
        onExecuteAction={executeAction}
      />
      {!isExpanded && !isWidgetOpen && (
        <GuideWidgetTrigger
          isOpen={isWidgetOpen}
          onClick={toggleWidget}
        />
      )}
    </>
  );
}
