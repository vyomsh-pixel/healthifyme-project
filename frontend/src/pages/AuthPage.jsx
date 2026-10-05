import { useState, useEffect } from "react";
import { authenticate, authenticateGoogle } from "../lib/api";
import { signInWithGooglePopup } from "../lib/firebase";

export default function AuthPage({ onAuthenticated }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ display_name: "", username: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [isShattering, setIsShattering] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  async function handleGoogleSignIn() {
    setBusy(true);
    setError("");
    try {
      const googleData = await signInWithGooglePopup();
      const session = await authenticateGoogle(googleData);
      setIsShattering(true);
      setTimeout(() => setIsLoading(true), 400);
      setTimeout(() => {
        onAuthenticated(session);
      }, 1600);
    } catch (err) {
      setError(err.message || "Google Authentication failed.");
      setBusy(false);
    }
  }

  async function submit(event) {
    event.preventDefault();
    setBusy(true); setError("");
    try {
      const session = await authenticate(mode, mode === "login" ? { username: form.username, password: form.password } : form);
      // Start the shatter animation
      setIsShattering(true);
      
      // Delay starting the loading bar
      setTimeout(() => setIsLoading(true), 400);
      
      // Complete transition
      setTimeout(() => {
        onAuthenticated(session);
      }, 1600);
    } catch (err) { setError(err.message); setBusy(false); }
  }

  return <main className={`auth-shell ${isShattering ? "shattering" : ""}`}>
    {/* Full Screen Crack SVG Overlay */}
    <svg className="full-screen-crack" viewBox="0 0 100 100" preserveAspectRatio="none">
      <g stroke="var(--status-green)" strokeLinecap="round" strokeLinejoin="miter" style={{ filter: "drop-shadow(0 0 3px rgba(255,255,255,1))" }}>
        <path d="M 85 -5 L 82 10 L 88 18 L 80 25 L 75 30 L 60 33 L 35 38 L 25 45 L 20 60 L 15 75 L 25 90 L 18 105" strokeWidth="0.6" fill="none" vectorEffect="non-scaling-stroke" />
        <path d="M 60 33 L 65 38 L 68 35" strokeWidth="0.3" fill="none" vectorEffect="non-scaling-stroke" opacity="0.7" />
        <path d="M 20 60 L 10 55 L 8 50" strokeWidth="0.2" fill="none" vectorEffect="non-scaling-stroke" opacity="0.6" />
        <path d="M 15 75 L 25 80" strokeWidth="0.4" fill="none" vectorEffect="non-scaling-stroke" opacity="0.8" />
      </g>
    </svg>

    <section className="auth-panel">
      <div style={{ position: "relative", zIndex: 10 }}>
        <p className="eyebrow">BREAK THE BARRIER</p>
        <h1 className="brand-title">Health<span>.io</span></h1>
        <p className="auth-copy" style={{ color: "var(--text-primary)", fontWeight: "600", marginBottom: "1.75rem", fontSize: "1.25rem", lineHeight: 1.4, letterSpacing: "-0.01em" }}>
          Life happens behind a screen.<br/>Health.io is the crack in the glass.
        </p>

        <button
          type="button"
          onClick={handleGoogleSignIn}
          disabled={busy || isShattering}
          className="google-auth-button"
          aria-label="Continue with Google authentication"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
          </svg>
          <span>Continue with Google</span>
        </button>

        <div className="auth-divider">
          <span>or with password</span>
        </div>
        
        <div className="auth-tabs" role="tablist">
          <button className={mode === "login" ? "active" : ""} onClick={() => setMode("login")} type="button">Sign in</button>
          <button className={mode === "register" ? "active" : ""} onClick={() => setMode("register")} type="button">Create account</button>
        </div>
        <form onSubmit={submit} className="form-stack">
          {mode === "register" && (
            <label htmlFor="auth-display-name">
              Display name
              <input
                id="auth-display-name"
                required
                minLength="2"
                value={form.display_name}
                onChange={(e) => setForm({ ...form, display_name: e.target.value })}
                placeholder="Your name"
              />
            </label>
          )}
          <label htmlFor="auth-username">
            Username
            <input
              id="auth-username"
              required
              minLength="3"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              placeholder="e.g. aarya_01"
            />
          </label>
          <label htmlFor="auth-password">
            Password
            <input
              id="auth-password"
              required
              type="password"
              minLength="8"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              placeholder="At least 8 characters"
            />
          </label>
          {error && <p className="form-error" role="alert">{error}</p>}
          <button className="button primary" disabled={busy || isShattering}>{busy ? "Please wait…" : mode === "login" ? "Sign in" : "Create secure account"}</button>
        </form>
        <p className="fine-print">Health.io is a personal wellness visualization tool for self-tracking. It is not intended to diagnose, treat, or replace professional medical advice.</p>
      </div>
    </section>

    <div className={`global-loading-screen ${isLoading ? 'visible' : ''}`}>
      <h2 className="loading-text">Loading your dashboard...</h2>
      <div className="loading-track premium">
        <div className="loading-bar premium" style={{ width: isLoading ? '100%' : '0%' }}></div>
      </div>
    </div>
  </main>;
}
