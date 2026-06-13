const TOKEN_KEY = "crypto_dashboard_access_token";

export function getToken() {
  // Demo tradeoff: localStorage keeps auth simple for reviewers; production apps should prefer httpOnly secure cookies.
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}
