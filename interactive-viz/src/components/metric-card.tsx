"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  label: string;
  value: string;
  deviation?: number;
  unit?: string;
  className?: string;
  animate?: boolean;
}

export function MetricCard({
  label,
  value,
  deviation,
  unit,
  className,
  animate = true,
}: MetricCardProps) {
  const statusColor =
    deviation === undefined
      ? "text-teal-400"
      : Math.abs(deviation) < 0.01
      ? "text-emerald-400"
      : Math.abs(deviation) < 0.1
      ? "text-amber-400"
      : "text-red-400";

  const badgeVariant =
    deviation === undefined
      ? "default"
      : Math.abs(deviation) < 0.01
      ? ("success" as const)
      : Math.abs(deviation) < 0.1
      ? ("warning" as const)
      : ("destructive" as const);

  return (
    <Card className={cn("transition-all duration-300 hover:border-teal-500/50", className)}>
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">
            {label}
          </p>
          {deviation !== undefined && (
            <Badge variant={badgeVariant}>
              ε = {Math.abs(deviation).toExponential(2)}
            </Badge>
          )}
        </div>
        <p
          className={cn(
            "mt-2 text-2xl font-bold font-mono transition-all duration-500",
            statusColor,
            animate && "tabular-nums"
          )}
        >
          {value}
          {unit && (
            <span className="ml-1 text-sm font-normal text-gray-500">{unit}</span>
          )}
        </p>
      </CardContent>
    </Card>
  );
}
