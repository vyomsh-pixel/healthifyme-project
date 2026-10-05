import { useCallback, useEffect, useState, useRef } from "react";
import { Page } from "./dashboard";
import { request } from "../lib/api";
import { getBMIStatus } from "../lib/bmi";
import { Line, Bar } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, Filler } from "chart.js";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, Filler);

const initialProfile = { age: "", gender: "", height_cm: "", weight_kg: "", goal: "Fitness", activity_level: "Moderate", diet_preference: "Vegetarian", bio: "" };
const dateTime = (value) => value ? new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date(value.endsWith("Z") || value.includes("+") ? value : `${value}Z`)) : "—";
const shortDate = (value) => { if (!value) return ""; const d = new Date(value.endsWith("Z") || value.includes("+") || value.includes("T") ? value : `${value}T00:00:00`); return d.toLocaleDateString(undefined, { month: "short", day: "numeric" }); };

function Notice({ notice }) { return notice ? <p className={`notice ${notice.type}`}>{notice.text}</p> : null; }
function useLoad(path, key) {
  const [state, setState] = useState({ loading: true, data: null, error: "" });
  const reload = useCallback(() => { setState((s) => ({ ...s, loading: true, error: "" })); return request(path).then((data) => setState({ loading: false, data, error: "" })).catch((e) => setState({ loading: false, data: null, error: e.message })); }, [path]);
  useEffect(() => { reload(); }, [reload, key]);
  return { ...state, reload, setData: (fn) => setState((s) => ({ ...s, data: fn(s.data) })) };
}
function FormButton({ busy, children }) { return <button className="button primary" disabled={busy}>{busy ? "Saving…" : children}</button>; }
function NumberField({ label, value, onChange, min, max, step = "1" }) { return <label>{label}<input type="number" min={min} max={max} step={step} value={value} onChange={(e) => onChange(e.target.value)} required /></label>; }
function DeleteBtn({ onClick, label = "Delete" }) {
  const [confirming, setConfirming] = useState(false);
  if (confirming) return <div className="delete-confirm"><span>Sure?</span><button type="button" className="delete-btn confirm-yes" onClick={onClick}>Yes</button><button type="button" className="delete-btn confirm-no" onClick={() => setConfirming(false)}>No</button></div>;
  return (
    <button type="button" className="delete-btn" onClick={() => setConfirming(true)} title={label}>
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M3 6h18"></path>
        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
        <line x1="10" y1="11" x2="10" y2="17"></line>
        <line x1="14" y1="11" x2="14" y2="17"></line>
      </svg>
    </button>
  );
}

// ─── Chart defaults ──────────────────────────────────
const chartFont = { family: "'Inter', sans-serif", size: 11 };
const chartDefaults = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false }, tooltip: { backgroundColor: "rgba(0,0,0,0.8)", titleFont: chartFont, bodyFont: chartFont, padding: 10, cornerRadius: 8 } },
  scales: {
    x: { grid: { display: false }, ticks: { font: chartFont, color: "var(--text-tertiary)" } },
    y: { grid: { color: "rgba(0,0,0,0.06)" }, ticks: { font: chartFont, color: "var(--text-tertiary)" } },
  },
};

// ─── Check-in ────────────────────────────────────────
export function CheckinPage() {
  const [form, setForm] = useState({ sleep_hours: "", steps: "", water_glasses: "", mood: "", energy: "", soreness: "", note: "" });
  const [notice, setNotice] = useState(null); const [busy, setBusy] = useState(false);
  const { data: historyData, reload: reloadHistory } = useLoad("/checkins/history", "checkin-history");
  const update = (key) => (value) => setForm({ ...form, [key]: value });

  // Pre-fill today's check-in
  useEffect(() => {
    request("/checkins/today").then((d) => {
      if (d.checkin) {
        const c = d.checkin;
        setForm({
          sleep_hours: c.sleep_hours ?? "", steps: c.steps ?? "", water_glasses: c.water_glasses ?? "",
          mood: c.mood ?? "", energy: c.energy ?? "", soreness: c.soreness ?? "", note: c.note ?? "",
        });
      }
    }).catch(() => {});
  }, []);

  async function submit(e) { e.preventDefault(); setBusy(true); try { await request("/checkins/today", { method: "PUT", body: numbers(form, ["sleep_hours", "steps", "water_glasses", "mood", "energy", "soreness"]) }); setNotice({ type: "success", text: "Today's check-in is saved. A small honest log is more useful than a perfect one." }); reloadHistory(); } catch (err) { setNotice({ type: "error", text: err.message }); } finally { setBusy(false); } }

  const checkins = historyData?.checkins || [];
  const moodEmoji = (v) => ["", "😞", "😐", "🙂", "😊", "🤩"][v] || "";

  return <Page><Header eyebrow="DAILY CHECK-IN" title="How are you actually doing?" copy="This takes a minute and helps turn health data into context." /><form className="panel form-grid" onSubmit={submit}>
    <NumberField label="Sleep (hours)" value={form.sleep_hours} onChange={update("sleep_hours")} min="0" max="24" step="0.5" /><NumberField label="Steps" value={form.steps} onChange={update("steps")} min="0" max="100000" />
    <NumberField label="Water (glasses)" value={form.water_glasses} onChange={update("water_glasses")} min="0" max="30" /><Scale label="Mood" value={form.mood} onChange={update("mood")} hint="1 = low · 5 = great" />
    <Scale label="Energy" value={form.energy} onChange={update("energy")} hint="1 = drained · 5 = strong" /><Scale label="Soreness" value={form.soreness} onChange={update("soreness")} hint="1 = none · 5 = high" />
    <label className="span-all">Anything worth remembering?<textarea value={form.note} onChange={(e) => update("note")(e.target.value)} placeholder="For example: busy day, slept late, workout felt good…" /></label><Notice notice={notice} /><FormButton busy={busy}>Save today's check-in</FormButton>
  </form>
  {checkins.length > 0 && <section className="panel" style={{ marginTop: "1.5rem" }}><p className="label">RECENT CHECK-INS</p>
    <div className="table-list">{checkins.map((c) => <article key={c.id} className="checkin-row">
      <div><b>{c.checkin_date}</b><span>{c.sleep_hours ? `${c.sleep_hours}h sleep` : ""}{c.steps ? ` · ${c.steps.toLocaleString()} steps` : ""}{c.water_glasses ? ` · ${c.water_glasses} glasses` : ""}</span></div>
      <div><span>{c.mood ? `Mood ${moodEmoji(c.mood)}` : ""}{c.energy ? ` · Energy ${c.energy}/5` : ""}</span>{c.note && <small style={{ display: "block", opacity: 0.7, marginTop: "0.2rem" }}>{c.note}</small>}</div>
    </article>)}</div>
  </section>}
  </Page>;
}

