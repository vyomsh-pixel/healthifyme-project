import { useState, useEffect } from "react";

export default function HealthScoreMark({ score = 0 }) {
  const pct = Math.max(0, Math.min(100, score));
  
  // Count up animation for the number
  const [displayScore, setDisplayScore] = useState(0);
  useEffect(() => {
    let start = null;
    const duration = 1500;
    const step = (timestamp) => {
      if (!start) start = timestamp;
      const progress = Math.min((timestamp - start) / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 4);
      setDisplayScore(Math.floor(ease * pct));
      if (progress < 1) {
        window.requestAnimationFrame(step);
      } else {
        setDisplayScore(pct);
      }
    };
    window.requestAnimationFrame(step);
  }, [pct]);

  let strokeColor = "var(--status-red)";
  let label = "Needs attention";
  if (pct >= 80) {
    strokeColor = "var(--status-green)";
    label = "Excellent";
  } else if (pct >= 50) {
    strokeColor = "var(--status-amber)";
    label = "Good progress";
  }

  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  // Calculate dash offset based on animation
  const dashoffset = circumference - (displayScore / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="relative flex items-center justify-center" style={{ width: 140, height: 140 }}>
        {/* Background Track */}
        <svg className="absolute top-0 left-0" width="140" height="140">
          <circle 
            cx="70" cy="70" r={radius} 
            fill="none" 
            stroke="var(--surface-raised)" 
            strokeWidth="12" 
          />
        </svg>
        {/* Animated Progress Ring */}
        <svg className="absolute top-0 left-0 transform -rotate-90" width="140" height="140">
          <circle 
            cx="70" cy="70" r={radius} 
            fill="none" 
            stroke={strokeColor} 
            strokeWidth="12" 
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={dashoffset}
            style={{ transition: "stroke-dashoffset 0.1s linear" }}
          />
        </svg>
        {/* Score Text */}
        <div className="flex flex-col items-center z-10">
          <span 
            className="text-4xl font-bold tracking-tighter" 
            style={{ color: strokeColor }}
          >
            {displayScore}
          </span>
          <span className="text-[10px] uppercase font-bold text-[var(--text-tertiary)] tracking-widest mt-1">
            / 100
          </span>
        </div>
      </div>
      <p className="text-xs font-semibold tracking-wide text-[var(--text-secondary)] mt-4 uppercase">
        {label}
      </p>
    </div>
  );
}