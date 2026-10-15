
/**
 * API Client & Authenticated Fetch Utility
 *
 * Features:
 * - Configurable API base URL for local and deployed environments
 * - Automatic access-token refresh using HttpOnly cookies
 * - Shared refresh request to prevent concurrent refresh races
 * - Automatic retry after a 401 Unauthorized response
 * - Session-expired event when refresh fails
 */

const TOKEN_KEY = 'sf_access_token';

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || ''
).replace(/\/$/, '');

let inFlightRefreshPromise = null;

/**
 * Resolves relative API paths to the configured backend URL.
 * Absolute URLs are returned unchanged.
 */
function resolveApiUrl(url) {
  if (/^https?:\/\//i.test(url)) {
    return url;
  }

  return `${API_BASE_URL}${url.startsWith('/') ? url : `/${url}`}`;
}

/**
 * Refreshes the access token using the HttpOnly refresh-token cookie.
 * Concurrent callers share the same refresh request.
 *
 * @returns {Promise<string>} Fresh access token.
 */
export async function refreshAccessToken() {
  if (inFlightRefreshPromise) {
    return inFlightRefreshPromise;
  }

  inFlightRefreshPromise = (async () => {
    try {
      const response = await fetch(
        resolveApiUrl('/api/auth/refresh'),
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
        }
      );

      if (!response.ok) {
        throw new Error('Refresh token invalid or expired');
      }

      const data = await response.json();

      if (data?.success && data?.access_token) {
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
 * Sends an authenticated API request.
 * If the access token has expired, attempts one refresh and one retry.
 *
 * @param {string} url API endpoint path or absolute URL.
 * @param {object} options Fetch options.
 * @param {boolean} isRetry Prevents repeated refresh attempts.
 * @returns {Promise<Response>} Fetch response.
 */
export async function authenticatedFetch(
  url,
  options = {},
  isRetry = false
) {
  const token = localStorage.getItem(TOKEN_KEY) || '';
  const headers = new Headers(options.headers || {});

  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const requestOptions = {
    ...options,
    headers,
    credentials: 'include',
  };

  const response = await fetch(
    resolveApiUrl(url),
    requestOptions
  );

  const isRefreshRequest = url.includes('/api/auth/refresh');

  if (response.status === 401 && !isRetry && !isRefreshRequest) {
    try {
      const newToken = await refreshAccessToken();

      if (newToken) {
        const retryHeaders = new Headers(options.headers || {});
        retryHeaders.set('Authorization', `Bearer ${newToken}`);

        return await fetch(resolveApiUrl(url), {
          ...options,
          headers: retryHeaders,
          credentials: 'include',
        });
      }
    } catch {
      localStorage.removeItem(TOKEN_KEY);

      window.dispatchEvent(
        new Event('sf_session_expired')
      );
    }
  }

  return response;
}
