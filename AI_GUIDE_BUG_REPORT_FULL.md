# AI Guide Widget Bug Report - Full Engineering Deep Dive

**Date**: December 8, 2025
**Status**: UNRESOLVED - Requires Senior Engineer Investigation
**Project**: agent-arch (Agent Architecture Portal)

---

## Executive Summary

Two persistent bugs in the AI Guide chat widget have resisted multiple fix attempts. This document provides all technical context, code analysis, attempted solutions, and remaining hypotheses for a senior engineer to investigate.

---

## Bug 1: Scroll-to-Bottom Button Never Appears

### Symptom
When a user scrolls up in the chat message area, the "Jump to bottom" pill button should appear. **It never appears**, regardless of scroll position.

### Expected Behavior
- User scrolls up in message area → button appears
- User clicks button → scrolls to bottom, button hides
- New messages while scrolled up → button shows "New content" with animation

### Actual Behavior
- Button **never appears** under any circumstances
- `isAtBottom` state appears to always be `true`

---

### Relevant Files

| File | Purpose |
|------|---------|
| `frontend/hooks/useSmartAutoScroll.ts` | Hook managing scroll state and listener |
| `frontend/components/guide/GuideWidgetPanel.tsx` | Main widget layout, uses the hook |
| `frontend/components/guide/ScrollToBottomButton.tsx` | The button component itself |

---

### Code Analysis

#### `useSmartAutoScroll.ts` (CURRENT - after attempted fix)

```typescript
'use client';

import { useRef, useState, useEffect, useCallback, RefCallback } from 'react';

interface UseSmartAutoScrollOptions {
  isStreaming?: boolean;
  threshold?: number;
}

export function useSmartAutoScroll(options: UseSmartAutoScrollOptions = {}) {
  const { isStreaming = false, threshold = 100 } = options;

  const [container, setContainer] = useState<HTMLDivElement | null>(null);
  const [isAtBottom, setIsAtBottom] = useState(true);  // ← STARTS TRUE
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Callback ref - should trigger state update when DOM node mounts
  const containerRef: RefCallback<HTMLDivElement> = useCallback((node) => {
    setContainer(node);  // ← Should trigger re-render and effect
  }, []);

  const checkIfAtBottom = useCallback(() => {
    if (!container) return;
    const { scrollTop, scrollHeight, clientHeight } = container;
    const distanceFromBottom = scrollHeight - scrollTop - clientHeight;
    setIsAtBottom(distanceFromBottom <= threshold);
  }, [container, threshold]);

  // Effect to attach scroll listener
  useEffect(() => {
    if (!container) return;

    const handleScroll = () => {
      checkIfAtBottom();
    };

    container.addEventListener('scroll', handleScroll, { passive: true });
    checkIfAtBottom();  // Initial check

    return () => {
      container.removeEventListener('scroll', handleScroll);
    };
  }, [container, checkIfAtBottom]);

  useEffect(() => {
    if (isAtBottom && isStreaming && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [isAtBottom, isStreaming]);

  const scrollToBottom = useCallback((behavior: ScrollBehavior = 'smooth') => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior });
      setIsAtBottom(true);
    }
  }, []);

  return {
    containerRef,
    messagesEndRef,
    isAtBottom,
    scrollToBottom
  };
}
```

#### `GuideWidgetPanel.tsx` (lines 172-216)

```tsx
{/* Messages area wrapper - relative for absolute button positioning */}
<div className="flex-1 relative min-h-0">
  {/* Scrollable content */}
  <div ref={containerRef} className="h-full overflow-y-auto bg-white">
    {messages.length === 0 ? (
      <div className="flex flex-col items-center justify-center h-full text-center px-8 py-12">
        {/* Empty state */}
      </div>
    ) : (
      <div className="px-4 py-2 pb-16">
        {messages.map((msg) => (
          <GuideChatMessage
            key={msg.id}
            message={msg}
            compact={!isExpanded}
            onExecuteAction={onExecuteAction}
          />
        ))}
        {isLoading && (
          <div className="py-3">
            <GuideTypingIndicator compact={!isExpanded} />
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
    )}
  </div>

  {/* Scroll button - OUTSIDE scroll container, positioned absolutely */}
  <div className="absolute bottom-4 left-0 right-0 flex justify-center pointer-events-none z-10">
    <div className="pointer-events-auto">
      <ScrollToBottomButton
        visible={!isAtBottom && messages.length > 0}  // ← VISIBILITY LOGIC
        onClick={() => scrollToBottom()}
        isStreaming={isLoading}
      />
    </div>
  </div>
</div>
```

