import React from "react";

// loading: skeleton with title bar + content lines.
export default function SummaryCard({ title, children, loading = false }) {
  return (
    <div className="rounded-xl border border-border bg-card/40 p-4">
      {loading ? (
        <>
          <div className="h-4 w-1/3 animate-pulse rounded bg-muted" />
          <div className="mt-4 space-y-2">
            <div className="h-3 w-full animate-pulse rounded bg-muted" />
            <div className="h-3 w-[90%] animate-pulse rounded bg-muted" />
            <div className="h-3 w-[75%] animate-pulse rounded bg-muted" />
          </div>
        </>
      ) : (
        <>
          <h3 className="text-[14px] font-semibold tracking-tight text-foreground">{title}</h3>
          <div className="mt-3 text-[13px] leading-relaxed text-foreground/85">{children}</div>
        </>
      )}
    </div>
  );
}