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
        <h3 className="text-sm font-medium">{title}</h3>
        {description && <p className="text-xs text-muted-foreground mt-0.5">{description}</p>}
      </div>
      {action && (
        <Link href={action.href} className="flex items-center gap-0.5 text-xs text-primary hover:underline">
          {action.label} <ChevronRight className="h-3 w-3" />
        </Link>
      )}
    </div>
  );
}
