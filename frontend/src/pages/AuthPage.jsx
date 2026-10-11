import { useState, useEffect, useRef } from "react";
import { useLocation, useNavigate, Link } from "react-router-dom";
import { authenticate, authenticateGoogle } from "../lib/api";
import { signInWithGooglePopup } from "../lib/firebase";

export const MANDATORY_DISCLAIMER =
  "Health.io is a personal wellness visualization tool for self-tracking. It is not intended to diagnose, treat, or replace professional medical advice.";

export const CONSENT_COPY =
  "I consent to Health.io storing my self-tracked wellness metrics and processing inputs via AI for personal visualization.";

export function LegalDocumentModal({ docType, onClose }) {
  if (!docType) return null;
  const isPrivacy = docType === "privacy";
  return (
    <div
      className="legal-modal-backdrop"
      role="dialog"
      aria-modal="true"
      aria-labelledby="legal-modal-title"
      onClick={onClose}
    >
      <div className="legal-modal-card panel" onClick={(e) => e.stopPropagation()}>
        <p className="eyebrow">{isPrivacy ? "PRIVACY POLICY (/PRIVACY)" : "TERMS OF SERVICE (/TERMS)"}</p>
        <h2 id="legal-modal-title" style={{ marginTop: "0.35rem" }}>
          {isPrivacy ? "Health.io Privacy Notice" : "Health.io Terms of Service"}
        </h2>
        <div className="legal-placeholder-box">
          <code>TODO(LEGAL): Supply official organization legal copy</code>
          <p style={{ margin: "0.5rem 0 0", fontSize: "0.85rem", color: "var(--text-secondary)" }}>
            {isPrivacy
              ? "Placeholder for organization-specific data controller details, retention schedules, third-party AI processor disclosures, and jurisdiction-specific privacy rights."
              : "Placeholder for organization-specific terms of use, acceptable use policy, limitation of liability, and governing law."}
          </p>
        </div>
        <div className="legal-disclaimer-callout">
          <strong>Mandatory Wellness Disclaimer</strong>
          <p style={{ margin: "0.35rem 0 0" }}>{MANDATORY_DISCLAIMER}</p>
        </div>
        <ul className="plain-list" style={{ fontSize: "0.85rem", color: "var(--text-secondary)", lineHeight: 1.6, marginTop: "0.75rem" }}>
          <li>• Self-tracked metrics (BMI, food logs, skin notes, workouts, check-ins) are stored for your personal visualization.</li>
          <li>• You may export your complete data archive as JSON or permanently delete your account and all data at any time from your Profile page.</li>
        </ul>
        <div style={{ marginTop: "1.25rem", display: "flex", justifyContent: "flex-end" }}>
          <button type="button" className="button primary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

export default function AuthPage({ onAuthenticated }) {
  const location = useLocation();
  const navigate = useNavigate();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ display_name: "", username: "", password: "" });
  const [consentData, setConsentData] = useState(false);
  const [consentDisclaimer, setConsentDisclaimer] = useState(false);
  const [legalDoc, setLegalDoc] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [isShattering, setIsShattering] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const timersRef = useRef([]);

  useEffect(() => {
    if (location.pathname === "/privacy") setLegalDoc("privacy");
    else if (location.pathname === "/terms") setLegalDoc("terms");
    else setLegalDoc(null);
  }, [location.pathname]);

  useEffect(() => {
    const timers = timersRef.current;
    return () => {
      timers.forEach((id) => clearTimeout(id));
    };
  }, []);

  function closeLegalModal() {
    setLegalDoc(null);
    if (location.pathname === "/privacy" || location.pathname === "/terms") {
      navigate("/", { replace: true });
    }
  }

  function startTransition(session) {
    const reducedMotion =
      typeof window !== "undefined" &&
      window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches;

    setIsShattering(true);
    if (reducedMotion) {
      setIsLoading(true);
      const t = setTimeout(() => onAuthenticated(session), 150);
      timersRef.current.push(t);
      return;
    }

    const t1 = setTimeout(() => setIsLoading(true), 280);
    const t2 = setTimeout(() => {
      onAuthenticated(session);
    }, 1150);
    timersRef.current.push(t1, t2);
  }

  function verifyConsentGate() {
    if (!consentData || !consentDisclaimer) {
      setError("Please accept both the Data Consent and Wellness Disclaimer checkboxes before continuing.");
      return false;
    }
    return true;
  }

  async function handleGoogleSignIn() {
    setError("");
    if (!verifyConsentGate()) return;
    setBusy(true);
    try {
      const googleData = await signInWithGooglePopup();
      const session = await authenticateGoogle({ ...googleData, consent_accepted: true });
      startTransition(session);
    } catch (err) {
      setError(err.message || "Google Authentication failed.");
      setBusy(false);
    }
  }

  async function submit(event) {
    event.preventDefault();
    setError("");
    if (!verifyConsentGate()) return;
    setBusy(true);
    try {
      const payload =
        mode === "login"
          ? { username: form.username, password: form.password }
          : { ...form, consent_accepted: true };
      const session = await authenticate(mode, payload);
      startTransition(session);
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  const allConsented = consentData && consentDisclaimer;

  return (
    <main className={`auth-shell ${isShattering ? "shattering" : ""}`}>
      {/* Full Screen Crack SVG Overlay */}
      <svg className="full-screen-crack" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
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
          <p className="auth-copy" style={{ color: "var(--text-primary)", fontWeight: "600", marginBottom: "1.25rem", fontSize: "1.15rem", lineHeight: 1.4, letterSpacing: "-0.01em" }}>
            Life happens behind a screen.<br />Health.io is the crack in the glass.
          </p>

          {/* Mandatory Pre-Use Consent & Wellness Disclaimer Gate */}
          <fieldset className="consent-gate" aria-label="Data authorization and wellness disclaimer">
            <legend className="eyebrow" style={{ marginBottom: "0.5rem" }}>REQUIRED BEFORE CONTINUING</legend>
            <label className="consent-checkbox-label" htmlFor="consent-data-checkbox">
              <input
                id="consent-data-checkbox"
                type="checkbox"
                required
                checked={consentData}
                onChange={(e) => {
                  setConsentData(e.target.checked);
                  if (error) setError("");
                }}
              />
              <span>{CONSENT_COPY}</span>
            </label>
            <label className="consent-checkbox-label" htmlFor="consent-disclaimer-checkbox">
              <input
                id="consent-disclaimer-checkbox"
                type="checkbox"
                required
                checked={consentDisclaimer}
                onChange={(e) => {
                  setConsentDisclaimer(e.target.checked);
                  if (error) setError("");
                }}
              />
              <span>{MANDATORY_DISCLAIMER}</span>
            </label>
          </fieldset>

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

          <div className="auth-tabs" role="tablist" aria-label="Authentication mode">
            <button
              role="tab"
              aria-selected={mode === "login"}
              className={mode === "login" ? "active" : ""}
              onClick={() => setMode("login")}
              type="button"
            >
              Sign in
            </button>
            <button
              role="tab"
              aria-selected={mode === "register"}
              className={mode === "register" ? "active" : ""}
              onClick={() => setMode("register")}
              type="button"
            >
              Create account
            </button>
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
            <button
              className="button primary"
              disabled={busy || isShattering || !allConsented}
              title={!allConsented ? "Please accept both checkboxes above to continue" : undefined}
            >
              {busy ? "Please wait…" : mode === "login" ? "Sign in" : "Create secure account"}
            </button>
          </form>

          <p className="fine-print">{MANDATORY_DISCLAIMER}</p>
          <div className="auth-legal-links">
            <Link to="/privacy" onClick={(e) => { e.preventDefault(); setLegalDoc("privacy"); navigate("/privacy"); }}>
              Privacy Policy
            </Link>
            <span aria-hidden="true">·</span>
            <Link to="/terms" onClick={(e) => { e.preventDefault(); setLegalDoc("terms"); navigate("/terms"); }}>
              Terms of Service
            </Link>
          </div>
        </div>
      </section>

      <LegalDocumentModal docType={legalDoc} onClose={closeLegalModal} />

      <div className={`global-loading-screen ${isLoading ? "visible" : ""}`} role="status" aria-live="polite">
        <div className="bio-pulse-wrap" aria-hidden="true">
          <svg className="bio-pulse-svg" width="76" height="76" viewBox="0 0 76 76" fill="none">
            <circle className="bio-pulse-ring-outer" cx="38" cy="38" r="32" stroke="#34D399" strokeWidth="1.5" strokeDasharray="6 4" />
            <circle className="bio-pulse-ring-inner" cx="38" cy="38" r="24" stroke="#2F855A" strokeWidth="2.5" />
            <path
              className="bio-pulse-wave"
              d="M18 38 H28 L32 27 L37 49 L42 33 L45 38 H58"
              stroke="#10B981"
              strokeWidth="2.6"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
        <h2 className="loading-text">Synchronizing your wellness workspace…</h2>
        <div className="loading-track premium">
          <div className="loading-bar premium" style={{ transform: `scaleX(${isLoading ? 1 : 0})` }}></div>
        </div>
      </div>
    </main>
  );
}
