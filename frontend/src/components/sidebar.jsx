import { NavLink } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: "home" },
  { to: "/check-in", label: "Daily check-in", icon: "check" },
  { to: "/bmi", label: "BMI", icon: "ruler" },
  { to: "/food-scanner", label: "Food Scanner", icon: "scan" },
  { to: "/skin-scan", label: "Skin Scan", icon: "droplet" },
  { to: "/meal-planner", label: "Meal Planner", icon: "utensils" },
  { to: "/workout-planner", label: "Workout Planner", icon: "dumbbell" },
  { to: "/workout-analytics", label: "Analytics", icon: "chart" },
  { to: "/history", label: "History", icon: "clock" },
  { to: "/profile", label: "Profile", icon: "user" },
  { to: "/assistant", label: "AI assistant", icon: "chat" },
];

function Icon({ name, className }) {
  const paths = {
    home: "M3 12l9-9 9 9M5 10v10h14V10",
    ruler: "M3 16l5-5 12 12M14 8l2 2M11 11l2 2M8 14l2 2",
    scan: "M4 7V4h3M17 4h3v3M20 17v3h-3M7 20H4v-3M9 9h6v6H9z",
    droplet: "M12 3c4 5 6 8 6 11a6 6 0 11-12 0c0-3 2-6 6-11z",
    utensils: "M7 3v8M5 3v4a2 2 0 004 0V3M17 3v18M17 9a3 3 0 003-3V3",
    dumbbell: "M4 9v6M2 11v2M22 11v2M20 9v6M7 12h10M7 9v6M17 9v6",
    chart: "M4 20V10M10 20V4M16 20v-8M22 20H2",
    clock: "M12 7v5l3 3M12 21a9 9 0 100-18 9 9 0 000 18z",
    user: "M12 12a4 4 0 100-8 4 4 0 000 8zM4 21c0-4 4-7 8-7s8 3 8 7",
    check: "M5 12l4 4L19 6",
    chat: "M21 11.5a8.4 8.4 0 01-9 8.5 9.5 9.5 0 01-4-.9L3 21l1.5-4A8.4 8.4 0 013 11.5a9 9 0 0118 0z",
  };
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d={paths[name]} />
    </svg>
  );
}

export default function Sidebar({ username = "Member", onSignOut }) {
  return (
    <aside className="app-sidebar fixed left-0 top-0 h-screen w-[240px] flex flex-col border-r border-[var(--border)] bg-[var(--surface)]">
      <div className="px-6 pt-7 pb-6">
        <div className="flex items-baseline gap-1.5">
          <span className="font-display text-2xl font-semibold tracking-tight text-[var(--text-primary)]">
            Health
          </span>
          <span className="font-display text-2xl font-semibold tracking-tight text-[var(--accent)]">
            .io
          </span>
        </div>
        <p className="font-mono text-[11px] text-[var(--text-tertiary)] mt-1 tracking-wide">
          QUANTIFIED WELLNESS
        </p>
      </div>

      <nav className="flex-1 px-3 overflow-y-auto">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg mb-0.5 text-[13.5px] font-medium transition-colors ${
                isActive
                  ? "bg-[var(--accent-dim)] text-[var(--accent)]"
                  : "text-[var(--text-secondary)] hover:bg-white/[0.04] hover:text-[var(--text-primary)]"
              }`
            }
          >
            <Icon name={item.icon} className="w-[17px] h-[17px] flex-shrink-0" />
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="px-4 py-4 border-t border-[var(--border)]">
        <div className="flex items-center gap-2.5 px-2 py-2 rounded-lg">
          <div className="w-8 h-8 rounded-full bg-[var(--accent)] flex items-center justify-center font-display text-sm font-semibold text-[#0a0e16] flex-shrink-0">
            {username.charAt(0).toUpperCase()}
          </div>
          <div className="min-w-0">
            <p className="text-[13px] font-medium text-[var(--text-primary)] truncate">
              {username}
            </p>
            <p className="font-mono text-[10px] text-[var(--text-tertiary)]">
              SIGNED IN
            </p>
          </div>
        </div>
        <button className="sidebar-signout" onClick={onSignOut}>Sign out</button>
      </div>
    </aside>
  );
}
