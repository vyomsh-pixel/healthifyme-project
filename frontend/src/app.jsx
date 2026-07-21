import { useState } from "react";
import { useLocation, BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import Sidebar from "./components/sidebar";
import Dashboard from "./pages/dashboard";
import AuthPage from "./pages/AuthPage";
import {
  BMIPage, FoodPage, SkinPage, MealPlannerPage, WorkoutPage,
  AnalyticsPage, HistoryPage, ProfilePage, CheckinPage, ChatPage,
} from "./pages/HealthPages";
import { getSession, signOut } from "./lib/api";

function AppShell({ session, onSignOut }) {
  const location = useLocation();
  
  let bgImage = "url('/sky-field-bg.png')";
  if (location.pathname === "/assistant") bgImage = "url('/ai-beach-bg.png')";
  else if (location.pathname === "/workout-planner" || location.pathname === "/bmi") bgImage = "url('/fitness-mountain-bg.png')";
  else if (location.pathname === "/meal-planner" || location.pathname === "/food-scanner") bgImage = "url('/nutrition-forest-bg.png')";
  else if (location.pathname === "/history" || location.pathname === "/profile" || location.pathname === "/workout-analytics") bgImage = "url('/history-sunset-bg.png')";

  return (
    <div className="app-global-bg min-h-screen" style={{ '--dynamic-bg': bgImage }}>
      <Sidebar username={session.user.display_name} onSignOut={onSignOut} />
      <main className="app-main">
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
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/assistant" element={<ChatPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  const [session, setSession] = useState(getSession);

  async function handleSignOut() {
    await signOut();
    setSession(null);
  }

  return (
    <BrowserRouter>
      {session ? <AppShell session={session} onSignOut={handleSignOut} /> : <AuthPage onAuthenticated={setSession} />}
    </BrowserRouter>
  );
}
