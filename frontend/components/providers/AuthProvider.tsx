'use client';

import React, { createContext, useContext, useEffect, useState, ReactNode, useCallback } from 'react';
import { PublicClientApplication, AccountInfo, InteractionStatus } from '@azure/msal-browser';
import { MsalProvider, useMsal, useIsAuthenticated } from '@azure/msal-react';
import { msalConfig, loginRequest } from '@/lib/auth-config';
import { accessApi, UserRole, AccessVerifyResponse } from '@/lib/access-api';

const msalInstance = new PublicClientApplication(msalConfig);

msalInstance.initialize().catch(console.error);

interface AuthContextType {
  user: AccountInfo | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isAuthorized: boolean;
  isCheckingAuthorization: boolean;
  userRole: UserRole | null;
  userName: string | null;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  getAccessToken: () => Promise<string | null>;
  checkAuthorization: () => Promise<AccessVerifyResponse | null>;
}

const AuthContext = createContext<AuthContextType | null>(null);

function AuthContextProvider({ children }: { children: ReactNode }) {
  const { instance, accounts, inProgress } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthorized, setIsAuthorized] = useState(false);
  const [isCheckingAuthorization, setIsCheckingAuthorization] = useState(false);
  const [userRole, setUserRole] = useState<UserRole | null>(null);
  const [userName, setUserName] = useState<string | null>(null);

  const user = accounts.length > 0 ? accounts[0] : null;

  const checkAuthorization = useCallback(async (): Promise<AccessVerifyResponse | null> => {
    if (!user?.username) {
      setIsAuthorized(false);
      setUserRole(null);
      setUserName(null);
      return null;
    }

    setIsCheckingAuthorization(true);
    try {
      const response = await accessApi.verify(user.username);
      setIsAuthorized(response.authorized);
      setUserRole(response.role || null);
      setUserName(response.name || user.name || null);
      return response;
    } catch (error) {
      console.error('Authorization check failed:', error);
      setIsAuthorized(false);
      setUserRole(null);
      setUserName(null);
      return null;
    } finally {
      setIsCheckingAuthorization(false);
    }
  }, [user?.username, user?.name]);

  useEffect(() => {
    if (inProgress === InteractionStatus.None) {
      setIsLoading(false);
      if (isAuthenticated && user) {
        checkAuthorization();
      }
    }
  }, [inProgress, isAuthenticated, user, checkAuthorization]);

  const login = async () => {
    try {
      setIsLoading(true);
      await instance.loginPopup(loginRequest);
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      setIsLoading(true);
      setIsAuthorized(false);
      setUserRole(null);
      setUserName(null);
      await instance.logoutPopup({
        postLogoutRedirectUri: window.location.origin,
        mainWindowRedirectUri: window.location.origin,
      });
    } catch (error) {
      console.error('Logout failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const getAccessToken = async (): Promise<string | null> => {
    if (!user) return null;

    try {
      const response = await instance.acquireTokenSilent({
        ...loginRequest,
        account: user,
      });
      return response.accessToken;
    } catch (error) {
      console.error('Failed to acquire token silently:', error);
      try {
        const response = await instance.acquireTokenPopup(loginRequest);
        return response.accessToken;
      } catch (interactiveError) {
        console.error('Interactive token acquisition failed:', interactiveError);
        return null;
      }
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated,
    isLoading: isLoading || inProgress !== InteractionStatus.None,
    isAuthorized,
    isCheckingAuthorization,
    userRole,
    userName,
    login,
    logout,
    getAccessToken,
    checkAuthorization,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  return (
    <MsalProvider instance={msalInstance}>
      <AuthContextProvider>{children}</AuthContextProvider>
    </MsalProvider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
