'use client';

import { useMemo } from 'react';
import { usePageContext } from './usePageContext';
import { getSuggestionsForPage, Suggestion } from '@/lib/guide-context';

export function useGuideSuggestions(): Suggestion[] {
  const pageContext = usePageContext();

  const suggestions = useMemo(() => {
    return getSuggestionsForPage(pageContext.route);
  }, [pageContext.route]);

  return suggestions;
}
