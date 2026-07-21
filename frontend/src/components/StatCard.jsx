import { useState, useEffect } from "react";

export default function StatCard({ label, value, unit, accent = false }) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    let start = null;
    const duration = 1200;
    const end = parseFloat(value) || 0;
    if (end === 0) {
      setDisplayValue(0);
      return;
    }
    const step = (timestamp) => {
      if (!start) start = timestamp;
      const progress = Math.min((timestamp - start) / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 4);
      setDisplayValue(Math.floor(ease * end));
      if (progress < 1) {
        window.requestAnimationFrame(step);
      } else {
        setDisplayValue(end);
      }
    };
    window.requestAnimationFrame(step);
  }, [value]);

  // Determine colored glass background based on label
  let bgGradient = "linear-gradient(135deg, rgba(255, 255, 255, 0.25) 0%, rgba(255, 255, 255, 0.05) 100%)";
  let icon = null;
  const l = label.toLowerCase();
  
  if (l.includes("bmi")) { 
    // Amber glass
    bgGradient = "linear-gradient(135deg, rgba(217, 119, 6, 0.25) 0%, rgba(217, 119, 6, 0.05) 100%)"; 
    icon = "📏"; 
  }
  else if (l.includes("food")) { 
    // Green glass
    bgGradient = "linear-gradient(135deg, rgba(47, 133, 90, 0.25) 0%, rgba(47, 133, 90, 0.05) 100%)"; 
    icon = "🥗"; 
  }
  else if (l.includes("workout")) { 
    // Red glass
    bgGradient = "linear-gradient(135deg, rgba(192, 82, 74, 0.25) 0%, rgba(192, 82, 74, 0.05) 100%)"; 
    icon = "💪"; 
  }
  else if (l.includes("meal")) { 
    // Blue glass instead of black
    bgGradient = "linear-gradient(135deg, rgba(59, 130, 246, 0.25) 0%, rgba(59, 130, 246, 0.05) 100%)"; 
    icon = "🍽️"; 
  }

  return (
    <div 
      className="rounded-2xl px-5 py-4 relative overflow-hidden"
      style={{ 
        background: bgGradient,
        backdropFilter: "blur(24px) saturate(150%)",
        WebkitBackdropFilter: "blur(24px) saturate(150%)",
        border: "1px solid rgba(255, 255, 255, 0.3)",
        borderTopColor: "rgba(255, 255, 255, 0.6)",
        borderLeftColor: "rgba(255, 255, 255, 0.6)",
        boxShadow: "0 8px 32px rgba(0, 0, 0, 0.05), inset 0 2px 4px rgba(255, 255, 255, 0.2)"
      }}
    >
      <p className="font-mono text-[10.5px] uppercase tracking-wider text-[var(--text-tertiary)] mb-2 flex items-center gap-2">
        <span>{icon}</span> {label}
      </p>
      <div className="flex items-baseline gap-1.5">
        <span
          className={`font-display text-3xl font-semibold text-[var(--text-primary)]`}
        >
          {displayValue}
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