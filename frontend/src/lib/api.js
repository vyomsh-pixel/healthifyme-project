const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
const API_BASE = import.meta.env.VITE_API_BASE_URL || (isLocal ? "http://localhost:8001/api" : "https://healthifyme-project.onrender.com/api");
const SESSION_KEY = "healthio-session";

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
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || "Something went wrong. Please try again.");
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

export async function signOut() {
  try { await request("/auth/logout", { method: "POST" }); } finally { clearSession(); }
}
