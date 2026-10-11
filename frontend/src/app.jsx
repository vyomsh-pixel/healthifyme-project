import { lazy, Suspense, useEffect, useState } from "react";
import { useLocation, useNavigate, BrowserRouter, Navigate, Route, Routes, Link } from "react-router-dom";
import Sidebar from "./components/sidebar";
import Dashboard from "./pages/dashboard";
import AuthPage, { MANDATORY_DISCLAIMER, LegalDocumentModal } from "./pages/AuthPage";
import { getSession, signOut } from "./lib/api";

const CheckinPage = lazy(() => import("./pages/HealthPages").then((m) => ({ default: m.CheckinPage })));
const BMIPage = lazy(() => import("./pages/HealthPages").then((m) => ({ default: m.BMIPage })));
const FoodPage = lazy(() => import("./pages/HealthPages").then((m) => ({ default: m.FoodPage })));
const SkinPage = lazy(() => import("./pages/HealthPages").then((m) => ({ default: m.SkinPage })));
const MealPlannerPage = lazy(() => import("./pages/HealthPages").then((m) => ({ default: m.MealPlannerPage })));
const WorkoutPage = lazy(() => import("./pages/HealthPages").then((m) => ({ default: m.WorkoutPage })));
const AnalyticsPage = lazy(() => import("./pages/HealthPages").then((m) => ({ default: m.AnalyticsPage })));
const HistoryPage = lazy(() => import("./pages/HealthPages").then((m) => ({ default: m.HistoryPage })));
const ProfilePage = lazy(() => import("./pages/HealthPages").then((m) => ({ default: m.ProfilePage })));
const ChatPage = lazy(() => import("./pages/HealthPages").then((m) => ({ default: m.ChatPage })));

function AppShell({ session, onSignOut }) {
  const location = useLocation();
  const navigate = useNavigate();

  let bgImage = "url('/sky-field-bg.png')";
  if (location.pathname === "/assistant") bgImage = "url('/ai-beach-bg.png')";
  else if (location.pathname === "/workout-planner" || location.pathname === "/bmi") bgImage = "url('/fitness-mountain-bg.png')";
  else if (location.pathname === "/meal-planner" || location.pathname === "/food-scanner") bgImage = "url('/nutrition-forest-bg.png')";
  else if (location.pathname === "/history" || location.pathname === "/profile" || location.pathname === "/workout-analytics") bgImage = "url('/history-sunset-bg.png')";

  const legalDoc =
    location.pathname === "/privacy" ? "privacy" : location.pathname === "/terms" ? "terms" : null;

  return (
    <div className="app-global-bg min-h-screen" style={{ "--dynamic-bg": bgImage }}>
      <Sidebar username={session.user.display_name} onSignOut={onSignOut} />
      <main className="app-main">
        <Suspense fallback={<div className="page-wrap"><p className="loading">Loading workspace…</p></div>}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/check-in" element={<CheckinPage />} />
            <Route path="/bmi" element={<BMIPage />} />
            <Route path="/food-scanner" element={<FoodPage />} />
            <Route path="/skin-scan" element={<SkinPage />} />
            <Route path="/meal-planner" element={<MealPlannerPage />} />
            <Route path="/workout-planner" element={<WorkoutPage />} />
            <Route path="/workout-analytics" element={<AnalyticsPage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/profile" element={<ProfilePage onSignOut={onSignOut} />} />
            <Route path="/assistant" element={<ChatPage />} />
            <Route path="/privacy" element={<Dashboard />} />
            <Route path="/terms" element={<Dashboard />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
        <footer className="app-global-footer" role="contentinfo">
          <p>{MANDATORY_DISCLAIMER}</p>
          <div className="footer-legal-links">
            <Link to="/privacy">Privacy Policy</Link>
            <span aria-hidden="true">·</span>
            <Link to="/terms">Terms of Service</Link>
          </div>
        </footer>
      </main>
      <LegalDocumentModal docType={legalDoc} onClose={() => navigate("/", { replace: true })} />
    </div>
  );
}

export default function App() {
  const [session, setSession] = useState(getSession);

  useEffect(() => {
    const handleUnauthorized = () => setSession(null);
    window.addEventListener("healthio:unauthorized", handleUnauthorized);
    return () => window.removeEventListener("healthio:unauthorized", handleUnauthorized);
  }, []);

  function handleSignOut() {
    setSession(null);
    signOut();
  }

  return (
    <BrowserRouter>
      {session ? <AppShell session={session} onSignOut={handleSignOut} /> : <AuthPage onAuthenticated={setSession} />}
    </BrowserRouter>
  );
}
