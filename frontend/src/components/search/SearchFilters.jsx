import React from "react";
import { SlidersHorizontal } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

// Compact filter row. scope = "all" | "<documentId>". nResults = number.
export default function SearchFilters({
  scope,
  onScopeChange,
  documents,
  nResults,
  onNResultsChange,
  resultCount,
}) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <div className="flex items-center gap-1.5 text-[12px] font-medium uppercase tracking-wider text-muted-foreground">
        <SlidersHorizontal className="h-3.5 w-3.5" />
        Filters
      </div>

      {/* Scope: All / Specific document */}
      <Select value={scope} onValueChange={onScopeChange}>
        <SelectTrigger className="h-8 w-[190px] gap-2 rounded-lg border-border bg-card/60 text-[12.5px]">
          <SelectValue placeholder="All documents" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All documents</SelectItem>
          {documents.map((d) => (
            <SelectItem key={d.id} value={d.id}>
              {d.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {/* Number of results */}
      <Select value={String(nResults)} onValueChange={(v) => onNResultsChange(Number(v))}>
        <SelectTrigger className="h-8 w-[120px] gap-2 rounded-lg border-border bg-card/60 text-[12.5px]">
          <SelectValue placeholder="Results" />
        </SelectTrigger>
        <SelectContent>
          {[3, 5, 10, 20].map((n) => (
            <SelectItem key={n} value={String(n)}>
              {n} results
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {typeof resultCount === "number" && (
        <span className="ml-auto text-[12px] text-muted-foreground">
          {resultCount} {resultCount === 1 ? "match" : "matches"}
        </span>
      )}
    </div>
  );
}