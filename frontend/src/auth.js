// Session token storage and the tiny bit of client-side logic around it. The
// token itself is `{expiry}.{signature}`, the expiry half is plaintext (not
// encrypted, just signed), so it can be read here to know whether a stored
// session is still good without asking the backend first.

const STORAGE_KEY = "ukask_session_token";

export function getToken() {
  return sessionStorage.getItem(STORAGE_KEY);
}

export function setToken(token) {
  sessionStorage.setItem(STORAGE_KEY, token);
}

export function clearToken() {
  sessionStorage.removeItem(STORAGE_KEY);
}

export function isTokenValid(token) {
  if (!token) return false;
  const [expiry] = token.split(".");
  const expirySeconds = Number(expiry);
  if (!Number.isFinite(expirySeconds)) return false;
  return expirySeconds * 1000 > Date.now();
}

export function hasValidSession() {
  return isTokenValid(getToken());
}