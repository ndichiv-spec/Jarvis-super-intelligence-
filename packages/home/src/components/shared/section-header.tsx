"use client";

import { cn } from "@/lib/utils";
import { ChevronRight } from "lucide-react";
import Link from "next/link";

interface SectionHeaderProps {
  title: string;
  description?: string;
  action?: { label: string; href: string };
  className?: string;
}

export function SectionHeader({ title, description, action, className }: SectionHeaderProps) {
  return (
    <div className={cn("flex items-center justify-between", className)}>
      <div>
        <h2 className="text-lg font-semibold">{title}</h2>
        {description && <p className="text-sm text-muted-foreground">{description}</p>}
      </div>
      {action && (
        <Link
          href={action.href}
          className="flex items-center gap-1 text-sm text-primary hover:underline"
        >
          {action.label}
          <ChevronRight className="h-3 w-3" />
        </Link>
      )}
    </div>
  );
}
