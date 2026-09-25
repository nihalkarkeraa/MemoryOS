import React from "react";
import { FileText, MoreHorizontal, CheckCircle2, Loader2 } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";

const statusStyles = {
  Ready: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
  Processing: "text-amber-400 bg-amber-500/10 border-amber-500/20",
};

export default function DocumentCard({ doc, onOpen, onSummarize, onDelete }) {
  const isProcessing = doc.status === "Processing";
  return (
    <div className="group flex flex-col rounded-xl border border-border bg-card p-4 transition-all duration-200 hover:border-border/80 hover:bg-card/80 hover:shadow-lg hover:shadow-black/20">
      <div className="flex items-start justify-between">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-border bg-muted/40">
          <FileText className="h-5 w-5 text-primary" />
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="rounded-md p-1 text-muted-foreground/60 transition-colors hover:bg-muted hover:text-foreground">
              <MoreHorizontal className="h-4 w-4" />
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-40">
            <DropdownMenuItem onClick={() => onOpen?.(doc)}>Open</DropdownMenuItem>
            <DropdownMenuItem onClick={() => onSummarize?.(doc)}>Summarize</DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => onDelete?.(doc)}
              className="text-destructive focus:text-destructive"
            >
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
      <p className="mt-3 truncate text-[13.5px] font-medium text-foreground" title={doc.name}>
        {doc.name}
      </p>
      <div className="mt-1 flex items-center gap-2 text-[11.5px] text-muted-foreground">
        <span>{doc.pages} pages</span>
        <span className="text-muted-foreground/40">·</span>
        <span>{doc.date}</span>
      </div>
      <div className="mt-3.5 flex items-center justify-between border-t border-border/70 pt-3">
        <span
          className={cn(
            "inline-flex items-center gap-1 rounded-md border px-2 py-0.5 text-[11px] font-medium",
            statusStyles[doc.status]
          )}
        >
          {isProcessing ? (
            <Loader2 className="h-3 w-3 animate-spin" />
          ) : (
            <CheckCircle2 className="h-3 w-3" />
          )}
          {doc.status}
        </span>
      </div>
    </div>
  );
}