#### `ScrollToBottomButton.tsx` (Full Component)

```tsx
'use client';

import { ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ScrollToBottomButtonProps {
  visible: boolean;
  onClick: () => void;
  isStreaming?: boolean;
}

export function ScrollToBottomButton({
  visible,
  onClick,
  isStreaming
}: ScrollToBottomButtonProps) {
  const buttonText = isStreaming ? 'New content' : 'Jump to bottom';

  return (
    <button
      onClick={onClick}
      className={cn(
        "z-10",
        "flex items-center gap-1.5 px-3 py-1.5 rounded-full",
        "bg-white/90 backdrop-blur-sm text-gray-600 border border-gray-200 shadow-md",
        "transition-all duration-200 ease-out",
        "hover:bg-gray-50 hover:text-gray-800 hover:shadow-lg",
        "focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-1",
        visible
          ? "opacity-100 translate-y-0"
          : "opacity-0 translate-y-4 pointer-events-none"  // ← HIDDEN WHEN !visible
      )}
      aria-label={buttonText}
    >
      {isStreaming && (
        <span className="flex gap-0.5">
          <span className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
          <span className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
          <span className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
        </span>
      )}
      <ChevronDown className="h-4 w-4" />
      <span className="text-xs font-medium">{buttonText}</span>
    </button>
  );
}
```

---

### What Was Tried & Why It Didn't Work

#### Attempt 1: DOM Restructuring
**Theory**: Button was inside scroll container, getting scrolled away with content.
**Fix**: Moved button outside scroll container with absolute positioning within a relative parent.
**Result**: Button STILL doesn't appear. DOM structure is now correct but issue persists.

#### Attempt 2: Callback Ref Pattern
**Theory**: Original `useRef` didn't trigger effect re-run when container mounted because refs don't cause re-renders.
**Fix**: Changed to `useState` + callback ref pattern so:
  - `containerRef` is a callback that sets state
  - State change triggers re-render
  - Effect depends on `container` state and re-runs when it changes
**Result**: Fix is applied in code, but bug persists. Possible reasons:
  - Callback ref isn't being called when expected
  - State update isn't triggering effect
  - Effect runs but scroll listener doesn't fire
  - `checkIfAtBottom` calculation returns wrong value
  - CSS preventing actual scroll

---

### Remaining Hypotheses

1. **Callback ref not being invoked**: The `containerRef` callback may not fire when expected in Next.js/React 19 due to timing differences

2. **Scroll container not actually scrollable**: `scrollHeight - clientHeight` may equal 0 if:
   - Content doesn't overflow the container
   - CSS `overflow` is being overridden somewhere
   - Container height isn't constrained properly

3. **Threshold always satisfied**: If `scrollHeight === clientHeight`, then `distanceFromBottom = 0`, which is `<= threshold (100)`, so `isAtBottom` stays `true`

4. **React 19 / Next.js 16 behavior change**: Ref callback timing or effect execution order may differ from React 18

5. **Hot Module Reload caching**: Dev server may be serving cached/old version of the hook

---

### Suggested Debug Steps

1. **Add console.logs to trace execution**:
```typescript
const containerRef: RefCallback<HTMLDivElement> = useCallback((node) => {
  console.log('[DEBUG] containerRef called with:', node);
  setContainer(node);
}, []);

useEffect(() => {
  console.log('[DEBUG] Effect running, container:', container);
  if (!container) return;
  console.log('[DEBUG] Attaching scroll listener');

  const { scrollTop, scrollHeight, clientHeight } = container;
  console.log('[DEBUG] Initial dimensions:', { scrollTop, scrollHeight, clientHeight });
}, [container, checkIfAtBottom]);

const checkIfAtBottom = useCallback(() => {
  if (!container) return;
  const { scrollTop, scrollHeight, clientHeight } = container;
  const distanceFromBottom = scrollHeight - scrollTop - clientHeight;
  console.log('[DEBUG] Scroll check:', { scrollTop, scrollHeight, clientHeight, distanceFromBottom, threshold });
  setIsAtBottom(distanceFromBottom <= threshold);
}, [container, threshold]);
```

2. **Verify container is scrollable in browser DevTools**:
```javascript
// Find the scroll container
const container = document.querySelector('.overflow-y-auto');
console.log('scrollHeight:', container.scrollHeight);
console.log('clientHeight:', container.clientHeight);
console.log('Is scrollable:', container.scrollHeight > container.clientHeight);

// Try manual scroll
container.scrollTop = 0;
```

