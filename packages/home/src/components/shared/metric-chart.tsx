"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface DataPoint {
  label: string;
  value: number;
}

interface MetricChartProps {
  title: string;
  data: DataPoint[];
  className?: string;
  height?: number;
  color?: string;
}

export function MetricChart({ title, data, className, height = 120, color = "hsl(var(--primary))" }: MetricChartProps) {
  const max = Math.max(...data.map((d) => d.value), 1);

  return (
    <Card className={cn("", className)}>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-end gap-1" style={{ height }}>
          {data.map((point, i) => (
            <div
              key={i}
              className="flex-1 flex flex-col items-center gap-1"
            >
              <div
                className="w-full rounded-t transition-all duration-500 ease-out hover:opacity-80"
                style={{
                  height: `${(point.value / max) * 100}%`,
                  backgroundColor: color,
                  minHeight: point.value > 0 ? 4 : 0,
                }}
              />
            </div>
          ))}
        </div>
        {data.length > 0 && (
          <div className="flex gap-1 mt-2">
            {data.filter((_, i) => data.length > 12 ? i % Math.ceil(data.length / 6) === 0 || i === data.length - 1 : true).map((point, i) => (
              <span key={i} className="flex-1 text-[10px] text-muted-foreground text-center truncate">
                {point.label}
              </span>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
