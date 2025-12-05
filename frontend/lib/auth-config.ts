import { Configuration, LogLevel } from '@azure/msal-browser';

// MSAL configuration for Microsoft Entra ID authentication
export const msalConfig: Configuration = {
  auth: {
    clientId: process.env.NEXT_PUBLIC_AZURE_CLIENT_ID || '92711679-0269-4cd4-9a7b-3e78259b9778',
    authority: `https://login.microsoftonline.com/${process.env.NEXT_PUBLIC_AZURE_TENANT_ID || '75cd3b18-d23a-40ee-ad06-ad4484fc72fe'}`,
    redirectUri: typeof window !== 'undefined' ? window.location.origin : 'https://agent-arch.fourth.com',
    postLogoutRedirectUri: typeof window !== 'undefined' ? window.location.origin : 'https://agent-arch.fourth.com',
    navigateToLoginRequestUrl: true,
  },
  cache: {
    cacheLocation: 'sessionStorage',
    storeAuthStateInCookie: false,
  },
  system: {
    loggerOptions: {
      loggerCallback: (level, message, containsPii) => {
        if (containsPii) return;
        switch (level) {
          case LogLevel.Error:
            console.error(message);
            break;
          case LogLevel.Warning:
            console.warn(message);
            break;
          case LogLevel.Info:
            // console.info(message); // Uncomment for debugging
            break;
          case LogLevel.Verbose:
            // console.debug(message); // Uncomment for debugging
            break;
        }
      },
      logLevel: LogLevel.Warning,
    },
  },
};

// Scopes for login - what permissions we're requesting
export const loginRequest = {
  scopes: ['User.Read', 'openid', 'profile', 'email'],
};

// Scopes for API calls (if needed for Microsoft Graph)
export const graphConfig = {
  graphMeEndpoint: 'https://graph.microsoft.com/v1.0/me',
};
