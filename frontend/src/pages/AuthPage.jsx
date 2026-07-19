import { useState } from "react";
import { authenticate } from "../lib/api";

export default function AuthPage({ onAuthenticated }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ display_name: "", username: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setBusy(true); setError("");
    try {
      const session = await authenticate(mode, mode === "login" ? { username: form.username, password: form.password } : form);
      onAuthenticated(session);
    } catch (err) { setError(err.message); } finally { setBusy(false); }
  }

  return <main className="auth-shell">
    <section className="auth-panel">
      <p className="eyebrow">PRIVATE WELLNESS, MADE PRACTICAL</p>
      <h1 className="brand-title">Health<span>.io</span></h1>
      <p className="auth-copy">Track habits, plan meals, and build a routine you can actually sustain.</p>
      <div className="auth-tabs" role="tablist">
        <button className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>Sign in</button>
        <button className={mode === "register" ? "active" : ""} onClick={() => setMode("register")}>Create account</button>
      </div>
      <form onSubmit={submit} className="form-stack">
        {mode === "register" && <label>Display name<input required minLength="2" value={form.display_name} onChange={(e) => setForm({ ...form, display_name: e.target.value })} placeholder="Your name" /></label>}
        <label>Username<input required minLength="3" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} placeholder="e.g. aarya_01" /></label>
        <label>Password<input required type="password" minLength="8" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder="At least 8 characters" /></label>
        {error && <p className="form-error" role="alert">{error}</p>}
        <button className="button primary" disabled={busy}>{busy ? "Please wait…" : mode === "login" ? "Sign in" : "Create secure account"}</button>
      </form>
      <p className="fine-print">Health.io provides general wellness information, not medical diagnosis or emergency care.</p>
    </section>
  </main>;
}
