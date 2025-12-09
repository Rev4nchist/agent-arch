# AI Guide Widget Updates (December 2025)

## Overview
- Addressed two persistent UI issues in the AI Guide widget:
  - Scroll-to-bottom pill never appearing.
  - Some action chips doing nothing when clicked.

## Changes Implemented
- Scroll detection (`frontend/hooks/useSmartAutoScroll.ts`)
  - Reduced bottom detection threshold to 20px so scrolling up quickly marks the view as not-at-bottom, allowing the pill to appear.
  - Added a `ResizeObserver` on the scroll container to re-run the distance check whenever content/size changes (covers new messages without relying solely on scroll events).
- Action chips (`frontend/components/providers/GuideProvider.tsx`)
  - Normalized entity paths for `navigate` and `show_detail` actions so both singular and plural entity names route correctly (prevents broken routes like `/taskss/:id`).

## Testing
- Automated tests not run here (Node dependencies not installed in this environment). Recommended locally:
  - `cd frontend`
  - `npm install`
  - `npm run lint`
  - Manual check: load the widget, send enough messages to overflow, scroll up and confirm the pill appears and works; click action chips with entity/id to confirm navigation fires.

## Impact & Notes
- Scroll pill should now appear as soon as the user scrolls up slightly and stay in sync with content changes.
- Action chips that previously failed due to malformed routes should now navigate or fall back to sending the query text.
