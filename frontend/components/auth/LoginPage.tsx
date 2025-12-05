'use client';

import { useAuth } from '@/components/providers/AuthProvider';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import Image from 'next/image';
import { LogIn, Loader2, Shield } from 'lucide-react';

export function LoginPage() {
  const { login, isLoading } = useAuth();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
      <Card className="w-full max-w-md mx-4 shadow-lg">
        <CardHeader className="text-center space-y-4">
          <div className="flex justify-center">
            <Image
              src="/Fourth_icon.png"
              alt="Fourth Logo"
              width={64}
              height={64}
              className="rounded-lg"
            />
          </div>
          <div>
            <CardTitle className="text-2xl font-bold text-gray-900">
              Fourth AI Architecture
            </CardTitle>
            <CardDescription className="text-gray-600 mt-2">
              Agent Framework Governance Portal
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <Shield className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
              <div className="text-sm text-blue-800">
                <p className="font-medium">Secure Access Required</p>
                <p className="mt-1 text-blue-700">
                  Sign in with your Fourth Microsoft account to access the platform.
                </p>
              </div>
            </div>
          </div>

          <Button
            onClick={login}
            disabled={isLoading}
            className="w-full h-12 text-base font-medium"
            size="lg"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                Signing in...
              </>
            ) : (
              <>
                <LogIn className="mr-2 h-5 w-5" />
                Sign in with Microsoft
              </>
            )}
          </Button>

          <p className="text-xs text-center text-gray-500">
            By signing in, you agree to Fourth's security policies and terms of use.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
