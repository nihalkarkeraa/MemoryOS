import React from "react";
import { ArrowLeft } from "lucide-react";

// Full-page skeleton for document loading.
export default function DocumentDetailSkeleton() {
  return (
    <div className="mx-auto w-full max-w-6xl px-5 py-8 sm:px-8 sm:py-10">
      <div className="flex items-center gap-2 text-muted-foreground">
        <ArrowLeft className="h-4 w-4 animate-pulse" />
        <div className="h-3 w-20 animate-pulse rounded bg-muted" />
      </div>
      <div className="mt-5 h-7 w-1/2 animate-pulse rounded bg-muted" />
      <div className="mt-2 h-3 w-1/3 animate-pulse rounded bg-muted" />
      <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-[340px_1fr]">
        <div className="h-64 w-full animate-pulse rounded-xl border border-border bg-muted/30" />
        <div className="h-80 w-full animate-pulse rounded-xl border border-border bg-muted/30" />
      </div>
    </div>
  );
}