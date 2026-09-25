import React from "react";

// Skeleton shown while comparison is running ("Analyzing documents...").
export default function ComparisonSkeleton() {
  const Card = () => (
    <div className="rounded-xl border border-border bg-card/40 p-4">
      <div className="flex items-center gap-2">
        <div className="h-7 w-7 animate-pulse rounded-lg bg-muted" />
        <div className="h-4 w-1/3 animate-pulse rounded bg-muted" />
      </div>
      <div className="mt-3 space-y-2">
        <div className="h-3 w-full animate-pulse rounded bg-muted" />
        <div className="h-3 w-4/5 animate-pulse rounded bg-muted" />
      </div>
    </div>
  );
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <Card />
        <Card />
      </div>
      <Card />
      <Card />
      <Card />
      <div className="space-y-2.5">
        <div className="h-3 w-16 animate-pulse rounded bg-muted" />
        <div className="h-[68px] w-full animate-pulse rounded-lg border border-border bg-muted/40" />
        <div className="h-[68px] w-full animate-pulse rounded-lg border border-border bg-muted/40" />
      </div>
    </div>
  );
}