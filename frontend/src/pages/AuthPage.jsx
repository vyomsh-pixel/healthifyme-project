import { useState, useEffect } from "react";
import { authenticate } from "../lib/api";

export default function AuthPage({ onAuthenticated }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ display_name: "", username: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [isShattering, setIsShattering] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

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
        
        <div className="auth-tabs" role="tablist">
          <button className={mode === "login" ? "active" : ""} onClick={() => setMode("login")} type="button">Sign in</button>
          <button className={mode === "register" ? "active" : ""} onClick={() => setMode("register")} type="button">Create account</button>
        </div>
        <form onSubmit={submit} className="form-stack">
          {mode === "register" && <label>Display name<input required minLength="2" value={form.display_name} onChange={(e) => setForm({ ...form, display_name: e.target.value })} placeholder="Your name" /></label>}
          <label>Username<input required minLength="3" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} placeholder="e.g. aarya_01" /></label>
          <label>Password<input required type="password" minLength="8" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder="At least 8 characters" /></label>
          {error && <p className="form-error" role="alert">{error}</p>}
          <button className="button primary" disabled={busy || isShattering}>{busy ? "Please wait…" : mode === "login" ? "Sign in" : "Create secure account"}</button>
        </form>
        <p className="fine-print">Health.io provides general wellness information, not medical diagnosis or emergency care.</p>
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
