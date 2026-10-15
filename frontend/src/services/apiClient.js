/**
 * API Client & Authenticated Fetch Utility
 * 
 * Provides concurrency-locked automatic access token refresh via HttpOnly cookies,
 * 401 Unauthorized handling, infinite retry loop protection, and unified request execution.
 */

const TOKEN_KEY = 'sf_access_token';
let inFlightRefreshPromise = null;

/**
 * Execute a single-in-flight refresh request to POST /api/auth/refresh using HttpOnly cookies.
 * Multiple concurrent callers will await the exact same shared promise to prevent rotation race conditions.
 *
 * @returns {Promise<string>} Fresh access token string.
 */
export async function refreshAccessToken() {
  if (inFlightRefreshPromise) {
    return inFlightRefreshPromise;
  }

  inFlightRefreshPromise = (async () => {
    try {
      const resp = await fetch('/api/auth/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
      });

      if (!resp.ok) {
        throw new Error('Refresh token invalid or expired');
      }

      const data = await resp.json();
      if (data && data.success && data.access_token) {
        localStorage.setItem(TOKEN_KEY, data.access_token);
        return data.access_token;
      }
      throw new Error('Refresh response missing access_token');
    } finally {
      inFlightRefreshPromise = null;
    }
  })();

  return inFlightRefreshPromise;
}

/**
 * Centralized authenticated fetch wrapper with automatic 401 token refresh and single-retry execution.
 *
 * @param {string} url Request URL endpoint.
 * @param {object} options Fetch options object.
 * @param {boolean} isRetry Flag indicating if request is already a retry.
 * @returns {Promise<Response>} Fetch Response object.
 */
export async function authenticatedFetch(url, options = {}, isRetry = false) {
  const token = localStorage.getItem(TOKEN_KEY) || '';
  const reqHeaders = new Headers(options.headers || {});

  if (token && !reqHeaders.has('Authorization')) {
    reqHeaders.set('Authorization', `Bearer ${token}`);
  }

  const reqOptions = {
    ...options,
    headers: reqHeaders,
    credentials: 'include',
  };

  const response = await fetch(url, reqOptions);

  // If 401 Unauthorized, not already a retry, and URL is NOT the refresh endpoint itself
  if (response.status === 401 && !isRetry && !url.includes('/api/auth/refresh')) {
    try {
      const newToken = await refreshAccessToken();
      if (newToken) {
        // Retry original request once with fresh access token
        const retryHeaders = new Headers(options.headers || {});
        retryHeaders.set('Authorization', `Bearer ${newToken}`);

        return await fetch(url, {
          ...options,
          headers: retryHeaders,
          credentials: 'include',
        });
      }
    } catch (err) {
      // Refresh failed -> clear expired token from localStorage
      localStorage.removeItem(TOKEN_KEY);
      window.dispatchEvent(new Event('sf_session_expired'));
    }
  }

  return response;
}
