# AI Guide Widget - Comprehensive Bug Report

**Document Created**: December 8, 2025
**Author**: Claude (AI Assistant)
**Status**: UNRESOLVED - Escalated to Senior Engineer
**Project**: agent-arch (Agent Architecture Portal)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Bug 1: Scroll-to-Bottom Button](#bug-1-scroll-to-bottom-button-never-appears)
3. [Bug 2: Action Chips Not Working](#bug-2-action-chips-do-nothing-when-clicked)
4. [File Reference](#file-reference)
5. [Environment Details](#environment-details)
6. [Debug Instructions](#debug-instructions)
7. [Appendix: Full Code Listings](#appendix-full-code-listings)

---

## Executive Summary

Two persistent bugs in the AI Guide chat widget have resisted multiple fix attempts across several debugging sessions. This document provides complete technical context for a senior engineer to investigate and resolve.

| Bug | Description | Fix Attempts | Status |
|-----|-------------|--------------|--------|
| #1 | Scroll-to-bottom button never appears | 2 | UNRESOLVED |
| #2 | Some action chips do nothing when clicked | 1 | PARTIALLY RESOLVED |

**Root Cause Confidence**: LOW - Multiple hypotheses remain; console logging needed to identify actual failure point.

---

## Bug 1: Scroll-to-Bottom Button Never Appears

### Description

When a user scrolls up in the AI Guide chat message area, a floating "Jump to bottom" pill button should appear. This button **never appears** regardless of scroll position, message count, or widget state.

### Expected Behavior

1. User opens AI Guide widget
2. User sends message, receives long response
3. User scrolls UP in the message area
4. **"Jump to bottom" button appears** at bottom of message area
5. User clicks button → scrolls to bottom → button disappears

### Actual Behavior

- Button **never appears** under any circumstances
- The `isAtBottom` state value appears to be permanently `true`
- No errors in console

### Technical Analysis

#### Component Architecture

```
GuideWidgetPanel
├── useSmartAutoScroll() hook
│   ├── containerRef (callback ref → sets container state)
│   ├── messagesEndRef (regular ref)
│   ├── isAtBottom (state, controls button visibility)
│   └── scrollToBottom (function)
│
├── Scroll Container (div with ref={containerRef})
│   ├── Messages list
│   └── <div ref={messagesEndRef} /> (scroll anchor)
│
└── ScrollToBottomButton (positioned outside scroll container)
    └── visible={!isAtBottom && messages.length > 0}
```

#### The Hook: `useSmartAutoScroll.ts`

**Current Implementation (after fix attempt):**

```typescript
export function useSmartAutoScroll(options: UseSmartAutoScrollOptions = {}) {
  const { isStreaming = false, threshold = 100 } = options;

  // State-based container tracking (callback ref pattern)
  const [container, setContainer] = useState<HTMLDivElement | null>(null);
  const [isAtBottom, setIsAtBottom] = useState(true);  // ← Initial value
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Callback ref - should update state when DOM element mounts/unmounts
  const containerRef: RefCallback<HTMLDivElement> = useCallback((node) => {
    setContainer(node);
  }, []);

  // Scroll position checker
  const checkIfAtBottom = useCallback(() => {
    if (!container) return;
    const { scrollTop, scrollHeight, clientHeight } = container;
    const distanceFromBottom = scrollHeight - scrollTop - clientHeight;
    setIsAtBottom(distanceFromBottom <= threshold);  // threshold = 100px
  }, [container, threshold]);

  // Effect to attach scroll listener
  useEffect(() => {
    if (!container) return;

    const handleScroll = () => {
      checkIfAtBottom();
    };

    container.addEventListener('scroll', handleScroll, { passive: true });
    checkIfAtBottom();  // Initial check on mount

    return () => {
      container.removeEventListener('scroll', handleScroll);
    };
  }, [container, checkIfAtBottom]);

  // ... rest of hook
}
```

#### Button Visibility Logic

In `GuideWidgetPanel.tsx`:

```tsx
<ScrollToBottomButton
  visible={!isAtBottom && messages.length > 0}
  onClick={() => scrollToBottom()}
  isStreaming={isLoading}
/>
```

For button to be visible:
- `isAtBottom` must be `false`
- `messages.length` must be `> 0`

### Previous Fix Attempts

#### Attempt 1: DOM Restructuring

**Hypothesis**: Button was inside the scroll container, getting scrolled out of view.

**Change**: Moved `ScrollToBottomButton` outside the scrollable div, positioned it absolutely within a relative parent wrapper.

**Result**: ❌ Bug persists. DOM structure is now correct but button still doesn't appear.

#### Attempt 2: Callback Ref Pattern

**Hypothesis**: Using `useRef` doesn't trigger re-renders, so the effect that attaches the scroll listener might not run when the container mounts.

**Change**: Replaced `useRef` with `useState` + callback ref pattern:
- `containerRef` is now a callback function that calls `setContainer(node)`
- Effect depends on `container` state, so it re-runs when container changes

**Result**: ❌ Bug persists. Either:
- Callback ref isn't being called
- Effect isn't running
- Scroll listener isn't firing
- `checkIfAtBottom` calculation is wrong

### Remaining Hypotheses

1. **Callback ref timing**: In React 19 / Next.js 16, the callback ref may not fire when expected

2. **Container not scrollable**: If `scrollHeight === clientHeight`, then `distanceFromBottom = 0`, which is always `<= threshold`, so `isAtBottom` stays `true`

3. **CSS issue**: Parent containers may be preventing overflow, or height isn't constrained

4. **Effect dependencies**: `checkIfAtBottom` in the dependency array might cause issues

5. **HMR caching**: Dev server might be serving old code despite changes

---

## Bug 2: Action Chips Do Nothing When Clicked

### Description

The "Suggested next actions" chips (small buttons) that appear below AI responses sometimes do nothing when clicked. No navigation occurs, no message is sent, and no error appears.

### Expected Behavior

1. AI response includes action suggestions
2. Chips render below the response
3. User clicks a chip
4. **Either**: Navigate to a page **OR** Send the chip's label as a new chat message

### Actual Behavior

- Some chips work correctly
- Some chips do nothing (silent failure)
- No console errors or warnings

### Technical Analysis

#### Component Architecture

```
GuideProvider (React Context)
├── executeAction(action) function
│
GuideChatMessage
├── message.suggestions array
└── GuideActionSuggestions
    └── Button onClick={() => onExecute(action)}
        └── Calls executeAction from context
```

#### The Handler: `executeAction` in `GuideProvider.tsx`

```typescript
const executeAction = useCallback((action: ActionSuggestion) => {
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
      fallbackToQuery();  // ← FIXED: Was dispatching unheard event
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

#### ActionSuggestion Type

```typescript
interface ActionSuggestion {
  action_type: 'query' | 'filter' | 'navigate' | 'show_detail' | 'export' | 'create';
  label: string;
  params?: {
    query?: string;
    page?: string;
    entity?: string;
    id?: string;
    field?: string;
    value?: string;
  };
  source?: string;
}
```

### Previous Fix Attempts

#### Attempt 1: Remove Filter Event Dispatch

**Hypothesis**: The `filter` case was dispatching a `CustomEvent('guide-filter-action')` that nothing was listening to.

**Change**: Changed `filter` case to call `fallbackToQuery()` directly.

**Result**: ⚠️ Partially resolved. Filter actions should now work, but other action types may still fail.

### Remaining Hypotheses

1. **Empty queryText**: If both `action.params?.query` and `action.label` are empty/undefined, nothing happens

2. **Backend data issue**: API may return malformed action objects

3. **Prop chain broken**: `onExecuteAction` may not be passed correctly through components

4. **Unknown action types**: Backend returns types not in the switch statement

5. **sendMessage failing**: The context's `sendMessage` function may not work properly

---

## File Reference

| File | Path | Key Lines | Purpose |
|------|------|-----------|---------|
| useSmartAutoScroll | `frontend/hooks/useSmartAutoScroll.ts` | 1-62 | Scroll state management hook |
| GuideWidgetPanel | `frontend/components/guide/GuideWidgetPanel.tsx` | 56-64, 172-216 | Main widget, uses hook, renders button |
| ScrollToBottomButton | `frontend/components/guide/ScrollToBottomButton.tsx` | 1-60 | The floating button component |
| GuideProvider | `frontend/components/providers/GuideProvider.tsx` | 348-393 | Context with executeAction |
| GuideActionSuggestions | `frontend/components/guide/GuideActionSuggestions.tsx` | 40-86 | Renders action chip buttons |
| GuideChatMessage | `frontend/components/guide/GuideChatMessage.tsx` | 186-195 | Message component, renders suggestions |
| API Types | `frontend/lib/api.ts` | TBD | ActionSuggestion interface |

---

## Environment Details

| Component | Version/Details |
|-----------|-----------------|
| Framework | Next.js 16.0.3 (Turbopack) |
| React | 19.x |
| Node | See package.json |
| Dev URL | http://localhost:8080 (nginx proxy) |
| Frontend Direct | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Proxy | nginx:alpine in Docker |

---

## Debug Instructions

### For Bug 1: Scroll Button

**Step 1: Add logging to useSmartAutoScroll.ts**

```typescript
const containerRef: RefCallback<HTMLDivElement> = useCallback((node) => {
  console.log('[SCROLL-DEBUG] containerRef called:', node);
  console.log('[SCROLL-DEBUG] node dimensions:', node ? {
    scrollHeight: node.scrollHeight,
    clientHeight: node.clientHeight,
    offsetHeight: node.offsetHeight
  } : 'null');
  setContainer(node);
}, []);

useEffect(() => {
  console.log('[SCROLL-DEBUG] Effect running');
  console.log('[SCROLL-DEBUG] container:', container);
  if (!container) {
    console.log('[SCROLL-DEBUG] No container, returning early');
    return;
  }

  const { scrollTop, scrollHeight, clientHeight } = container;
  console.log('[SCROLL-DEBUG] Attaching listener. Dimensions:', {
    scrollTop, scrollHeight, clientHeight,
    isScrollable: scrollHeight > clientHeight
  });

  // ... rest of effect
}, [container, checkIfAtBottom]);

const checkIfAtBottom = useCallback(() => {
  if (!container) {
    console.log('[SCROLL-DEBUG] checkIfAtBottom: no container');
    return;
  }
  const { scrollTop, scrollHeight, clientHeight } = container;
  const distanceFromBottom = scrollHeight - scrollTop - clientHeight;
  console.log('[SCROLL-DEBUG] checkIfAtBottom:', {
    scrollTop, scrollHeight, clientHeight,
    distanceFromBottom,
    threshold,
    willBeAtBottom: distanceFromBottom <= threshold
  });
  setIsAtBottom(distanceFromBottom <= threshold);
}, [container, threshold]);
```

**Step 2: Add isAtBottom state change logger**

```typescript
useEffect(() => {
  console.log('[SCROLL-DEBUG] isAtBottom changed to:', isAtBottom);
}, [isAtBottom]);
```

**Step 3: Force button visible in GuideWidgetPanel.tsx**

```tsx
<ScrollToBottomButton
  visible={true}  // TEMPORARY: Force visible
  onClick={() => scrollToBottom()}
  isStreaming={isLoading}
/>
```

**Step 4: Check in browser DevTools**

```javascript
// Run in console
const container = document.querySelector('.overflow-y-auto');
console.log('Container found:', container);
console.log('scrollHeight:', container?.scrollHeight);
console.log('clientHeight:', container?.clientHeight);
console.log('Is scrollable:', container?.scrollHeight > container?.clientHeight);
```

### For Bug 2: Action Chips

**Step 1: Add logging to executeAction in GuideProvider.tsx**

```typescript
const executeAction = useCallback((action: ActionSuggestion) => {
  console.log('[ACTION-DEBUG] executeAction called');
  console.log('[ACTION-DEBUG] Full action:', JSON.stringify(action, null, 2));

  const queryText = action.params?.query?.toString() || action.label;
  console.log('[ACTION-DEBUG] Resolved queryText:', queryText);

  const fallbackToQuery = () => {
    console.log('[ACTION-DEBUG] fallbackToQuery called');
    if (queryText) {
      console.log('[ACTION-DEBUG] Calling sendMessage with:', queryText);
      sendMessage(queryText);
    } else {
      console.warn('[ACTION-DEBUG] No queryText available - silent failure!');
    }
  };

  console.log('[ACTION-DEBUG] action_type:', action.action_type);

  switch (action.action_type) {
    // ... cases with additional logging
  }
}, [router, sendMessage]);
```

**Step 2: Add logging to button click in GuideActionSuggestions.tsx**

```tsx
onClick={() => {
  console.log('[ACTION-DEBUG] Button clicked');
  console.log('[ACTION-DEBUG] Action:', action);
  onExecute(action);
}}
```

**Step 3: Check Network tab**

1. Open DevTools → Network tab
2. Send a message in AI Guide
3. Find the chat API response
4. Inspect the `suggestions` array in the response
5. Verify each suggestion has valid `action_type`, `label`, and `params`

---

## Appendix: Full Code Listings

### A1: useSmartAutoScroll.ts (Current)

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
  const [isAtBottom, setIsAtBottom] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const containerRef: RefCallback<HTMLDivElement> = useCallback((node) => {
    setContainer(node);
  }, []);

  const checkIfAtBottom = useCallback(() => {
    if (!container) return;
    const { scrollTop, scrollHeight, clientHeight } = container;
    const distanceFromBottom = scrollHeight - scrollTop - clientHeight;
    setIsAtBottom(distanceFromBottom <= threshold);
  }, [container, threshold]);

  useEffect(() => {
    if (!container) return;

    const handleScroll = () => {
      checkIfAtBottom();
    };

    container.addEventListener('scroll', handleScroll, { passive: true });
    checkIfAtBottom();

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

### A2: ScrollToBottomButton.tsx (Current)

```typescript
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
          : "opacity-0 translate-y-4 pointer-events-none"
      )}
      aria-label={buttonText}
      aria-live="polite"
      tabIndex={visible ? 0 : -1}
    >
      {isStreaming && (
        <span className="flex gap-0.5" aria-hidden="true">
          <span className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
          <span className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
          <span className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
        </span>
      )}
      <ChevronDown className="h-4 w-4" aria-hidden="true" />
      <span className="text-xs font-medium">{buttonText}</span>
    </button>
  );
}
```

---

**End of Report**
