import React from "react";
import { FileText } from "lucide-react";
import { cn } from "@/lib/utils";

// Displays a cited source using the metadata currently
// provided by the MemoryOS backend.
export default function SourceCard({ source }) {
  const hasChunk = Boolean(source?.chunkId);
  const hasScore =
    typeof source?.hybridScore === "number" &&
    Number.isFinite(source.hybridScore);

  return (
    <div className="rounded-lg border border-border bg-card/60 p-3 transition-colors hover:border-primary/30 hover:bg-card">
      <div className="flex items-center gap-2">
        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md border border-border bg-muted/40">
          <FileText className="h-3.5 w-3.5 text-primary" />
        </div>

        <span
          className="truncate text-[12.5px] font-medium text-foreground"
          title={source?.name || "Document source"}
        >
          {source?.name || "Document source"}
        </span>

        {source?.page != null && (
          <span className="ml-auto shrink-0 rounded-md border border-border bg-muted/40 px-1.5 py-0.5 text-[10.5px] font-medium text-muted-foreground">
            Page {source.page}
          </span>
        )}
      </div>

      <div
        className={cn(
          "mt-2.5 flex flex-wrap items-center gap-x-3 gap-y-1.5",
          "border-l-2 border-primary/40 pl-3"
        )}
      >
        {hasChunk && (
          <span className="text-[11.5px] text-muted-foreground">
            Chunk{" "}
            <span
              className="font-medium text-foreground/80"
              title={source.chunkId}
            >
              {source.chunkId}
            </span>
          </span>
        )}

        {hasScore && (
          <span className="text-[11.5px] text-muted-foreground">
            Relevance{" "}
            <span className="font-medium text-foreground/80">
              {source.hybridScore.toFixed(3)}
            </span>
          </span>
        )}

        {!hasChunk && !hasScore && (
          <span className="text-[11.5px] text-muted-foreground">
            Source metadata
          </span>
        )}
      </div>
    </div>
  );
}