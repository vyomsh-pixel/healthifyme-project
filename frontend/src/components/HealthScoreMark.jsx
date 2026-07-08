export default function HealthScoreMark({ score = 0 }) {
  const pct = Math.max(0, Math.min(100, score));

  let strokeColor = "var(--danger)";
  let label = "Needs attention";
  if (pct >= 80) {
    strokeColor = "var(--success)";
    label = "Excellent";
  } else if (pct >= 50) {
    strokeColor = "var(--warning)";
    label = "Good progress";
  }

  const underlineWidth = 40 + (pct / 100) * 160;

  return (
    <div className="flex flex-col items-start">
      <div className="flex items-baseline gap-2">
        <span
          className="font-display text-[88px] leading-none font-semibold tracking-tight"
          style={{ color: strokeColor }}
        >
          {pct}
        </span>
        <span className="font-mono text-sm text-[var(--text-tertiary)] mb-2">
          / 100
        </span>
      </div>

      <svg
        width={Math.max(underlineWidth, 60)}
        height="14"
        viewBox={`0 0 ${Math.max(underlineWidth, 60)} 14`}
        className="-mt-1"
      >
        <path
          d={`M2 8 Q ${underlineWidth / 4} 2, ${underlineWidth / 2} 7 T ${underlineWidth - 2} 6`}
          fill="none"
          stroke={strokeColor}
          strokeWidth="3.5"
          strokeLinecap="round"
        />
      </svg>

      <p className="font-mono text-[11px] tracking-wide text-[var(--text-tertiary)] mt-2 uppercase">
        {label}
      </p>
    </div>
  );
}