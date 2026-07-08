export default function StatCard({ label, value, unit, accent = false }) {
  return (
    <div className="bg-[var(--surface)] border border-[var(--border)] rounded-2xl px-5 py-4">
      <p className="font-mono text-[10.5px] uppercase tracking-wider text-[var(--text-tertiary)] mb-2">
        {label}
      </p>
      <div className="flex items-baseline gap-1.5">
        <span
          className={`font-display text-3xl font-semibold ${
            accent ? "text-[var(--accent)]" : "text-[var(--text-primary)]"
          }`}
        >
          {value}
        </span>
        {unit && (
          <span className="font-mono text-xs text-[var(--text-tertiary)]">
            {unit}
          </span>
        )}
      </div>
    </div>
  );
}