const LOGIN_EVENT = 'app:redirect-login';

/**
 * Dispatches a custom event to redirect to login.
 * Avoids window.location.href which can cause the PWA
 * to open the browser on some Android devices.
 */
export function redirectToLogin(): void {
  window.dispatchEvent(new CustomEvent(LOGIN_EVENT));
}

/**
 * Listen for redirect-to-login events.
 * Returns a cleanup function to use in useEffect.
 */
export function onRedirectToLogin(handler: () => void): () => void {
  const listener = () => handler();
  window.addEventListener(LOGIN_EVENT, listener);
  return () => window.removeEventListener(LOGIN_EVENT, listener);
}
