# Bug Investigation Brief for Codex

**Date**: December 8, 2025
**Priority**: High
**Project**: agent-arch (AI Guide Widget)

---

## TL;DR

Two bugs in the AI Guide chat widget need your investigation. Multiple fix attempts have failed. This document tells you exactly what to check and where.

---

## Bug 1: Scroll-to-Bottom Button Never Appears

### Symptom
When users scroll up in chat, a "Jump to bottom" pill button should appear. **It never appears.**

### Your First Steps

1. **Add debug logging** to `frontend/hooks/useSmartAutoScroll.ts`:

```typescript
// Line 17 - Check if callback ref fires
const containerRef: RefCallback<HTMLDivElement> = useCallback((node) => {
  console.log('[DEBUG] containerRef called:', node);
  setContainer(node);
}, []);

// Line 28 - Check if effect runs
useEffect(() => {
  console.log('[DEBUG] Effect running, container:', container);
  if (!container) return;

  const { scrollTop, scrollHeight, clientHeight } = container;
  console.log('[DEBUG] Dimensions:', { scrollTop, scrollHeight, clientHeight });
  // ... rest of effect
}, [container, checkIfAtBottom]);

// Line 21 - Check scroll calculations
const checkIfAtBottom = useCallback(() => {
  if (!container) return;
  const { scrollTop, scrollHeight, clientHeight } = container;
  const distanceFromBottom = scrollHeight - scrollTop - clientHeight;
  console.log('[DEBUG] Scroll check:', { distanceFromBottom, threshold });
  setIsAtBottom(distanceFromBottom <= threshold);
}, [container, threshold]);
```

2. **Quick visibility test** in `frontend/components/guide/GuideWidgetPanel.tsx` line 210:
```tsx
// Change this:
visible={!isAtBottom && messages.length > 0}
// To this:
visible={true}  // Force visible to confirm button renders
```

3. **Browser DevTools check**:
   - Find the scroll container: `document.querySelector('.overflow-y-auto')`
   - Check: `scrollHeight > clientHeight` (must be true for scrolling to work)
   - Try: `element.scrollTop = 0` and see if it scrolls

### Key Files
| File | What to Check |
|------|---------------|
| `frontend/hooks/useSmartAutoScroll.ts` | Lines 17-41 - callback ref and effect |
| `frontend/components/guide/GuideWidgetPanel.tsx` | Lines 175, 210 - ref attachment and visibility |
| `frontend/components/guide/ScrollToBottomButton.tsx` | Button component itself |

### What Was Already Tried (didn't work)
- Moved button outside scroll container with absolute positioning
- Changed from `useRef` to callback ref pattern with `useState`

---

## Bug 2: Action Chips Do Nothing When Clicked

### Symptom
"Suggested next actions" chips below AI responses do nothing when clicked (some work, some don't).

### Your First Steps

1. **Add debug logging** to `frontend/components/providers/GuideProvider.tsx`:

```typescript
// Line 349
const executeAction = useCallback((action: ActionSuggestion) => {
  console.log('[DEBUG] executeAction called:', JSON.stringify(action, null, 2));

  const queryText = action.params?.query?.toString() || action.label;
  console.log('[DEBUG] queryText:', queryText);

  const fallbackToQuery = () => {
    console.log('[DEBUG] fallbackToQuery called');
    if (queryText) {
      console.log('[DEBUG] Calling sendMessage with:', queryText);
      sendMessage(queryText);
    } else {
      console.warn('[DEBUG] No queryText available!');
    }
  };
  // ... rest of function
}, [router, sendMessage]);
```

2. **Check Network tab**: Look at API response for chat messages - inspect the `suggestions` array structure

3. **Verify prop chain** - add log in `frontend/components/guide/GuideActionSuggestions.tsx`:
```tsx
// Line 68
onClick={() => {
  console.log('[DEBUG] Button clicked, action:', action);
  onExecute(action);
}}
```

### Key Files
| File | What to Check |
|------|---------------|
| `frontend/components/providers/GuideProvider.tsx` | Lines 348-393 - `executeAction` function |
| `frontend/components/guide/GuideActionSuggestions.tsx` | Lines 64-68 - button onClick |
| `frontend/components/guide/GuideChatMessage.tsx` | Lines 187-194 - where suggestions render |

### What Was Already Tried (didn't work)
- Changed `filter` case to always call `fallbackToQuery()` instead of dispatching unheard event

---

## How to Test

1. **Start local env**: http://localhost:8080
2. **Open AI Guide** (sparkle icon bottom-right)
3. **Send a message** that generates a long response
4. **Bug 1 test**: Scroll up in chat → button should appear (doesn't)
5. **Bug 2 test**: Click any action chip → should navigate or send message (some don't)

---

## Environment
- Next.js 16.0.3 (Turbopack)
- React 19.x
- Local: nginx proxy on :8080 → frontend:3000 + backend:8000

---

## Questions?

The full technical analysis is in: `C:\Users\david.hayes\.claude\plans\prancy-bubbling-dongarra.md`

Let me know what you find in the console logs - that should reveal the root cause.
