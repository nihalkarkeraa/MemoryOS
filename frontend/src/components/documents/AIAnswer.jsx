import React from "react";
import { Sparkles, BookOpen } from "lucide-react";
import SourceCard from "./SourceCard";

// loading: show skeleton answer + sources.
export default function AIAnswer({ answer, sources = [], loading = false }) {
  return (
    <div className="rounded-xl border border-border bg-card/40 p-4">
      <div className="flex items-center gap-2">
        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/10">
          <Sparkles className="h-3.5 w-3.5 text-primary" />
        </div>
        <h3 className="text-[13.5px] font-semibold tracking-tight text-foreground">AI Answer</h3>
      </div>

      <div className="mt-3.5">
        {loading ? (
          <div className="space-y-2">
            <div className="h-3 w-full animate-pulse rounded bg-muted" />
            <div className="h-3 w-[92%] animate-pulse rounded bg-muted" />
            <div className="h-3 w-[78%] animate-pulse rounded bg-muted" />
            <div className="h-3 w-[60%] animate-pulse rounded bg-muted" />
          </div>
        ) : (
          <p className="text-[13.5px] leading-relaxed text-foreground/90">{answer}</p>
        )}
      </div>

      <div className="mt-5 border-t border-border pt-4">
        <div className="mb-2.5 flex items-center gap-1.5">
          <BookOpen className="h-3.5 w-3.5 text-muted-foreground" />
          <span className="text-[12px] font-medium text-muted-foreground">Sources</span>
        </div>
        <div className="space-y-2.5">
          {loading
            ? Array.from({ length: 2 }).map((_, i) => (
                <div
                  key={i}
                  className="h-[68px] w-full animate-pulse rounded-lg border border-border bg-muted/40"
                />
              ))
            : sources.map((s, i) => <SourceCard key={i} source={s} />)}
        </div>
      </div>
    </div>
  );
}