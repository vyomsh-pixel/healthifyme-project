import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import ComingSoon from "./pages/ComingSoon";

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[var(--bg)]">
        <Sidebar />
        <main className="ml-[240px] min-h-screen">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/bmi" element={<ComingSoon title="BMI" />} />
            <Route path="/food-scanner" element={<ComingSoon title="Food Scanner" />} />
            <Route path="/skin-scan" element={<ComingSoon title="Skin Scan" />} />
            <Route path="/meal-planner" element={<ComingSoon title="Meal Planner" />} />
            <Route path="/workout-planner" element={<ComingSoon title="Workout Planner" />} />
            <Route path="/workout-analytics" element={<ComingSoon title="Workout Analytics" />} />
            <Route path="/history" element={<ComingSoon title="History" />} />
            <Route path="/profile" element={<ComingSoon title="Profile" />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}