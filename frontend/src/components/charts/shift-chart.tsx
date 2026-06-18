"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from "recharts";
import { useTheme } from "@/lib/theme-context";
import { getModelDisplayName } from "@/lib/utils";

interface ShiftChartProps {
  data: Record<string, number>;
  height?: number;
}

export function ShiftChart({ data, height = 280 }: ShiftChartProps) {
  const { theme } = useTheme();
  const chartData = Object.entries(data).map(([key, value]) => ({
    name: getModelDisplayName(key),
    shift: value,
    color: value >= 0 ? "#22c55e" : "#ef4444",
  }));

  if (chartData.length === 0) return null;

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={chartData} layout="vertical" margin={{ left: 80, right: 20, top: 10, bottom: 10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={theme === "dark" ? "#374151" : "#e5e7eb"} />
        <XAxis
          type="number"
          tick={{ fontSize: 12, fill: theme === "dark" ? "#9ca3af" : "#6b7280" }}
        />
        <YAxis
          type="category"
          dataKey="name"
          tick={{ fontSize: 13, fill: theme === "dark" ? "#d1d5db" : "#374151" }}
          width={80}
        />
        <ReferenceLine x={0} stroke={theme === "dark" ? "#6b7280" : "#9ca3af"} />
        <Tooltip
          formatter={(val) => { const n = Number(val); return [`${n >= 0 ? "+" : ""}${n.toFixed(1)}`, "Confidence Shift"]; }}
          contentStyle={{
            backgroundColor: theme === "dark" ? "#1f2937" : "#fff",
            border: `1px solid ${theme === "dark" ? "#374151" : "#e5e7eb"}`,
            borderRadius: "8px",
            color: theme === "dark" ? "#f3f4f6" : "#111827",
            fontSize: "13px",
          }}
        />
        <Bar dataKey="shift" radius={[0, 4, 4, 0]} maxBarSize={24}>
          {chartData.map((entry, i) => (
            <Cell key={i} fill={entry.color} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
