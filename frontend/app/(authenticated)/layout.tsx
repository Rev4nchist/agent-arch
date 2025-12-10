'use client';

import { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import { AccessGuard } from '@/components/auth';
import { GuideProvider } from '@/components/providers/GuideProvider';
import { GuideWidget } from '@/components/guide';
import { MobileHeader } from '@/components/MobileHeader';
import { MobileNavDrawer } from '@/components/MobileNavDrawer';
import { SidebarContent } from '@/components/SidebarContent';
import { BottomNavBar } from '@/components/BottomNavBar';

export default function AuthenticatedLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    setMobileNavOpen(false);
  }, [pathname]);

  return (
    <AccessGuard>
      <GuideProvider>
        <MobileHeader onMenuClick={() => setMobileNavOpen(true)} />
        <MobileNavDrawer isOpen={mobileNavOpen} onClose={() => setMobileNavOpen(false)}>
          <SidebarContent onNavigate={() => setMobileNavOpen(false)} hideHeader />
        </MobileNavDrawer>
        <Sidebar />
        <main className="pt-14 pb-16 lg:pt-0 lg:pb-0 lg:pl-64">
          {children}
        </main>
        <BottomNavBar onMenuClick={() => setMobileNavOpen(true)} />
        <GuideWidget />
      </GuideProvider>
    </AccessGuard>
  );
}
