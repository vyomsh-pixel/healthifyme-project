import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import HealthScoreMark from "../components/HealthScoreMark";
import StatCard from "../components/StatCard";
import { request } from "../lib/api";

const ACTIVITY_LABELS = { BMI: "BMI check", FOOD: "Food log", SKIN: "Skin note", MEAL_PLAN: "Meal plan", WORKOUT: "Workout completed" };
const formatDate = (value) => value ? new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date(`${value}Z`)) : "Not yet";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const reload = () => request("/dashboard").then(setData).catch((err) => setError(err.message));
  useEffect(() => { reload(); }, []);

  if (error) return <Page><h1>Dashboard</h1><div className="notice error">{error} <button onClick={() => { setError(""); reload(); }}>Try again</button></div></Page>;
  if (!data) return <Page><p className="loading">Loading your private dashboard…</p></Page>;
  const { latest, today_nutrition: nutrition, counts } = data;
  const caloriePercent = Math.min(100, Math.round((nutrition.calories / nutrition.calorie_goal) * 100));
  const proteinPercent = Math.min(100, Math.round((nutrition.protein_g / nutrition.protein_goal) * 100));

  return <Page>
    <header className="page-header"><p className="eyebrow">YOUR WELLNESS OVERVIEW</p><h1>Hi, {data.user.display_name.split(" ")[0]}.</h1><p>Small, consistent actions are the point—not a perfect score.</p></header>
    <div className="dashboard-top">
      <section className="score-card"><p className="label">WELLNESS CONSISTENCY</p><HealthScoreMark score={data.health_score} /><p className="score-note">Based on profile completion, recent food logs, completed workouts, meal plans, and your latest BMI. It is not a medical score.</p></section>
      <section className="quick-actions"><p className="label">TODAY’S STARTING POINT</p><h2>{data.profile.goal ? `Build toward ${data.profile.goal}` : "Set a goal to personalize Health.io"}</h2><p>Log one thing now. That is enough to keep your trend moving.</p><div className="action-row"><Link className="button primary" to="/check-in">Check in</Link><Link className="button secondary" to="/food-scanner">Log food</Link></div></section>
    </div>
    <section className="stat-grid">
      <StatCard label="BMI records" value={counts.bmi_records} />
      <StatCard label="Food logs" value={counts.food_logs} />
      <StatCard label="Completed workouts" value={counts.completed_workouts} />
      <StatCard label="Meal plans" value={counts.meal_plans} accent />
    </section>
    <section className="two-column">
      <article className="panel"><p className="label">TODAY’S NUTRITION</p><h2>{nutrition.calories} <span>of {nutrition.calorie_goal} kcal</span></h2><Progress value={caloriePercent} label="Calories" /><h2>{nutrition.protein_g}g <span>of {nutrition.protein_goal}g protein</span></h2><Progress value={proteinPercent} label="Protein" /><p className="muted">Food values are estimates; serving size makes a big difference.</p></article>
      <article className="panel"><p className="label">LATEST BMI</p>{latest.bmi ? <><h2>{latest.bmi.bmi} <span>{latest.bmi.category}</span></h2><p>{latest.bmi.guidance}</p><p className="muted">Recorded {formatDate(latest.bmi.created_at)}</p></> : <Empty text="Add a BMI check to see your trend." to="/bmi" action="Calculate BMI" />}</article>
      <article className="panel"><p className="label">LATEST MEAL PLAN</p>{latest.meal ? <><h2>{latest.meal.goal}</h2><p>{latest.meal.diet_type} · {latest.meal.meals_per_day} meals/day</p><Link className="text-link" to="/meal-planner">Open meal planner →</Link></> : <Empty text="Create a practical plan around your food preferences." to="/meal-planner" action="Plan meals" />}</article>
      <article className="panel"><p className="label">RECENT ACTIVITY</p>{data.recent_activity.length ? <ul className="activity-list">{data.recent_activity.map((item) => <li key={`${item.type}-${item.id}`}><span className="activity-dot" /><span>{ACTIVITY_LABELS[item.type] || item.type}</span><time>{formatDate(item.created_at)}</time></li>)}</ul> : <Empty text="Your activities will appear here." to="/check-in" action="Start check-in" />}</article>
    </section>
  </Page>;
}

export function Page({ children }) { return <div className="page-wrap">{children}</div>; }
function Progress({ value, label }) { return <div className="progress-block"><div><span>{label}</span><b>{value}%</b></div><div className="progress-track"><i style={{ width: `${value}%` }} /></div></div>; }
function Empty({ text, to, action }) { return <div className="empty"><p>{text}</p><Link className="text-link" to={to}>{action} →</Link></div>; }
