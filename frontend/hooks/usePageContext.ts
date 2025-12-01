'use client';

import { usePathname } from 'next/navigation';
import { useMemo } from 'react';
import { getPageContext, PageContext } from '@/lib/guide-context';

export function usePageContext(): PageContext {
  const pathname = usePathname();

  const context = useMemo(() => {
    return getPageContext(pathname);
  }, [pathname]);

  return context;
}
