"use client";

import { useTheme } from "@/lib/theme-context";

interface GaugeChartProps {
  value: number;
  label: string;
  size?: number;
  strokeWidth?: number;
}

export function GaugeChart({ value, label, size = 120, strokeWidth = 10 }: GaugeChartProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (Math.min(value, 100) / 100) * circumference;

  const color =
    value >= 80 ? "#22c55e" : value >= 60 ? "#f59e0b" : value >= 40 ? "#f97316" : "#ef4444";

  return (
    <div className="flex flex-col items-center" style={{ width: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="currentColor" strokeWidth={strokeWidth} className="text-border" />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <span className="text-3xl font-bold -mt-[calc(theme(spacing.14))]" style={{ color }}>
        {Math.round(value)}
      </span>
      <span className="text-xs text-muted-foreground mt-1 text-center">{label}</span>
    </div>
  );
}
