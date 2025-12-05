'use client';

import { useAuth } from '@/components/providers/AuthProvider';
import { LoginPage } from './LoginPage';
import { RequestAccessForm } from './RequestAccessForm';
import { Loader2, ShieldX, LogOut } from 'lucide-react';
import { useEffect, useState } from 'react';
import { usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';

const PUBLIC_ROUTES = ['/landing'];

interface AccessGuardProps {
  children: React.ReactNode;
}

export function AccessGuard({ children }: AccessGuardProps) {
  const { isAuthenticated, isLoading, isAuthorized, isCheckingAuthorization, logout, user } = useAuth();
  const [isClient, setIsClient] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    setIsClient(true);
  }, []);

  // Allow public routes to bypass auth (check BEFORE isClient to work during SSG)
  if (PUBLIC_ROUTES.includes(pathname)) {
    return <>{children}</>;
  }

  // During SSR/SSG, render children to allow proper page content in static HTML
  // Client-side auth will kick in after hydration
  if (!isClient) {
    return <>{children}</>;
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
          <p className="text-sm text-gray-600">Checking authentication...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  if (isCheckingAuthorization) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
          <p className="text-sm text-gray-600">Verifying access permissions...</p>
        </div>
      </div>
    );
  }

  if (!isAuthorized) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-blue-50 p-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
          <div className="text-center mb-6">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-amber-100 rounded-full mb-4">
              <ShieldX className="h-8 w-8 text-amber-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900">Access Required</h2>
            <p className="text-gray-600 mt-2">
              You&apos;re signed in as <span className="font-medium">{user?.username}</span>, but you don&apos;t have access to this platform yet.
            </p>
          </div>

          <div className="border-t border-gray-200 pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Request Access</h3>
            <RequestAccessForm />
          </div>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <Button
              variant="outline"
              onClick={() => logout()}
              className="w-full"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Sign Out
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
