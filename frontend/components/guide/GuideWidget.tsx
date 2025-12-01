'use client';

import React, { useEffect, useCallback } from 'react';
import { useGuide } from '@/components/providers/GuideProvider';
import { GuideWidgetTrigger } from './GuideWidgetTrigger';
import { GuideWidgetPanel } from './GuideWidgetPanel';

export function GuideWidget() {
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
        onClear={clearConversation}
        onDismissInsight={dismissInsight}
        onInsightAction={runInsightAction}
        onExecuteAction={executeAction}
      />
      <GuideWidgetTrigger
        isOpen={isWidgetOpen}
        onClick={toggleWidget}
      />
    </>
  );
}
