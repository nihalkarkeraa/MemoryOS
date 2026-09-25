import React from "react";
import { FileText } from "lucide-react";
import { cn } from "@/lib/utils";

// Highlights occurrences of each search term within text.
function highlight(text, query) {
  if (!query) return text;

  const terms = query
    .split(/\s+/)
    .map((t) => t.trim())
    .filter((t) => t.length > 1);

  if (terms.length === 0) return text;

  const escaped = terms.map((t) =>
    t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
  );

  const re = new RegExp(
    `(${escaped.join("|")})`,
    "gi"
  );

  const parts = text.split(re);

  return parts.map((part, i) =>
    re.test(part) ? (
      <mark
        key={i}
        className="rounded bg-primary/20 px-0.5 text-primary-foreground"
      >
        {part}
      </mark>
    ) : (
      <React.Fragment key={i}>
        {part}
      </React.Fragment>
    )
  );
}

// result:
// {
//   id,
//   name,
//   page,
//   excerpt,
//   hybridScore,
//   rerankerScore,
//   matchPercent
// }
export default function SearchResultCard({
  result,
  query,
}) {
  const score =
    result.matchPercent ??
    (result.rerankerScore != null
      ? Math.round(result.rerankerScore * 100)
      : result.hybridScore != null
        ? Math.round(result.hybridScore * 100)
        : 0);

  const scorePct = Math.max(
    0,
    Math.min(100, score)
  );

  const level =
    scorePct >= 80
      ? "high"
      : scorePct >= 50
        ? "medium"
        : "low";

  const levelColor = {
    high: "bg-emerald-500",
    medium: "bg-amber-500",
    low: "bg-rose-500",
  }[level];

  const fmt = (n) =>
    typeof n === "number"
      ? Number.isInteger(n)
        ? n.toFixed(2)
        : n.toFixed(4)
      : null;

  return (
    <div className="group rounded-xl border border-border bg-card/40 p-4 transition-colors hover:border-primary/30 hover:bg-card">
      <div className="flex items-start gap-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-border bg-muted/40">
          <FileText className="h-4 w-4 text-primary" />
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span
              className="truncate text-[14px] font-medium text-foreground"
              title={result.name}
            >
              {result.name}
            </span>

            <span className="shrink-0 rounded-md border border-border bg-muted/40 px-1.5 py-0.5 text-[10.5px] font-medium text-muted-foreground">
              Page {result.page}
            </span>
          </div>

          <p className="mt-2 text-[13px] leading-relaxed text-muted-foreground">
            {highlight(result.excerpt, query)}
          </p>
        </div>

        {/* Relevance indicator */}
        <div className="flex shrink-0 flex-col items-end gap-1">
          <span className="text-[11px] font-medium text-muted-foreground">
            {scorePct}% match
          </span>

          <div className="h-1.5 w-16 overflow-hidden rounded-full bg-muted">
            <div
              className={cn(
                "h-full rounded-full transition-all",
                levelColor
              )}
              style={{
                width: `${Math.max(scorePct, 8)}%`,
              }}
            />
          </div>

          {(result.hybridScore != null ||
            result.rerankerScore != null) && (
            <div className="mt-0.5 flex flex-col items-end gap-0.5 text-[10px] text-muted-foreground/70">
              {result.hybridScore != null && (
                <span>
                  Hybrid {fmt(result.hybridScore)}
                </span>
              )}

              {result.rerankerScore != null && (
                <span>
                  Reranker {fmt(result.rerankerScore)}
                </span>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}