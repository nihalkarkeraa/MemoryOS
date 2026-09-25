import React from "react";
import { FileText, CheckCircle2, Loader2, MoreHorizontal, FolderOpen, ScrollText, Trash2 } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";
import DocumentCard from "./DocumentCard";

const statusStyles = {
  Ready: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
  Processing: "text-amber-400 bg-amber-500/10 border-amber-500/20",
};

function StatusBadge({ status }) {
  const isProcessing = status === "Processing";
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-md border px-2 py-0.5 text-[11px] font-medium",
        statusStyles[status]
      )}
    >
      {isProcessing ? <Loader2 className="h-3 w-3 animate-spin" /> : <CheckCircle2 className="h-3 w-3" />}
      {status}
    </span>
  );
}

export default function DocumentList({ documents, onOpen, onSummarize, onDelete }) {
  return (
    <>
      {/* Desktop table */}
      <div className="hidden overflow-hidden rounded-xl border border-border bg-card md:block">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border text-left text-[11.5px] font-medium uppercase tracking-wider text-muted-foreground">
              <th className="px-4 py-3 font-medium">Filename</th>
              <th className="px-4 py-3 font-medium">Pages</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Uploaded</th>
              <th className="px-4 py-3 text-right font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((doc) => (
              <tr
                key={doc.id}
                className="border-b border-border/60 transition-colors last:border-0 hover:bg-muted/30"
              >
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2.5">
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-border bg-muted/40">
                      <FileText className="h-4 w-4 text-primary" />
                    </div>
                    <span className="max-w-[260px] truncate text-[13.5px] font-medium text-foreground" title={doc.name}>
                      {doc.name}
                    </span>
                  </div>
                </td>
                <td className="px-4 py-3 text-[13px] text-muted-foreground">{doc.pages}</td>
                <td className="px-4 py-3">
                  <StatusBadge status={doc.status} />
                </td>
                <td className="px-4 py-3 text-[13px] text-muted-foreground">{doc.date}</td>
                <td className="px-4 py-3">
                  <div className="flex items-center justify-end gap-1">
                    <button
                      onClick={() => onOpen?.(doc)}
                      className="flex items-center gap-1 rounded-md px-2 py-1 text-[12.5px] font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                    >
                      <FolderOpen className="h-3.5 w-3.5" />
                      Open
                    </button>
                    <button
                      onClick={() => onSummarize?.(doc)}
                      className="flex items-center gap-1 rounded-md px-2 py-1 text-[12.5px] font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                    >
                      <ScrollText className="h-3.5 w-3.5" />
                      Summarize
                    </button>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <button className="rounded-md p-1.5 text-muted-foreground/60 transition-colors hover:bg-muted hover:text-foreground">
                          <MoreHorizontal className="h-4 w-4" />
                        </button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end" className="w-40">
                        <DropdownMenuItem onClick={() => onOpen?.(doc)}>
                          <FolderOpen className="h-3.5 w-3.5" /> Open
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => onSummarize?.(doc)}>
                          <ScrollText className="h-3.5 w-3.5" /> Summarize
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() => onDelete?.(doc)}
                          className="text-destructive focus:text-destructive"
                        >
                          <Trash2 className="h-3.5 w-3.5" /> Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile cards */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 md:hidden">
        {documents.map((doc) => (
          <DocumentCard
            key={doc.id}
            doc={doc}
            onOpen={onOpen}
            onSummarize={onSummarize}
            onDelete={onDelete}
          />
        ))}
      </div>
    </>
  );
}