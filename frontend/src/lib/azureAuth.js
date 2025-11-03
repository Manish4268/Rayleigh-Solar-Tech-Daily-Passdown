/**
 * Azure Static Web Apps Authentication Helper
 * 
 * This file handles authentication for both local development and Azure SWA deployment
 */

// Check if running on Azure SWA
export const isAzureSWA = () => {
  const isAzure = window.location.hostname.includes('azurestaticapps.net') || 
                  window.location.hostname.includes('azure.com');
  console.log('[Auth] Environment check:', {
    hostname: window.location.hostname,
    isAzure: isAzure
  });
  return isAzure;
};

// Get user info from Azure SWA
export const getAzureUser = async () => {
  try {
    console.log('[Auth] Fetching user from /.auth/me...');
    const response = await fetch('/.auth/me');
    
    if (!response.ok) {
      console.error('[Auth] /.auth/me failed:', response.status, response.statusText);
      return null;
    }
    
    const payload = await response.json();
    console.log('[Auth] /.auth/me response:', payload);
    
    const { clientPrincipal } = payload;
    
    if (clientPrincipal) {
      const email = clientPrincipal.userDetails;
      
      // Validate email domain for security
      if (!email.endsWith('@rayleighsolartech.com')) {
        console.error('[Auth] Invalid email domain:', email);
        alert('Access denied: Only @rayleighsolartech.com emails are allowed');
        return null;
      }
      
      const user = {
        email: email,
        name: clientPrincipal.userDetails.split('@')[0],
        userId: clientPrincipal.userId,
        provider: clientPrincipal.identityProvider
      };
      
      console.log('[Auth] User authenticated:', user);
      return user;
    }
    
    console.log('[Auth] No clientPrincipal found');
    return null;
  } catch (error) {
    console.error('[Auth] Failed to get Azure user:', error);
    return null;
  }
};

// Check authentication status
export const checkAuthentication = async () => {
  console.log('[Auth] Checking authentication...');
  
  // If on Azure SWA, check Azure authentication
  if (isAzureSWA()) {
    console.log('[Auth] Azure environment detected, checking /.auth/me');
    const user = await getAzureUser();
    if (user) {
      // Store user info in localStorage for consistency
      localStorage.setItem('isAuthenticated', 'true');
      localStorage.setItem('userEmail', user.email);
      localStorage.setItem('userName', user.name);
      console.log('[Auth] User authenticated on Azure');
      return true;
    }
    console.log('[Auth] No authenticated user on Azure');
    return false;
  }
  
  // For local development, check localStorage
  const isAuth = localStorage.getItem('isAuthenticated') === 'true';
  console.log('[Auth] Local environment, isAuthenticated:', isAuth);
  return isAuth;
};

// Login function
export const login = () => {
  if (isAzureSWA()) {
    console.log('[Auth] Redirecting to Azure AD login...');
    // Redirect to Azure AD login
    window.location.href = '/.auth/login/aad?post_login_redirect_uri=' + window.location.origin;
  } else {
    // For local, this is handled by Login component
    console.log('[Auth] Local login - handled by Login component');
  }
};

// Logout function
export const logout = () => {
  console.log('[Auth] Logging out...');
  
  // Clear localStorage
  localStorage.removeItem('isAuthenticated');
  localStorage.removeItem('userEmail');
  localStorage.removeItem('userName');
  localStorage.removeItem('registeredUsers');
  
  if (isAzureSWA()) {
    console.log('[Auth] Redirecting to Azure logout...');
    // Redirect to Azure logout
    window.location.href = '/.auth/logout?post_logout_redirect_uri=' + window.location.origin;
  } else {
    console.log('[Auth] Local logout - reloading page...');
    // For local, just reload
    window.location.reload();
  }
};

// Get current user info
export const getCurrentUser = () => {
  return {
    email: localStorage.getItem('userEmail'),
    name: localStorage.getItem('userName'),
    isAuthenticated: localStorage.getItem('isAuthenticated') === 'true'
  };
};
