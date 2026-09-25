import React from "react";
import { Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

const suggestions = [
  { icon: Sparkles, label: "Explain database indexing" },
  { icon: Sparkles, label: "Summarize my documents" },
  { icon: Sparkles, label: "Compare these documents" },
  { icon: Sparkles, label: "What are the key concepts?" },
];

export default function SuggestionChips({ onPick }) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      {suggestions.map((s) => {
        const Icon = s.icon;
        return (
          <button
            key={s.label}
            onClick={() => onPick?.(s.label)}
            className={cn(
              "group inline-flex items-center gap-1.5 rounded-full border border-border bg-card/60 px-3.5 py-2",
              "text-[13px] font-medium text-muted-foreground transition-all duration-200",
              "hover:border-primary/40 hover:bg-accent/40 hover:text-foreground"
            )}
          >
            <Icon className="h-3.5 w-3.5 text-primary/70 transition-colors group-hover:text-primary" />
            {s.label}
          </button>
        );
      })}
    </div>
  );
}