3. **Check if isAtBottom ever changes**:
```typescript
useEffect(() => {
  console.log('[DEBUG] isAtBottom changed to:', isAtBottom);
}, [isAtBottom]);
```

4. **Force button visible to confirm it renders**:
```tsx
<ScrollToBottomButton
  visible={true}  // Force visible
  onClick={() => scrollToBottom()}
  isStreaming={isLoading}
/>
```

5. **Check CSS in DevTools**: Inspect the scroll container element and verify:
   - `overflow-y: auto` is applied
   - Height is constrained (not `auto` or unconstrained)
   - No parent is preventing overflow

---

## Bug 2: Action Chips Do Nothing When Clicked

### Symptom
The "Suggested next actions" chips (buttons) below AI responses do nothing when clicked for certain action types.

### Expected Behavior
- Click chip → either navigate to a page, OR send the label as a new chat query

### Actual Behavior
- Some chips work (query type, navigate with valid params)
- Some chips do nothing (silent failure, no console errors, no visual feedback)

---

### Relevant Files

| File | Purpose |
|------|---------|
| `frontend/components/providers/GuideProvider.tsx` | Contains `executeAction` function (lines 348-393) |
| `frontend/components/guide/GuideActionSuggestions.tsx` | Renders the action chips |
| `frontend/components/guide/GuideChatMessage.tsx` | Parent that passes `onExecuteAction` prop |
| `frontend/lib/api.ts` | `ActionSuggestion` type definition |

---

### Code Analysis

#### `GuideProvider.tsx` - executeAction function (lines 348-393)

```typescript
const executeAction = useCallback((action: ActionSuggestion) => {
  // Validate action has usable data
  const queryText = action.params?.query?.toString() || action.label;

  const fallbackToQuery = () => {
    if (queryText) {
      sendMessage(queryText);
    } else {
      console.warn('[Guide] Action has no query text:', action);
    }
  };

  switch (action.action_type) {
    case 'query':
    case 'create':
    case 'export':
      fallbackToQuery();
      break;

    case 'navigate':
      if (action.params?.page) {
        router.push(`/${action.params.page}`);
      } else if (action.params?.id && action.params?.entity) {
        router.push(`/${action.params.entity}s/${action.params.id}`);
      } else {
        fallbackToQuery();
      }
      break;

    case 'filter':
      fallbackToQuery();  // ← FIXED: Previously dispatched unheard CustomEvent
      break;

    case 'show_detail':
      if (action.params?.id && action.params?.entity) {
        router.push(`/${action.params.entity}s/${action.params.id}`);
      } else {
        fallbackToQuery();
      }
      break;

    default:
      fallbackToQuery();
  }
}, [router, sendMessage]);
```

#### `GuideActionSuggestions.tsx` (lines 40-86)

```typescript
export function GuideActionSuggestions({
  suggestions,
  onExecute,
  compact = false,
}: GuideActionSuggestionsProps) {
  if (suggestions.length === 0) return null;

  return (
    <div className={cn(compact ? 'mt-2' : 'mt-3')}>
      {!compact && (
        <div className="flex items-center gap-1.5 mb-2">
          <Sparkles className="w-3 h-3 text-[#00A693]" />
          <span className="text-xs font-medium text-muted-foreground">
            Suggested next actions
          </span>
        </div>
      )}
      <div className="flex flex-wrap gap-1.5">
        {suggestions.slice(0, compact ? 2 : 6).map((action, index) => {
          const Icon = getIconForAction(action);
          const colorClass = actionColors[action.action_type] || '';

          return (
            <Button
              key={`${action.action_type}-${index}`}
              variant="outline"
              size="sm"
              onClick={() => onExecute(action)}  // ← This calls executeAction
              className={cn(
                'h-7 px-2 text-xs font-medium',
                'transition-colors duration-150',
                cn('border-muted-foreground/20', colorClass)
              )}
            >
              <Icon className="w-3 h-3 mr-1" />
              {action.label}
            </Button>
          );
        })}
      </div>
    </div>
  );
}
```

#### Data Flow (Prop Chain)

```
GuideProvider (context)
  └─ provides: executeAction
      │
GuideWidgetPanel
  └─ prop: onExecuteAction={executeAction}
      │
GuideChatMessage
  └─ prop: onExecuteAction={onExecuteAction}
      │
GuideActionSuggestions
  └─ prop: onExecute={onExecuteAction}
      └─ Button onClick={() => onExecute(action)}
```

---

### What Was Tried & Why It Didn't Work