// ─── BMI ─────────────────────────────────────────────
export function BMIPage() {
  const [weight, setWeight] = useState(""); const [height, setHeight] = useState(""); const [record, setRecord] = useState(null); const [notice, setNotice] = useState(null); const [busy, setBusy] = useState(false); const [isStale, setIsStale] = useState(false);
  const handleWeight = (v) => { setWeight(v); if (record) { setIsStale(true); setNotice(null); } };
  const handleHeight = (v) => { setHeight(v); if (record) { setIsStale(true); setNotice(null); } };
  async function submit(e) { e.preventDefault(); setBusy(true); try { const data = await request("/records/bmi", { method: "POST", body: { weight_kg: Number(weight), height_cm: Number(height) } }); setRecord(data.record); setIsStale(false); setNotice({ type: "success", text: "BMI measurement saved to your private history." }); } catch (err) { setNotice({ type: "error", text: err.message }); } finally { setBusy(false); } }
  const bmiStatus = getBMIStatus(record?.category);
  return <Page><Header eyebrow="BODY METRIC" title="BMI, with context." copy="BMI is a screening estimate, not a diagnosis or complete picture of health." /><div className="two-column"><form className="panel form-stack" onSubmit={submit}><NumberField label="Weight (kg)" value={weight} onChange={handleWeight} min="20" max="400" step="0.1" /><NumberField label="Height (cm)" value={height} onChange={handleHeight} min="80" max="250" step="0.1" /><Notice notice={notice} /><FormButton busy={busy}>Calculate and save</FormButton></form><section className="panel result-panel" style={{ transition: "opacity 0.2s", opacity: isStale ? 0.4 : 1 }}>{record ? <><p className="label">YOUR RESULT</p><div className="hero-number">{record.bmi}</div><h2 style={{display: "flex", alignItems: "center", gap: "0.5rem"}}>{record.category} {bmiStatus && <span className={`metric-card-status status-${bmiStatus.color}`}>● {bmiStatus.label}</span>}</h2><p>{record.guidance}</p><div className="point-of-result-disclaimer" style={{ marginTop: "1rem", padding: "0.75rem 1rem", borderRadius: "8px", background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)", fontSize: "0.75rem", color: "var(--text-tertiary)", lineHeight: "1.4" }}><strong style={{ color: "var(--text-secondary)", display: "block", marginBottom: "0.2rem" }}>Personal Habit Visualization Only</strong>BMI is a simple geometric estimate (mass/height²). It does not measure body fat percentage, muscle mass, or metabolic health. Never use this as a clinical diagnosis or physician replacement.</div></> : <EmptyMessage text="Enter height and weight to calculate your BMI." />}</section></div></Page>;
}

// ─── Food Scanner ────────────────────────────────────
export function FoodPage() {
  const [form, setForm] = useState({ food_name: "", calories: "", protein_g: "", carbs_g: "", fat_g: "", note: "" }); const [notice, setNotice] = useState(null); const [busy, setBusy] = useState(false); const [preview, setPreview] = useState(null); const [base64Image, setBase64Image] = useState(null); const [analyzing, setAnalyzing] = useState(false); const [foodText, setFoodText] = useState("");
  const update = (key) => (value) => setForm({ ...form, [key]: value });
  const handleFile = (e) => { const file = e.target.files?.[0]; if (file) { setPreview(URL.createObjectURL(file)); const reader = new FileReader(); reader.onloadend = () => setBase64Image(reader.result); reader.readAsDataURL(file); } else { setPreview(null); setBase64Image(null); } };
  async function analyzeFoodInfo(type) {
    if (type === 'image' && !base64Image) return;
    if (type === 'text' && !foodText.trim()) { setNotice({ type: "error", text: "Please enter a food description first." }); return; }
    setAnalyzing(true); setNotice(null);
    try {
      const body = type === 'image' ? { image: base64Image } : { text: foodText };
      const data = await request("/analyze-food", { method: "POST", body });
      if (!data) throw new Error("No data returned from AI.");
      setForm(prev => ({ ...prev, food_name: data.food_name || prev.food_name, calories: data.calories?.toString() || prev.calories, protein_g: data.protein_g?.toString() || prev.protein_g, carbs_g: data.carbs_g?.toString() || prev.carbs_g, fat_g: data.fat_g?.toString() || prev.fat_g }));
      setNotice({ type: "success", text: "AI analysis complete! You can tweak the values before saving." });
    } catch (err) {
      setNotice({ type: "error", text: "AI Analysis failed: " + err.message });
    } finally {
      setAnalyzing(false);
    }
  }
  async function submit(e) { e.preventDefault(); setBusy(true); try { await request("/records/food", { method: "POST", body: numbers(form, ["calories", "protein_g", "carbs_g", "fat_g"]) }); setNotice({ type: "success", text: "Food log added to today's nutrition totals." }); setForm({ food_name: "", calories: "", protein_g: "", carbs_g: "", fat_g: "", note: "" }); setPreview(null); setBase64Image(null); setFoodText(""); } catch (err) { setNotice({ type: "error", text: err.message }); } finally { setBusy(false); } }
  return <Page><Header eyebrow="FOOD SCANNER & LOG" title="Photo & text-assisted food logging." copy="Take a photo or describe your meal. The AI will estimate the nutrition, which you can adjust before saving." /><div className="two-column"><form className="panel form-grid" onSubmit={submit}><label className="span-all upload-box">Food photo<input type="file" accept="image/*" onChange={handleFile} disabled={analyzing} />{preview && <img src={preview} alt="Selected food" />}</label>{base64Image && <div className="span-all"><button type="button" className="button secondary" onClick={() => analyzeFoodInfo('image')} disabled={analyzing}>{analyzing ? "Analyzing..." : "Analyze Photo with AI"}</button></div>}<div className="span-all" style={{ textAlign: "center", margin: "1rem 0", color: "var(--muted)", fontSize: "0.9rem", textTransform: "uppercase", letterSpacing: "1px" }}>— or describe it instead —</div><label className="span-all">Food Description<textarea value={foodText} onChange={(e) => setFoodText(e.target.value)} placeholder="e.g., 100g cooked white rice, 1 katori toor dal, 1 spoon ghee..." disabled={analyzing} /></label>{foodText.trim() && <div className="span-all"><button type="button" className="button secondary" onClick={() => analyzeFoodInfo('text')} disabled={analyzing}>{analyzing ? "Analyzing..." : "Analyze Text with AI"}</button></div>}<label className="span-all" style={{ marginTop: "1rem" }}>Food / meal name<input required value={form.food_name} onChange={(e) => update("food_name")(e.target.value)} placeholder="e.g. Dal rice with salad" /></label><NumberField label="Calories (kcal)" value={form.calories} onChange={update("calories")} min="0" max="10000" /><NumberField label="Protein (g)" value={form.protein_g} onChange={update("protein_g")} min="0" max="1000" step="0.1" /><NumberField label="Carbohydrates (g)" value={form.carbs_g} onChange={update("carbs_g")} min="0" max="1000" step="0.1" /><NumberField label="Fat (g)" value={form.fat_g} onChange={update("fat_g")} min="0" max="1000" step="0.1" /><label className="span-all">Notes<textarea value={form.note} onChange={(e) => update("note")(e.target.value)} placeholder="Portion, preparation, or how you felt after eating" /></label><Notice notice={notice} /><FormButton busy={busy}>Add food log</FormButton></form><section className="panel"><p className="label">ESTIMATING WELL</p><h2>AI is an assistant, not magic.</h2><ol className="plain-list"><li>Ensure good lighting in your photos.</li><li>Be specific with text (e.g., "cooked" vs "raw", mention oils/ghee).</li><li>Review the AI's numbers and tweak them if they seem off.</li></ol><div className="point-of-result-disclaimer" style={{ marginTop: "1rem", padding: "0.75rem 1rem", borderRadius: "8px", background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)", fontSize: "0.75rem", color: "var(--text-tertiary)", lineHeight: "1.4" }}><strong style={{ color: "var(--text-secondary)", display: "block", marginBottom: "0.2rem" }}>Nutritional Approximation</strong>Estimates can vary significantly based on hidden fats, cooking methods, and portions. Always adjust values based on your personal knowledge.</div></section></div></Page>;
}

// ─── Skin ────────────────────────────────────────────
export function SkinPage() {
  const [summary, setSummary] = useState(""); const [concerns, setConcerns] = useState([]); const [notice, setNotice] = useState(null); const [busy, setBusy] = useState(false);
  const [preview, setPreview] = useState(null); const [base64Image, setBase64Image] = useState(null); const [analyzing, setAnalyzing] = useState(false);
  const options = ["Acne / pimples", "Dryness", "Oiliness", "Redness", "Pigmentation", "Dark circles"];
  const handleFile = (e) => { const file = e.target.files?.[0]; if (file) { setPreview(URL.createObjectURL(file)); const reader = new FileReader(); reader.onloadend = () => setBase64Image(reader.result); reader.readAsDataURL(file); } else { setPreview(null); setBase64Image(null); } };
  async function analyzeSkin() { if (!base64Image) return; setAnalyzing(true); setNotice(null); try { const data = await request("/analyze-skin", { method: "POST", body: { image: base64Image } }); if (data.concerns) { setConcerns(prev => Array.from(new Set([...prev, ...data.concerns.filter(c => options.includes(c))]))); } if (data.summary) { setSummary(prev => prev ? prev + "\n\nAI Notes: " + data.summary : "AI Notes: " + data.summary); } setNotice({ type: "success", text: "AI skin analysis complete! Review the notes before saving." }); } catch (err) { setNotice({ type: "error", text: "AI Analysis failed: " + err.message }); } finally { setAnalyzing(false); } }
  async function submit(e) { e.preventDefault(); setBusy(true); try { await request("/records/skin", { method: "POST", body: { summary, concerns } }); setNotice({ type: "success", text: "Private skin note saved. It is not a diagnosis." }); setSummary(""); setConcerns([]); setPreview(null); setBase64Image(null); } catch (err) { setNotice({ type: "error", text: err.message }); } finally { setBusy(false); } }
  return <Page><Header eyebrow="SKIN JOURNAL" title="Notice patterns safely." copy="Upload a photo to let AI help log cosmetic observations. Persistent, painful, sudden, or concerning changes deserve a clinician's input." /><div className="two-column"><form className="panel form-stack" onSubmit={submit}><label className="upload-box">Optional skin photo<input type="file" accept="image/*" onChange={handleFile} />{preview && <img src={preview} alt="Skin" />}</label>{base64Image && <button type="button" className="button secondary" onClick={analyzeSkin} disabled={analyzing}>{analyzing ? "Analyzing..." : "Analyze Photo with AI"}</button>}<fieldset><legend>What are you noticing?</legend><div className="choice-grid">{options.map((item) => <label className="check-choice" key={item}><input type="checkbox" checked={concerns.includes(item)} onChange={() => setConcerns(concerns.includes(item) ? concerns.filter((x) => x !== item) : [...concerns, item])} />{item}</label>)}</div></fieldset><label>Notes<textarea required minLength="2" value={summary} onChange={(e) => setSummary(e.target.value)} placeholder="When it started, products used, discomfort, and anything that changed…" /></label><Notice notice={notice} /><FormButton busy={busy}>Save skin note</FormButton></form><section className="panel safety-panel"><p className="label">WHEN TO GET HELP</p><h2>Don't wait on an app for urgent symptoms.</h2><p>Seek professional care for severe swelling, breathing difficulty, rapidly spreading rash, significant pain, fever, signs of infection, or anything worrying you.</p><div className="point-of-result-disclaimer" style={{ marginTop: "1rem", padding: "0.75rem 1rem", borderRadius: "8px", background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)", fontSize: "0.75rem", color: "var(--text-tertiary)", lineHeight: "1.4" }}><strong style={{ color: "var(--text-secondary)", display: "block", marginBottom: "0.2rem" }}>Cosmetic Self-Tracking Only</strong>This is an AI visual estimate of surface skin features, not a clinical diagnosis. Photos are streamed to Google Gemini for real-time analysis and are not retained on our servers. Health.io never prescribes treatment.</div></section></div></Page>;
}

// ─── Meal Planner (with delete) ──────────────────────
export function MealPlannerPage() {
  const [form, setForm] = useState({ goal: "Fitness", diet_type: "Vegetarian", budget: "", meals_per_day: "4", extra_instructions: "" }); const [plan, setPlan] = useState(null); const [notice, setNotice] = useState(null); const [busy, setBusy] = useState(false); const { data, reload, setData } = useLoad("/meal-plans", "plans");
  const update = (key) => (value) => setForm({ ...form, [key]: value });
  async function submit(e) { e.preventDefault(); setBusy(true); try { const result = await request("/meal-plans", { method: "POST", body: { ...form, budget: form.budget ? Number(form.budget) : null, meals_per_day: Number(form.meals_per_day) } }); setPlan(result.meal_plan); reload(); setNotice({ type: "success", text: "Your practical meal plan is ready and saved." }); } catch (err) { setNotice({ type: "error", text: err.message }); } finally { setBusy(false); } }
  async function deletePlan(id) { try { await request(`/meal-plans/${id}`, { method: "DELETE" }); setData((d) => ({ ...d, meal_plans: d.meal_plans.filter((p) => p.id !== id) })); } catch (err) { setNotice({ type: "error", text: err.message }); } }
  return <Page><Header eyebrow="MEAL PLANNER" title="Plan for real life, not perfection." copy="Plans are general guidance. For medical nutrition needs, consult a registered dietitian." /><div className="two-column"><form className="panel form-grid" onSubmit={submit}><label>Goal<select value={form.goal} onChange={(e) => update("goal")(e.target.value)}><option>Fat Loss</option><option>Muscle Gain</option><option>Fitness</option></select></label><label>Diet<select value={form.diet_type} onChange={(e) => update("diet_type")(e.target.value)}><option>Vegetarian</option><option>Non-vegetarian</option><option>Vegan</option><option>Eggetarian</option></select></label><NumberField label="Daily budget (optional, Rs.)" value={form.budget} onChange={update("budget")} min="0" max="100000" /><label>Meals per day<select value={form.meals_per_day} onChange={(e) => update("meals_per_day")(e.target.value)}>{[2,3,4,5,6].map((n) => <option key={n}>{n}</option>)}</select></label><label className="span-all">Preferences / constraints<textarea value={form.extra_instructions} onChange={(e) => update("extra_instructions")(e.target.value)} placeholder="Foods you dislike, schedule constraints, allergies to discuss with a professional…" /></label><Notice notice={notice} /><FormButton busy={busy}>Generate meal plan</FormButton></form><PlanCard plan={plan} /></div><section className="history-section"><p className="label">SAVED PLANS</p>{data?.meal_plans?.length ? data.meal_plans.map((item) => <details className="saved-item" key={item.id}><summary><span>{item.goal} · {item.diet_type}</span><div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}><time>{dateTime(item.created_at)}</time><DeleteBtn onClick={() => deletePlan(item.id)} /></div></summary><PlanViewer text={item.plan_text} /></details>) : <p className="muted">Saved meal plans will appear here.</p>}</section></Page>;
}

// ─── Workout Planner ─────────────────────────────────
export function WorkoutPage() {
  const [form, setForm] = useState({ goal: "Fitness", level: "Beginner", location: "Home", duration_minutes: "30", rest_seconds: "30", weight_kg: "70" }); const [workout, setWorkout] = useState(null); const [notice, setNotice] = useState(null); const [busy, setBusy] = useState(false);
  const update = (key) => (value) => setForm({ ...form, [key]: value });
  async function generate(e) { e.preventDefault(); setBusy(true); try { const result = await request("/workouts/generate", { method: "POST", body: numbers(form, ["duration_minutes", "rest_seconds", "weight_kg"]) }); setWorkout(result.workout); setNotice({ type: "success", text: "Workout generated. Read the form cues before starting." }); } catch (err) { setNotice({ type: "error", text: err.message }); } finally { setBusy(false); } }
  async function complete() { if (!workout) return; setBusy(true); try { const calories = workout.exercises.reduce((total, item) => total + item.estimated_calories, 0); await request(`/workouts/${workout.id}/complete`, { method: "POST", body: { total_calories: calories } }); setNotice({ type: "success", text: "Workout saved as completed. Nice work showing up." }); } catch (err) { setNotice({ type: "error", text: err.message }); } finally { setBusy(false); } }
  return <Page><Header eyebrow="WORKOUT PLANNER" title="A session you can explain—and do." copy="Generated plans are conservative general fitness guidance. Stop for sharp pain, dizziness, chest pain, or unusual breathlessness." /><div className="two-column"><form className="panel form-grid" onSubmit={generate}><Select label="Goal" value={form.goal} onChange={update("goal")} options={["Fat Loss", "Muscle Gain", "Fitness"]} /><Select label="Experience" value={form.level} onChange={update("level")} options={["Beginner", "Intermediate", "Advanced"]} /><Select label="Location" value={form.location} onChange={update("location")} options={["Home", "Gym"]} /><NumberField label="Duration (minutes)" value={form.duration_minutes} onChange={update("duration_minutes")} min="15" max="120" /><NumberField label="Rest (seconds)" value={form.rest_seconds} onChange={update("rest_seconds")} min="10" max="120" /><NumberField label="Body weight (kg)" value={form.weight_kg} onChange={update("weight_kg")} min="20" max="400" step="0.1" /><Notice notice={notice} /><FormButton busy={busy}>Build workout</FormButton></form><section className="panel">{workout ? <><p className="label">YOUR SESSION</p><h2>{workout.goal} · {workout.duration_minutes} min</h2><ol className="workout-list">{workout.exercises.map((exercise) => <li key={exercise.name}><div><b>{exercise.name}</b><span>{exercise.sets} · {exercise.seconds}s · rest {exercise.rest_seconds}s</span><small>{exercise.form_cue}</small></div><a href={exercise.video_search} target="_blank" rel="noreferrer">Form guide ↗</a></li>)}</ol><button className="button primary" disabled={busy} onClick={complete}>Mark workout complete</button></> : <EmptyMessage text="Choose your preferences to build a structured session." />}</section></div></Page>;
}

// ─── Analytics (with charts + delete) ────────────────
export function AnalyticsPage() {
  const { data: workoutData, loading, error, reload: reloadWorkouts, setData: setWorkoutData } = useLoad("/workouts", "workouts");
  const { data: analyticsData, reload: reloadAnalytics } = useLoad("/analytics", "analytics");
  const workouts = workoutData?.workouts || []; const completed = workouts.filter((item) => item.completed_at);
  const totalMinutes = completed.reduce((sum, item) => sum + item.duration_minutes, 0);
  const totalCalories = completed.reduce((sum, item) => sum + item.total_calories, 0);

  async function deleteWorkout(id) { try { await request(`/workouts/${id}`, { method: "DELETE" }); setWorkoutData((d) => ({ ...d, workouts: d.workouts.filter((w) => w.id !== id) })); } catch {} }

  const bmiTrend = analyticsData?.bmi_trend || [];
  const calorieTrend = analyticsData?.calorie_trend || [];
  const workoutTrend = analyticsData?.workout_trend || [];
  const checkinTrend = analyticsData?.checkin_trend || [];

  const bmiChartData = {
    labels: bmiTrend.map((p) => shortDate(p.date)),
    datasets: [{ label: "BMI", data: bmiTrend.map((p) => p.bmi), borderColor: "#2F855A", backgroundColor: "rgba(47,133,90,0.1)", fill: true, tension: 0.4, pointRadius: 4, pointBackgroundColor: "#2F855A" }],
  };
  const calorieChartData = {
    labels: calorieTrend.map((p) => shortDate(p.date)),
    datasets: [{ label: "Calories", data: calorieTrend.map((p) => p.calories), backgroundColor: "rgba(217,119,6,0.7)", borderRadius: 6, borderSkipped: false }],
  };
  const sleepChartData = {
    labels: checkinTrend.map((p) => shortDate(p.checkin_date)),
    datasets: [
      { label: "Sleep (hrs)", data: checkinTrend.map((p) => p.sleep_hours), borderColor: "#6366F1", backgroundColor: "rgba(99,102,241,0.1)", fill: true, tension: 0.4, pointRadius: 3 },
      { label: "Mood", data: checkinTrend.map((p) => p.mood), borderColor: "#EC4899", backgroundColor: "transparent", tension: 0.4, pointRadius: 3, yAxisID: "y1" },
    ],
  };
  const sleepChartOpts = {
    ...chartDefaults,
    scales: {
      ...chartDefaults.scales,
      y: { ...chartDefaults.scales.y, title: { display: true, text: "Hours", font: chartFont } },
      y1: { position: "right", min: 0, max: 6, grid: { display: false }, ticks: { font: chartFont, color: "#EC4899" }, title: { display: true, text: "Mood", font: chartFont } },
    },
    plugins: { ...chartDefaults.plugins, legend: { display: true, labels: { font: chartFont, usePointStyle: true, padding: 16 } } },
  };

  return <Page><Header eyebrow="ANALYTICS" title="Progress is a history, not a mood." copy="Review your trends across workouts, nutrition, BMI, and daily check-ins." />
    {error && <div className="notice error">{error}<button onClick={reloadWorkouts}>Try again</button></div>}
    {loading ? <p className="loading">Loading analytics…</p> : <>
      <div className="stat-grid">
        <Metric label="Completed sessions" value={completed.length} /><Metric label="Minutes trained" value={totalMinutes} />
        <Metric label="Estimated kcal" value={Math.round(totalCalories)} /><Metric label="Plans generated" value={workouts.length} />
      </div>

      <div className="chart-grid">
        {bmiTrend.length > 1 && <section className="panel chart-card"><p className="label">BMI TREND</p><div className="chart-wrap"><Line data={bmiChartData} options={chartDefaults} /></div></section>}
        {calorieTrend.length > 0 && <section className="panel chart-card"><p className="label">DAILY CALORIES</p><div className="chart-wrap"><Bar data={calorieChartData} options={chartDefaults} /></div></section>}
        {checkinTrend.length > 1 && <section className="panel chart-card"><p className="label">SLEEP & MOOD</p><div className="chart-wrap"><Line data={sleepChartData} options={sleepChartOpts} /></div></section>}
        {workoutTrend.length > 0 && <section className="panel chart-card"><p className="label">WORKOUT ACTIVITY</p><div className="chart-wrap"><Bar data={{ labels: workoutTrend.map((p) => shortDate(p.date)), datasets: [{ label: "Minutes", data: workoutTrend.map((p) => p.minutes), backgroundColor: "rgba(99,102,241,0.7)", borderRadius: 6 }] }} options={chartDefaults} /></div></section>}
      </div>

      {!bmiTrend.length && !calorieTrend.length && !checkinTrend.length && <div className="panel" style={{ textAlign: "center", padding: "3rem" }}><p className="muted">Log a few BMI checks, food entries, or check-ins to see your charts appear here.</p></div>}

      <section className="panel" style={{ marginTop: "1.5rem" }}><p className="label">SESSION HISTORY</p>
        {workouts.length ? <div className="table-list">{workouts.map((item) => <article key={item.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div><b>{item.goal}</b><span>{item.level} · {item.location} · {item.duration_minutes} min</span></div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}><span>{item.completed_at ? "Completed" : "Planned"}</span><time>{dateTime(item.completed_at || item.created_at)}</time><DeleteBtn onClick={() => deleteWorkout(item.id)} /></div>
        </article>)}</div> : <EmptyMessage text="Finish a workout to see useful trends here." />}
      </section>
    </>}
  </Page>;
}

// ─── History (with delete) ───────────────────────────
export function HistoryPage() {
  const { data, loading, error, reload, setData } = useLoad("/records", "records");
  const [filter, setFilter] = useState("ALL");
  const records = (data?.records || []).filter((record) => filter === "ALL" || record.type === filter);

  async function deleteRecord(id) {
    try { await request(`/records/${id}`, { method: "DELETE" }); setData((d) => ({ ...d, records: d.records.filter((r) => r.id !== id) })); } catch {}
  }

  return <Page><Header eyebrow="HEALTH HISTORY" title="Your private record." copy="Records are visible only to the signed-in account in this local setup." /><div className="filter-row">{["ALL", "BMI", "FOOD", "SKIN"].map((type) => <button className={filter === type ? "selected" : ""} onClick={() => setFilter(type)} key={type}>{type === "ALL" ? "All activity" : type}</button>)}</div>{error && <div className="notice error">{error}<button onClick={reload}>Try again</button></div>}{loading ? <p className="loading">Loading your history…</p> : <div className="form-stack">{records.length ? records.map((record) => <HistoryItem record={record} onDelete={() => deleteRecord(record.id)} key={`${record.type}-${record.id}`} />) : <EmptyMessage text="No records match this view yet." />}</div>}</Page>;
}

// ─── Profile ─────────────────────────────────────────
export function ProfilePage() {
  const { data, loading, error, reload } = useLoad("/me", "me"); const [form, setForm] = useState(initialProfile); const [notice, setNotice] = useState(null); const [busy, setBusy] = useState(false);
  useEffect(() => { if (data?.profile) setForm({ ...initialProfile, ...Object.fromEntries(Object.entries(data.profile).filter(([key]) => key in initialProfile).map(([key, value]) => [key, value ?? ""])) }); }, [data]);
  const update = (key) => (value) => setForm({ ...form, [key]: value });
  async function submit(e) { e.preventDefault(); setBusy(true); try { await request("/profile", { method: "PUT", body: nullableNumbers(form, ["age", "height_cm", "weight_kg"]) }); setNotice({ type: "success", text: "Profile saved. Future planning and guidance can use these preferences." }); reload(); } catch (err) { setNotice({ type: "error", text: err.message }); } finally { setBusy(false); } }
  if (loading) return <Page><p className="loading">Loading profile…</p></Page>;
  return <Page><Header eyebrow="YOUR PROFILE" title={data?.user?.display_name || "Your profile"} copy="Only share what you're comfortable using for personal planning. You can update this at any time." />{error && <div className="notice error">{error}</div>}<form className="panel form-grid" onSubmit={submit}><NumberField label="Age" value={form.age} onChange={update("age")} min="13" max="120" /><Select label="Gender (optional)" value={form.gender} onChange={update("gender")} options={["", "Female", "Male", "Non-binary", "Prefer not to say"]} /><NumberField label="Height (cm)" value={form.height_cm} onChange={update("height_cm")} min="80" max="250" step="0.1" /><NumberField label="Weight (kg)" value={form.weight_kg} onChange={update("weight_kg")} min="20" max="400" step="0.1" /><Select label="Goal" value={form.goal} onChange={update("goal")} options={["Fat Loss", "Muscle Gain", "Fitness", "Better routine"]} /><Select label="Activity level" value={form.activity_level} onChange={update("activity_level")} options={["Low", "Light", "Moderate", "High"]} /><Select label="Diet preference" value={form.diet_preference} onChange={update("diet_preference")} options={["Vegetarian", "Non-vegetarian", "Vegan", "Eggetarian", "No preference"]} /><label className="span-all">About your routine<textarea value={form.bio} onChange={(e) => update("bio")(e.target.value)} placeholder="Schedule, preferences, or context you want to remember" /></label><Notice notice={notice} /><FormButton busy={busy}>Save profile</FormButton></form></Page>;
}

// ─── Chat ────────────────────────────────────────────
export function ChatPage() {
  const { data, loading, error, reload } = useLoad("/chat", "chat"); const [message, setMessage] = useState(""); const [notice, setNotice] = useState(null); const [busy, setBusy] = useState(false);
  async function submit(e) { e.preventDefault(); if (!message.trim()) return; setBusy(true); try { await request("/chat", { method: "POST", body: { message } }); setMessage(""); reload(); } catch (err) { setNotice({ type: "error", text: err.message }); } finally { setBusy(false); } }
  async function clear() { if (!window.confirm("Clear this chat history?")) return; await request("/chat", { method: "DELETE" }); reload(); }
  return <Page><Header eyebrow="AI WELLNESS ASSISTANT" title="Ask, then act on one thing." copy="This assistant gives general wellness information. It does not diagnose, prescribe, or replace professional care." /><section className="chat-panel">{error && <Notice notice={{ type: "error", text: error }} />}{loading ? <p className="loading">Loading conversation…</p> : <div className="messages">{data?.messages?.length ? data.messages.map((item) => <article className={`message ${item.role}`} key={item.id}><b>{item.role === "user" ? "You" : "Health.io"}</b><MarkdownMessage content={item.content} /></article>) : <EmptyMessage text="Ask about a small fitness, nutrition, or routine goal." />}</div>}<div className="panel" style={{ padding: "0.75rem 1rem", marginTop: "1rem", borderRadius: "20px" }}><form className="chat-form" style={{ margin: 0, padding: 0, border: "none" }} onSubmit={submit}><textarea value={message} maxLength="1500" onChange={(e) => setMessage(e.target.value)} placeholder="Ask a general wellness question…" /><FormButton busy={busy}>Send</FormButton><button type="button" className="button secondary" onClick={clear}>Clear chat</button></form></div><Notice notice={notice} /></section></Page>;
}

// ─── Shared Components ───────────────────────────────
function Header({ eyebrow, title, copy }) { return <header className="page-header"><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p>{copy}</p></header>; }
function MarkdownMessage({ content }) {
  if (!content) return null;
  
  const parseInline = (text) => {
    const parts = text.split(/(\*\*.*?\*\*|\*.*?\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) return <strong key={i}>{part.slice(2, -2)}</strong>;
      if (part.startsWith('*') && part.endsWith('*')) return <em key={i}>{part.slice(1, -1)}</em>;
      return part;
    });
  };

  const lines = content.split('\\n');
  const elements = [];
  let inList = false;
  let listItems = [];

  lines.forEach((line, i) => {
    const listMatch = line.match(/^(?:-|\\*)\s+(.*)/);
    if (listMatch) {
      inList = true;
      listItems.push(<li key={`li-${i}`}>{parseInline(listMatch[1])}</li>);
    } else {
      if (inList) {
        elements.push(<ul key={`ul-${i}`} className="chat-list">{listItems}</ul>);
        inList = false;
        listItems = [];
      }
      elements.push(<span key={`span-${i}`}>{parseInline(line)}<br/></span>);
    }
  });
  if (inList) elements.push(<ul key="ul-end" className="chat-list">{listItems}</ul>);

  return <div className="message-content">{elements}</div>;
}
function EmptyMessage({ text }) { return <p className="muted empty-message">{text}</p>; }
function Select({ label, value, onChange, options }) { return <label>{label}<select value={value} onChange={(e) => onChange(e.target.value)}>{options.map((option) => <option key={option} value={option}>{option || "Select"}</option>)}</select></label>; }
function Scale({ label, value, onChange, hint }) { return <label>{label}<select required value={value} onChange={(e) => onChange(e.target.value)}><option value="">Choose</option>{[1,2,3,4,5].map((n) => <option key={n}>{n}</option>)}</select><small>{hint}</small></label>; }
function Metric({ label, value }) { return <article className="metric-card"><p>{label}</p><strong>{value}</strong></article>; }
function PlanCard({ plan }) { return <section className="panel plan-card">{plan ? <><p className="label">YOUR SAVED PLAN</p><h2>{plan.goal} · {plan.diet_type}</h2><PlanViewer text={plan.plan_text} /></> : <EmptyMessage text="Your generated plan will stay here and be saved in your history." />}</section>; }
function PlanViewer({ text }) {
  const [currentMealIndex, setCurrentMealIndex] = useState(0);

  if (!text) return null;
  try {
    const data = JSON.parse(text);
    
    if (!data.meals || data.meals.length === 0) {
      throw new Error("No meals in JSON");
    }

    const currentMeal = data.meals[currentMealIndex] || data.meals[0];
    const handlePrev = () => setCurrentMealIndex(i => Math.max(0, i - 1));
    const handleNext = () => setCurrentMealIndex(i => Math.min(data.meals.length - 1, i + 1));
    
    const handleCopy = () => {
      let copyText = `Meal Plan: ${data.plan_title || 'Custom Plan'}\n`;
      if (data.daily_total_calories) copyText += `Daily Calories: ${data.daily_total_calories} kcal\n`;
      if (data.daily_total_protein_g) copyText += `Daily Protein: ${data.daily_total_protein_g}g\n\n`;
      
      data.meals.forEach(meal => {
        copyText += `--- ${meal.meal_type} ---\n`;
        copyText += `${meal.total_calories} kcal, ${meal.total_protein_g}g protein\n`;
        if (meal.items) {
          meal.items.forEach(item => {
            copyText += `• ${item.name} (${item.portion})\n`;
          });
        }
        copyText += `\n`;
      });
      navigator.clipboard.writeText(copyText.trim());
      alert("Plan copied to clipboard!");
    };

    return (
      <div className="plan-structured meal-carousel" style={{ marginTop: "1rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
          <h3 style={{ margin: 0, fontSize: "1.1rem", color: "var(--text-primary)" }}>{data.plan_title || "Your Meal Plan"}</h3>
          <button className="button secondary" onClick={handleCopy} type="button" style={{ padding: "0.25rem 0.75rem", fontSize: "0.85rem", minHeight: "32px" }}>Copy Plan</button>
        </div>
        
        <div className="carousel-card panel" style={{ padding: "1.5rem", borderRadius: "16px", minHeight: "250px", display: "flex", flexDirection: "column" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
            <h4 style={{ margin: 0, fontSize: "1.2rem", color: "var(--brand)" }}>{currentMeal.meal_type}</h4>
            <span style={{ fontSize: "0.9rem", color: "var(--text-secondary)", fontWeight: 500, background: "color-mix(in srgb, var(--surface) 60%, transparent)", padding: "4px 8px", borderRadius: "6px" }}>
              {currentMeal.total_calories} kcal · {currentMeal.total_protein_g}g protein
            </span>
          </div>
          
          <ul style={{ margin: 0, paddingLeft: "1.2rem", color: "var(--text-secondary)", fontSize: "1rem", flex: 1 }}>
            {currentMeal.items && currentMeal.items.map((item, j) => (
              <li key={j} style={{ marginBottom: "0.5rem" }}>
                <span style={{ color: "var(--text-primary)", fontWeight: 500 }}>{item.name}</span>
                <span style={{ opacity: 0.8, marginLeft: "0.25rem" }}>({item.portion})</span>
              </li>
            ))}
          </ul>

          <div className="carousel-controls" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "1.5rem", borderTop: "1px solid var(--border)", paddingTop: "1rem" }}>
            <button className="button secondary carousel-btn" type="button" onClick={handlePrev} disabled={currentMealIndex === 0} style={{ padding: "0.4rem 0.8rem", fontSize: "0.85rem", minHeight: "32px", opacity: currentMealIndex === 0 ? 0.4 : 1 }}>&larr; Prev</button>
            <span style={{ fontSize: "0.85rem", color: "var(--text-tertiary)" }}>Meal {currentMealIndex + 1} of {data.meals.length}</span>
            <button className="button secondary carousel-btn" type="button" onClick={handleNext} disabled={currentMealIndex === data.meals.length - 1} style={{ padding: "0.4rem 0.8rem", fontSize: "0.85rem", minHeight: "32px", opacity: currentMealIndex === data.meals.length - 1 ? 0.4 : 1 }}>Next &rarr;</button>
          </div>
        </div>
        
        {(data.daily_total_calories || data.daily_total_protein_g) && (
          <div style={{ marginTop: "1.5rem", display: "flex", gap: "2rem", justifyContent: "center", textAlign: "center", background: "color-mix(in srgb, var(--surface) 60%, transparent)", padding: "1rem", borderRadius: "12px", border: "1px solid var(--border)" }}>
            <div>
              <span style={{ fontSize: "0.75rem", color: "var(--text-tertiary)", fontWeight: 600, display: "block", marginBottom: "0.25rem" }}>DAILY CALORIES</span>
              <b style={{ fontSize: "1.2rem", color: "var(--text-primary)" }}>{data.daily_total_calories || "--"}</b>
            </div>
            <div>
              <span style={{ fontSize: "0.75rem", color: "var(--text-tertiary)", fontWeight: 600, display: "block", marginBottom: "0.25rem" }}>DAILY PROTEIN</span>
              <b style={{ fontSize: "1.2rem", color: "var(--text-primary)" }}>{data.daily_total_protein_g || "--"}g</b>
            </div>
          </div>
        )}
      </div>
    );
  } catch (e) {
    console.error("PlanViewer JSON parse or render error:", e);
    return <PlanText text={text} />;
  }
}
function PlanText({ text }) { return <div className="plan-text">{text.split("\n").map((line, index) => line.startsWith("## ") ? <h3 key={index}>{line.slice(3)}</h3> : line ? <p key={index}>{line.replace(/^- /, "• ")}</p> : <br key={index} />)}</div>; }
function HistoryItem({ record, onDelete }) {
  const title = record.type === "BMI" ? `BMI ${record.bmi} · ${record.category}` : record.type === "FOOD" ? record.food_name : record.concerns?.join(", ") || "Skin note";
  return <article className="panel history-item">
    <div style={{ flex: 1 }}>
      <h2 style={{margin: 0, fontSize: "1.2rem"}}>{title}</h2>
      <span style={{opacity: 0.8, display: "block", marginTop: "0.25rem"}}>{record.type === "FOOD" ? `${record.calories} kcal · ${record.protein_g}g protein` : record.summary || record.guidance || "Saved health record"}</span>
    </div>
    <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", flexShrink: 0 }}>
      <time style={{fontSize: "0.85rem", opacity: 0.7, whiteSpace: "nowrap"}}>{dateTime(record.created_at)}</time>
      {onDelete && <DeleteBtn onClick={onDelete} />}
    </div>
  </article>;
}
function numbers(form, fields) { const result = { ...form }; fields.forEach((field) => { result[field] = Number(result[field]); }); return result; }
function nullableNumbers(form, fields) { const result = { ...form }; fields.forEach((field) => { result[field] = result[field] === "" ? null : Number(result[field]); }); return result; }
