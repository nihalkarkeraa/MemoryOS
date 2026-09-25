import React, { useState, useEffect, useCallback } from "react";
import { Search as SearchIcon, Sparkles, AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import SearchResultCard from "@/components/search/SearchResultCard";
import SearchResultsSkeleton from "@/components/search/SearchResultsSkeleton";
import SearchFilters from "@/components/search/SearchFilters";
import { getDocuments, searchKnowledge } from "@/services/api";

// State machine: idle -> loading -> (results | empty | error)
// API communication lives in services/api.js; UI never fabricates results.

export default function Search() {
  const [query, setQuery] = useState("");
  const [scope, setScope] = useState("all");
  const [nResults, setNResults] = useState(5);
  const [results, setResults] = useState(null);
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState(null);
  const [documents, setDocuments] = useState([]);

  useEffect(() => {
    getDocuments()
      .then(setDocuments)
      .catch(() => setDocuments([]));
  }, []);

  const runSearch = async (e) => {
    e?.preventDefault();
    const q = query.trim();
    if (!q) return;
    setStatus("loading");
    setResults(null);
    setError(null);
    try {
      const documentIds = scope && scope !== "all" ? [scope] : null;
      const res = await searchKnowledge(q, nResults, documentIds);
      setResults(res);
      setStatus(res.length > 0 ? "results" : "empty");
    } catch (err) {
      setError(err.message || "Search failed. Please try again.");
      setStatus("error");
    }
  };

  const retry = () => {
    setError(null);
    setStatus("idle");
  };

  return (
    <div className="mx-auto w-full max-w-4xl px-5 py-8 sm:px-8 sm:py-10">
      {/* Header */}
      <div>
        <h1 className="text-[22px] font-semibold tracking-tight text-foreground">
          Search your knowledge
        </h1>
        <p className="mt-1 text-[14px] text-muted-foreground">
          Find relevant information across your documents.
        </p>
      </div>

      {/* Search bar */}
      <form onSubmit={runSearch} className="mt-6">
        <div className="flex items-center gap-2 rounded-2xl border border-border bg-card/40 p-2 transition-colors focus-within:border-primary/50 focus-within:ring-1 focus-within:ring-primary/30">
          <SearchIcon className="ml-2 h-5 w-5 shrink-0 text-muted-foreground" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search your knowledge..."
            className="h-9 flex-1 bg-transparent px-1 text-[14.5px] text-foreground placeholder:text-muted-foreground/60 focus:outline-none"
          />
          <Button type="submit" className="gap-1.5" disabled={status === "loading"}>
            {status === "loading" ? (
              <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-primary-foreground/40 border-t-primary-foreground" />
            ) : (
              <SearchIcon className="h-4 w-4" />
            )}
            Search
          </Button>
        </div>
      </form>

      {/* Filters */}
      <div className="mt-4">
        <SearchFilters
          scope={scope}
          onScopeChange={setScope}
          documents={documents}
          nResults={nResults}
          onNResultsChange={setNResults}
          resultCount={status === "results" ? results?.length : undefined}
        />
      </div>

      {/* Results area */}
      <div className="mt-6">
        {status === "idle" && (
          <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border py-16 text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-border bg-muted/40">
              <Sparkles className="h-5 w-5 text-primary" />
            </div>
            <p className="mt-4 text-[14px] font-medium text-foreground">
              Search across your knowledge base
            </p>
            <p className="mt-1 max-w-sm text-[13px] text-muted-foreground">
              Enter a query above to find relevant passages, pages, and citations from your documents.
            </p>
          </div>
        )}

        {status === "loading" && <SearchResultsSkeleton count={nResults} />}

        {status === "error" && (
          <div className="flex flex-col items-center justify-center rounded-2xl border border-destructive/30 bg-destructive/5 py-14 text-center">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-destructive/20 bg-destructive/10">
              <AlertCircle className="h-5 w-5 text-destructive" />
            </div>
            <p className="mt-4 text-[14px] font-medium text-foreground">{error}</p>
            <Button variant="outline" size="sm" className="mt-4 gap-1.5 border-border" onClick={retry}>
              <RefreshCw className="h-3.5 w-3.5" />
              Try again
            </Button>
          </div>
        )}

        {status === "empty" && (
          <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border py-14 text-center">
            <SearchIcon className="h-6 w-6 text-muted-foreground/60" />
            <p className="mt-4 text-[14px] font-medium text-foreground">
              No relevant knowledge found.
            </p>
            <p className="mt-1 text-[12.5px] text-muted-foreground">
              Try refining your query or selecting a different document.
            </p>
          </div>
        )}

        {status === "results" && (
          <div className="space-y-3">
            {results.map((r) => (
              <SearchResultCard key={r.id} result={r} query={query} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}