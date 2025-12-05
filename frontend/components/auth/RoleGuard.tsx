'use client';

import { useAuth } from '@/components/providers/AuthProvider';
import { UserRole } from '@/lib/access-api';
import { ShieldAlert } from 'lucide-react';

interface RoleGuardProps {
  children: React.ReactNode;
  requiredRole: UserRole;
  fallback?: React.ReactNode;
}

export function RoleGuard({ children, requiredRole, fallback }: RoleGuardProps) {
  const { userRole, isAuthorized } = useAuth();

  if (!isAuthorized) {
    return null;
  }

  const hasAccess = requiredRole === 'user' || userRole === 'admin';

  if (!hasAccess) {
    if (fallback) {
      return <>{fallback}</>;
    }

    return (
      <div className="min-h-[50vh] flex items-center justify-center">
        <div className="text-center p-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-4">
            <ShieldAlert className="h-8 w-8 text-red-600" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Access Denied</h2>
          <p className="text-gray-600">
            You don&apos;t have permission to access this page.
          </p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}

export function useHasRole(requiredRole: UserRole): boolean {
  const { userRole, isAuthorized } = useAuth();

  if (!isAuthorized) return false;
  if (requiredRole === 'user') return true;
  return userRole === 'admin';
}
