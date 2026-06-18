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
} from "recharts";
import { useTheme } from "@/lib/theme-context";
import { getModelDisplayName } from "@/lib/utils";

interface DriftChartProps {
  data: Record<string, number>;
  height?: number;
}

const MODEL_COLORS = ["#8b5cf6", "#10b981", "#f59e0b", "#3b82f6", "#ef4444"];

export function DriftChart({ data, height = 280 }: DriftChartProps) {
  const { theme } = useTheme();
  const chartData = Object.entries(data).map(([key, value], i) => ({
    name: getModelDisplayName(key),
    drift: value,
    fill: MODEL_COLORS[i % MODEL_COLORS.length],
  }));

  if (chartData.length === 0) return null;

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={chartData} layout="vertical" margin={{ left: 80, right: 20, top: 10, bottom: 10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={theme === "dark" ? "#374151" : "#e5e7eb"} />
        <XAxis
          type="number"
          domain={[0, 1]}
          tick={{ fontSize: 12, fill: theme === "dark" ? "#9ca3af" : "#6b7280" }}
          tickFormatter={(v) => v.toFixed(2)}
        />
        <YAxis
          type="category"
          dataKey="name"
          tick={{ fontSize: 13, fill: theme === "dark" ? "#d1d5db" : "#374151" }}
          width={80}
        />
        <Tooltip
          formatter={(val) => [Number(val).toFixed(4), "Opinion Drift"]}
          contentStyle={{
            backgroundColor: theme === "dark" ? "#1f2937" : "#fff",
            border: `1px solid ${theme === "dark" ? "#374151" : "#e5e7eb"}`,
            borderRadius: "8px",
            color: theme === "dark" ? "#f3f4f6" : "#111827",
            fontSize: "13px",
          }}
        />
        <Bar dataKey="drift" radius={[0, 4, 4, 0]} maxBarSize={24}>
          {chartData.map((entry, i) => (
            <Cell key={i} fill={entry.fill} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
