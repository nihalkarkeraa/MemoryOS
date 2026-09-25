import React from "react";
import { Link } from "react-router-dom";
import { FileText, MoreHorizontal, CheckCircle2, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

const statusStyles = {
  Ready: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
  Processing: "text-amber-400 bg-amber-500/10 border-amber-500/20",
  Error: "text-rose-400 bg-rose-500/10 border-rose-500/20",
};

// Displays the most recently uploaded documents. Accepts real data via props.
export default function RecentDocuments({ documents = [] }) {
  const list = documents.slice(0, 4);

  return (
    <section>
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-[13px] font-medium uppercase tracking-wider text-muted-foreground">
          Recent Documents
        </h3>
        <Link
          to="/documents"
          className="text-[12.5px] font-medium text-primary/80 transition-colors hover:text-primary"
        >
          View all
        </Link>
      </div>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {list.map((doc) => {
          const isProcessing = doc.status === "Processing";
          return (
            <Link
              key={doc.id}
              to={`/documents/${doc.id}`}
              className="group flex flex-col rounded-xl border border-border bg-card p-4 transition-all duration-200 hover:border-border/80 hover:bg-card/80 hover:shadow-lg hover:shadow-black/20"
            >
              <div className="flex items-start justify-between">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-border bg-muted/40">
                  <FileText className="h-5 w-5 text-primary" />
                </div>
                <MoreHorizontal className="h-4 w-4 text-muted-foreground/60" />
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
                    statusStyles[doc.status] || statusStyles.Ready
                  )}
                >
                  {isProcessing ? (
                    <Loader2 className="h-3 w-3 animate-spin" />
                  ) : (
                    <CheckCircle2 className="h-3 w-3" />
                  )}
                  {doc.status}
                </span>
                <span className="text-[12px] font-medium text-muted-foreground transition-colors group-hover:text-primary">
                  Open
                </span>
              </div>
            </Link>
          );
        })}
      </div>
    </section>
  );
}