import React from "react";
import { FileText } from "lucide-react";
import { cn } from "@/lib/utils";

// Displays a single cited source: filename, page number, and a relevant excerpt.
export default function SourceCard({ source }) {
  return (
    <div className="rounded-lg border border-border bg-card/60 p-3 transition-colors hover:border-primary/30 hover:bg-card">
      <div className="flex items-center gap-2">
        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md border border-border bg-muted/40">
          <FileText className="h-3.5 w-3.5 text-primary" />
        </div>
        <span className="truncate text-[12.5px] font-medium text-foreground" title={source.name}>
          {source.name}
        </span>
        <span className="ml-auto shrink-0 rounded-md border border-border bg-muted/40 px-1.5 py-0.5 text-[10.5px] font-medium text-muted-foreground">
          Page {source.page}
        </span>
      </div>
      <blockquote
        className={cn(
          "mt-2.5 border-l-2 border-primary/40 pl-3 text-[12.5px] italic leading-relaxed text-muted-foreground"
        )}
      >
        “{source.excerpt}”
      </blockquote>
    </div>
  );
}