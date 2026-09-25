import React from "react";

// Skeleton placeholder cards shown while a search is loading.
export default function SearchResultsSkeleton({ count = 4 }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="rounded-xl border border-border bg-card/40 p-4"
        >
          <div className="flex items-start gap-3">
            <div className="h-9 w-9 shrink-0 animate-pulse rounded-lg bg-muted" />
            <div className="flex-1 space-y-2">
              <div className="h-4 w-2/5 animate-pulse rounded bg-muted" />
              <div className="h-3 w-full animate-pulse rounded bg-muted" />
              <div className="h-3 w-4/5 animate-pulse rounded bg-muted" />
            </div>
            <div className="h-3 w-16 animate-pulse rounded bg-muted" />
          </div>
        </div>
      ))}
    </div>
  );
}