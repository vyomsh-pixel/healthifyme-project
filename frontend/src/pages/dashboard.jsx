import { useEffect, useState } from "react";
import { getDashboard } from "../lib/api";
import HealthScoreMark from "../components/HealthScoreMark";
import StatCard from "../components/StatCard";

const TYPE_META = {
  BMI: { label: "BMI Check", color: "var(--accent)" },
  "Food Scan": { label: "Food Scan", color: "var(--success)" },
  "Skin Scan": { label: "Skin Scan", color: "var(--warning)" },
};

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center text-center py-24 border border-dashed border-[var(--border-strong)] rounded-2xl">
      <p className="font-display text-2xl text-[var(--text-primary)] mb-2">
        Nothing logged yet
      </p>
      <p className="text-[var(--text-secondary)] text-sm max-w-sm">
        Run a BMI check, scan a meal, or log a skin photo — your dashboard
        fills in as soon as you do.
      </p>
    </div>
  );
}

function SectionLabel({ children }) {
  return (
    <p className="font-mono text-[11px] uppercase tracking-wider text-[var(--text-tertiary)] mb-3">
      {children}
    </p>
  );
}

function truncate(text, n = 220) {
  if (!text) return "";
  return text.length > n ? text.slice(0, n).trim() + "…" : text;
}

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    getDashboard()
      .then(setData)
      .catch((err) => setError(err.message));
  }, []);

  if (error) {
    return (
      <div className="p-10">
        <p className="text-[var(--danger)] font-mono text-sm">
          Couldn't reach the API — is the backend running on :8000? ({error})
        </p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="p-10">
        <p className="text-[var(--text-tertiary)] font-mono text-sm">
          Loading…
        </p>
      </div>
    );
  }

  if (!data.has_data) {
    return (
      <div className="max-w-5xl mx-auto px-10 py-12">
        <Header />
        <EmptyState />
      </div>
    );
  }

  const { counts, health_score, latest_bmi, latest_food, latest_skin, latest_meal, recent_activity } = data;

  return (
    <div className="max-w-6xl mx-auto px-10 py-12">
      <Header />

      <div className="grid grid-cols-[auto_1fr] gap-8 mb-12 items-start">
        <div className="bg-[var(--surface)] border border-[var(--border)] rounded-2xl px-8 py-7">
          <SectionLabel>Health Score</SectionLabel>
          <HealthScoreMark score={health_score} />
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 self-stretch">
          <StatCard label="BMI Records" value={counts.bmi_records} />
          <StatCard label="Food Scans" value={counts.food_scans} />
          <StatCard label="Skin Scans" value={counts.skin_scans} />
          <StatCard label="Meal Plans" value={counts.meal_plans} accent />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-[var(--surface)] border border-[var(--border)] rounded-2xl px-6 py-5">
          <SectionLabel>Latest BMI</SectionLabel>
          {latest_bmi ? (
            <div className="flex items-end justify-between">
              <div>
                <span className="font-display text-4xl font-semibold text-[var(--text-primary)]">
                  {latest_bmi.bmi}
                </span>
                <p className="text-sm text-[var(--text-secondary)] mt-1">
                  {latest_bmi.category}
                </p>
              </div>
              <p className="font-mono text-[11px] text-[var(--text-tertiary)]">
                {latest_bmi.timestamp}
              </p>
            </div>
          ) : (
            <p className="text-sm text-[var(--text-tertiary)]">No BMI records yet.</p>
          )}
        </div>

        <div className="bg-[var(--surface)] border border-[var(--border)] rounded-2xl px-6 py-5">
          <SectionLabel>Latest Meal Plan</SectionLabel>
          {latest_meal ? (
            <div>
              <div className="flex gap-4 text-sm mb-2">
                <span className="text-[var(--text-secondary)]">
                  Goal: <span className="text-[var(--text-primary)] font-medium">{latest_meal.goal}</span>
                </span>
                <span className="text-[var(--text-secondary)]">
                  Diet: <span className="text-[var(--text-primary)] font-medium">{latest_meal.diet_type}</span>
                </span>
              </div>
              <p className="font-mono text-xs text-[var(--text-tertiary)]">
                Budget ₹{latest_meal.budget}/day
              </p>
            </div>
          ) : (
            <p className="text-sm text-[var(--text-tertiary)]">No meal plans generated yet.</p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-12">
        <div className="bg-[var(--surface)] border border-[var(--border)] rounded-2xl px-6 py-5">
          <SectionLabel>Latest Food Scan</SectionLabel>
          {latest_food ? (
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              {truncate(latest_food.result)}
            </p>
          ) : (
            <p className="text-sm text-[var(--text-tertiary)]">No food scans yet.</p>
          )}
        </div>

        <div className="bg-[var(--surface)] border border-[var(--border)] rounded-2xl px-6 py-5">
          <SectionLabel>Latest Skin Scan</SectionLabel>
          {latest_skin ? (
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              {truncate(latest_skin.result)}
            </p>
          ) : (
            <p className="text-sm text-[var(--text-tertiary)]">No skin scans yet.</p>
          )}
        </div>
      </div>

      <div>
        <SectionLabel>Recent Activity</SectionLabel>
        <div className="bg-[var(--surface)] border border-[var(--border)] rounded-2xl divide-y divide-[var(--border)]">
          {recent_activity.map((item, i) => {
            const meta = TYPE_META[item.type] || { label: item.type, color: "var(--text-tertiary)" };
            return (
              <div key={i} className="flex items-center gap-4 px-6 py-3.5">
                <span
                  className="w-1.5 h-1.5 rounded-full flex-shrink-0"
                  style={{ background: meta.color }}
                />
                <span className="text-sm font-medium text-[var(--text-primary)] flex-1">
                  {meta.label}
                </span>
                <span className="font-mono text-[11px] text-[var(--text-tertiary)]">
                  {item.timestamp}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function Header() {
  return (
    <div className="mb-10 pb-6 border-b border-[var(--border)]">
      <h1 className="font-display text-4xl font-semibold tracking-tight text-[var(--text-primary)]">
        Dashboard
      </h1>
      <p className="text-[var(--text-secondary)] text-sm mt-1.5">
        Your health overview, logged and quantified.
      </p>
    </div>
  );
}