"use client";

import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  AreaChart,
  Area,
  BarChart,
  Bar,
} from "recharts";
import { useMemo } from "react";

interface LiveChartProps {
  data: Record<string, unknown>[];
  xKey: string;
  lines: { key: string; color: string; name: string }[];
  title?: string;
  type?: "line" | "area" | "bar";
  height?: number;
}

export function LiveChart({
  data,
  xKey,
  lines,
  title,
  type = "line",
  height = 300,
}: LiveChartProps) {
  // Use data directly with memoized reference for animation
  const chartData = useMemo(() => data, [data]);

  const ChartComponent = type === "area" ? AreaChart : type === "bar" ? BarChart : LineChart;

  return (
    <div className="w-full">
      {title && (
        <h3 className="text-sm font-medium text-gray-300 mb-2">{title}</h3>
      )}
      <div style={{ height }} className="transition-opacity duration-300">
        <ResponsiveContainer width="100%" height="100%">
          <ChartComponent data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1c2740" />
            <XAxis
              dataKey={xKey}
              tick={{ fill: "#9ca3af", fontSize: 11 }}
              stroke="#1c2740"
            />
            <YAxis
              tick={{ fill: "#9ca3af", fontSize: 11 }}
              stroke="#1c2740"
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#0f1525",
                border: "1px solid #1c2740",
                borderRadius: "6px",
                color: "#e5e7eb",
                fontSize: "12px",
              }}
            />
            <Legend
              wrapperStyle={{ fontSize: "11px", color: "#9ca3af" }}
            />
            {lines.map(({ key, color, name }) => {
              if (type === "area") {
                return (
                  <Area
                    key={key}
                    type="monotone"
                    dataKey={key}
                    stroke={color}
                    fill={color}
                    fillOpacity={0.15}
                    name={name}
                    strokeWidth={2}
                    animationDuration={300}
                  />
                );
              }
              if (type === "bar") {
                return (
                  <Bar
                    key={key}
                    dataKey={key}
                    fill={color}
                    name={name}
                    animationDuration={300}
                  />
                );
              }
              return (
                <Line
                  key={key}
                  type="monotone"
                  dataKey={key}
                  stroke={color}
                  name={name}
                  strokeWidth={2}
                  dot={false}
                  animationDuration={300}
                />
              );
            })}
          </ChartComponent>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
