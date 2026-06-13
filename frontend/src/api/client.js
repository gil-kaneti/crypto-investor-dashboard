import { clearToken, getToken } from "../auth/token";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function buildUrl(path) {
  return `${API_BASE_URL.replace(/\/$/, "")}${path}`;
}

function errorMessageFromBody(body, fallback) {
  if (!body) return fallback;
  if (typeof body.detail === "string") return body.detail;
  if (Array.isArray(body.detail)) {
    return body.detail.map((item) => item.msg || item.message).filter(Boolean).join(" ");
  }
  return fallback;
}

export async function apiRequest(path, options = {}) {
  const token = getToken();
  const headers = new Headers(options.headers || {});

  if (!headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(buildUrl(path), {
    ...options,
    headers,
  });

  const text = await response.text();
  let body = null;
  if (text) {
    try {
      body = JSON.parse(text);
    } catch (error) {
      body = null;
    }
  }

  if (response.status === 401) {
    clearToken();
    window.dispatchEvent(new Event("auth-token-cleared"));
  }

  if (!response.ok) {
    throw new Error(errorMessageFromBody(body, "Something went wrong. Please try again."));
  }

  return body;
}

export const api = {
  register: (payload) =>
    apiRequest("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  login: (payload) =>
    apiRequest("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  me: () => apiRequest("/auth/me"),
  getPreferences: () => apiRequest("/preferences"),
  savePreferences: (payload) =>
    apiRequest("/preferences", {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  getDashboard: () => apiRequest("/dashboard"),
  sendFeedback: (payload) =>
    apiRequest("/feedback", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};