#### Attempt 1: Remove Filter Event Dispatch
**Theory**: The `filter` action case was dispatching a `CustomEvent('guide-filter-action')` that nothing in the app was listening to, causing silent failure.
**Fix**: Changed `filter` case to always call `fallbackToQuery()` instead of dispatching the event.
**Result**: Fix is applied in code. Filter actions should now work, but other action types may still have issues.

---

### Remaining Hypotheses

1. **Action object missing required data**: Backend may return actions without `params.query` or with empty/undefined `label`

2. **`sendMessage` failing silently**: The `sendMessage` function from context may not be executing properly

3. **Prop drilling broken**: `onExecuteAction` prop may not be passed correctly at some point in the component tree

4. **Action type not in switch**: Backend returns action types not handled in the switch statement (would hit `default` case)

5. **Button click event stopped**: Some parent element may be calling `event.stopPropagation()` or `event.preventDefault()`

6. **Empty queryText**: If both `action.params?.query` and `action.label` are empty/undefined, `fallbackToQuery` does nothing except log a warning

---

### Suggested Debug Steps

1. **Log the entire action object**:
```typescript
const executeAction = useCallback((action: ActionSuggestion) => {
  console.log('[DEBUG] executeAction called with:', JSON.stringify(action, null, 2));
  console.log('[DEBUG] action_type:', action.action_type);
  console.log('[DEBUG] label:', action.label);
  console.log('[DEBUG] params:', action.params);
  // ...
}, [router, sendMessage]);
```

2. **Log fallback execution**:
```typescript
const fallbackToQuery = () => {
  console.log('[DEBUG] fallbackToQuery called');
  console.log('[DEBUG] queryText:', queryText);
  if (queryText) {
    console.log('[DEBUG] Calling sendMessage with:', queryText);
    sendMessage(queryText);
  } else {
    console.warn('[DEBUG] No queryText - nothing will happen!');
  }
};
```

3. **Log button click in GuideActionSuggestions.tsx**:
```tsx
onClick={() => {
  console.log('[DEBUG] Action button clicked');
  console.log('[DEBUG] Action object:', action);
  onExecute(action);
}}
```

4. **Check backend API response**: In Network tab, find the chat API response and inspect the `suggestions` array:
```json
{
  "suggestions": [
    {
      "action_type": "query",
      "label": "Show all tasks",
      "params": {
        "query": "list all tasks"
      }
    }
  ]
}
```
Verify:
- `action_type` is a valid type
- `label` is not empty
- `params.query` exists for query-type actions

5. **Verify sendMessage works**: Try calling it directly from browser console:
```javascript
// If GuideProvider exposes sendMessage via window for debugging
window.__guideDebug?.sendMessage('test message');
```

---

## Complete File Reference

| File Path | Lines | Description |
|-----------|-------|-------------|
| `frontend/hooks/useSmartAutoScroll.ts` | 1-62 | Scroll detection hook (REWRITTEN with callback ref) |
| `frontend/components/guide/GuideWidgetPanel.tsx` | 56-64, 172-216 | Hook usage, DOM structure, button placement |
| `frontend/components/guide/ScrollToBottomButton.tsx` | 1-60 | The button component |
| `frontend/components/providers/GuideProvider.tsx` | 348-393 | `executeAction` function |
| `frontend/components/guide/GuideActionSuggestions.tsx` | 40-86 | Action chips rendering |
| `frontend/components/guide/GuideChatMessage.tsx` | 186-195 | Where suggestions are rendered |
| `frontend/lib/api.ts` | TBD | `ActionSuggestion` type definition |

---

## Environment

- **Framework**: Next.js 16.0.3 (Turbopack)
- **React**: 19.x
- **Dev URL**: http://localhost:8080 (nginx reverse proxy)
- **Direct Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000

---

## Summary

| Bug | Root Cause Confidence | Code Fix Applied | Bug Resolved |
|-----|----------------------|------------------|--------------|
| Scroll Button | LOW | YES (callback ref pattern) | NO |
| Action Chips | MEDIUM | YES (filter fallback) | PARTIALLY |

---

## Recommended Approach

**Do not attempt more code fixes until console logging reveals the actual issue.**

1. Add all the console.log statements listed above
2. Reproduce both bugs
3. Check browser console output
4. The logs will show exactly where the flow breaks down
5. Then fix the actual root cause

---

## Previous Conversation Context

- Multiple fix attempts over several sessions
- Callback ref pattern was implemented for Bug 1 but didn't resolve it
- Filter fallback was implemented for Bug 2 but some chips may still fail
- Both "fixes" are currently in the codebase
- Hot module reload and browser cache were suspected but clearing didn't help
