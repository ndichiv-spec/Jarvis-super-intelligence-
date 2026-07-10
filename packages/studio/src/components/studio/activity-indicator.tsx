"use client";

import { cn } from "@/lib/utils";
import { useEffect, useState } from "react";

export function ActivityIndicator() {
  const [active, setActive] = useState(true);

  useEffect(() => {
    const interval = setInterval(() => {
      setActive((prev) => !prev);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <span className="flex items-center gap-1.5 text-[10px] text-muted-foreground">
      <span className="relative flex h-2 w-2">
        <span
          className={cn(
            "absolute inline-flex h-full w-full rounded-full bg-green-400",
            active && "animate-ping opacity-75",
            !active && "opacity-0",
          )}
        />
        <span className="relative inline-flex h-2 w-2 rounded-full bg-green-500" />
      </span>
      System Online
    </span>
  );
}
