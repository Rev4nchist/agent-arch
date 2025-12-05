'use client';

import { usePathname } from 'next/navigation';

const FULL_WIDTH_ROUTES = ['/landing'];

interface MainContentProps {
  children: React.ReactNode;
}

export function MainContent({ children }: MainContentProps) {
  const pathname = usePathname();
  const isFullWidth = FULL_WIDTH_ROUTES.includes(pathname);

  return (
    <main className={isFullWidth ? '' : 'pl-64'}>
      {children}
    </main>
  );
}
