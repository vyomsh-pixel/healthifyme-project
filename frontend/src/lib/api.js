const isLocal = typeof window !== "undefined" && (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1");
const API_BASE = import.meta.env.VITE_API_BASE_URL || (isLocal ? "http://localhost:8001/api" : "/api");
const SESSION_KEY = "healthio-session";

export function normalizeErrorMessage(data, fallback = "Something went wrong. Please try again.") {
  if (typeof data === "string") return data;
  if (!data || typeof data !== "object") return fallback;

  if (typeof data.message === "string" && data.message.trim()) return data.message;
  if (typeof data.error === "string" && data.error.trim()) return data.error;
  if (typeof data.msg === "string" && data.msg.trim()) return data.msg;

  const detail = data.detail;
  if (typeof detail === "string" && detail.trim()) return detail;
  if (Array.isArray(detail)) {
    const parts = detail
      .map((item) => {
        if (typeof item === "string") return item;
        if (item && typeof item === "object") {
          if (typeof item.msg === "string") return item.msg;
          if (typeof item.message === "string") return item.message;
          return JSON.stringify(item);
        }
        return "";
      })
      .filter(Boolean);
    if (parts.length) return parts.join(" • ");
  }
  if (detail && typeof detail === "object") {
    if (typeof detail.message === "string") return detail.message;
    if (typeof detail.error === "string") return detail.error;
    if (typeof detail.msg === "string") return detail.msg;
    return JSON.stringify(detail);
  }

  return fallback;
}

export function getSession() {
  try {
    return JSON.parse(localStorage.getItem(SESSION_KEY) || "null");
  } catch {
    return null;
  }
}

export function saveSession(session) {
  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

export function clearSession() {
  localStorage.removeItem(SESSION_KEY);
}

export async function request(path, { method = "GET", body, token = getSession()?.token, retries = 1 } = {}) {
  try {
    const response = await fetch(`${API_BASE}${path}`, {
      method,
      headers: {
        ...(body ? { "Content-Type": "application/json" } : {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      ...(body ? { body: JSON.stringify(body) } : {}),
    });
    if (response.status === 204) return null;

    const rawText = await response.text();
    let data = {};
    try {
      data = rawText ? JSON.parse(rawText) : {};
    } catch {
      data = {};
    }

    if (!response.ok) {
      throw new Error(normalizeErrorMessage(data));
    }
    return data;
  } catch (err) {
    // Catch generic network failures thrown by fetch()
    if (err.name === "TypeError" || err.message === "Failed to fetch") {
      if (retries > 0) {
        await new Promise(resolve => setTimeout(resolve, 1500));
        return request(path, { method, body, token, retries: retries - 1 });
      }
      throw new Error("Network issue — check your connection or wait a moment and try again.");
    }
    throw err;
  }
}

export async function authenticate(mode, values) {
  const session = await request(`/auth/${mode}`, { method: "POST", body: values, token: null });
  saveSession(session);
  return session;
}

export async function authenticateGoogle(authPayload) {
  const session = await request("/auth/google", { method: "POST", body: authPayload, token: null });
  saveSession(session);
  return session;
}


export function signOut() {
  const token = getSession()?.token;
  clearSession();
  if (!token) return;

  void request("/auth/logout", {
    method: "POST",
    token,
    retries: 0,
  }).catch(() => {
    // Ignore server-side logout failures so the client signs out immediately.
  });
}
