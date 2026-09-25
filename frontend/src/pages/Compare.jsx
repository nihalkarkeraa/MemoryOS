import React, { useState, useEffect } from "react";
import { GitCompareArrows, FileText, Loader2, AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import ComparisonResult from "@/components/compare/ComparisonResult";
import ComparisonSkeleton from "@/components/compare/ComparisonSkeleton";
import { getDocuments, compareDocuments } from "@/services/api";

const suggestedQuestions = [
  "Compare their approaches to database indexing.",
  "How do these documents differ?",
  "What concepts are shared between them?",
];

// State machine: idle -> loading -> (results | error)
// API communication lives in services/api.js; UI never fabricates responses.

export default function Compare() {
  const [doc1, setDoc1] = useState("");
  const [doc2, setDoc2] = useState("");
  const [question, setQuestion] = useState("");
  const [status, setStatus] = useState("idle");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [documents, setDocuments] = useState([]);

  useEffect(() => {
    getDocuments()
      .then(setDocuments)
      .catch(() => setDocuments([]));
  }, []);

  const canCompare = doc1 && doc2 && doc1 !== doc2 && question.trim().length > 0;

  const runCompare = async () => {
    if (!canCompare) return;
    setStatus("loading");
    setResult(null);
    setError(null);
    try {
      const res = await compareDocuments(question, [doc1, doc2], 5);
      setResult(res);
      setStatus("results");
    } catch (err) {
      setError(err.message || "MemoryOS couldn't complete the comparison.");
      setStatus("error");
    }
  };

  const reset = () => {
    setStatus("idle");
    setResult(null);
    setError(null);
  };

  return (
    <div className="mx-auto w-full max-w-5xl px-5 py-8 sm:px-8 sm:py-10">
      {/* Header */}
      <div>
        <h1 className="text-[22px] font-semibold tracking-tight text-foreground">
          Compare documents
        </h1>
        <p className="mt-1 text-[14px] text-muted-foreground">
          Identify similarities, differences, and unique information across your documents.
        </p>
      </div>

      {/* Selectors + question */}
      <div className="mt-6 space-y-4 rounded-2xl border border-border bg-card/40 p-5">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-1.5 block text-[12px] font-medium uppercase tracking-wider text-muted-foreground">
              Document 1
            </label>
            <Select value={doc1} onValueChange={setDoc1}>
              <SelectTrigger className="gap-2 rounded-lg border-border bg-background/60 text-[13px]">
                <SelectValue placeholder="Select a document" />
              </SelectTrigger>
              <SelectContent>
                {documents.map((d) => (
                  <SelectItem key={d.id} value={d.id} disabled={d.id === doc2}>
                    {d.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="mb-1.5 block text-[12px] font-medium uppercase tracking-wider text-muted-foreground">
              Document 2
            </label>
            <Select value={doc2} onValueChange={setDoc2}>
              <SelectTrigger className="gap-2 rounded-lg border-border bg-background/60 text-[13px]">
                <SelectValue placeholder="Select a document" />
              </SelectTrigger>
              <SelectContent>
                {documents.map((d) => (
                  <SelectItem key={d.id} value={d.id} disabled={d.id === doc1}>
                    {d.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <div>
          <label className="mb-1.5 block text-[12px] font-medium uppercase tracking-wider text-muted-foreground">
            Question
          </label>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="What would you like to compare?"
            rows={3}
            className="w-full resize-none rounded-lg border border-input bg-background/60 px-3 py-2.5 text-[13.5px] text-foreground placeholder:text-muted-foreground/60 focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          />
          <div className="mt-2.5 flex flex-wrap gap-2">
            {suggestedQuestions.map((q) => (
              <button
                key={q}
                onClick={() => setQuestion(q)}
                className="rounded-full border border-border bg-muted/30 px-3 py-1 text-[11.5px] text-muted-foreground transition-colors hover:border-primary/40 hover:bg-accent/40 hover:text-foreground"
              >
                {q}
              </button>
            ))}
          </div>
        </div>

        <div className="flex justify-end">
          <Button onClick={runCompare} disabled={!canCompare || status === "loading"} className="gap-1.5">
            {status === "loading" ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <GitCompareArrows className="h-4 w-4" />
            )}
            Compare
          </Button>
        </div>
      </div>

      {/* Result area */}
      <div className="mt-8">
        {status === "idle" && (
          <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border py-16 text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-border bg-muted/40">
              <FileText className="h-5 w-5 text-muted-foreground" />
            </div>
            <p className="mt-4 text-[14px] font-medium text-foreground">
              Select two documents to begin.
            </p>
            <p className="mt-1 max-w-sm text-[13px] text-muted-foreground">
              Choose two documents and ask a question to surface their similarities, differences, and gaps.
            </p>
          </div>
        )}

        {status === "loading" && (
          <div>
            <p className="mb-4 flex items-center gap-2 text-[13px] font-medium text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin text-primary" />
              Analyzing documents...
            </p>
            <ComparisonSkeleton />
          </div>
        )}

        {status === "error" && (
          <div className="flex flex-col items-center justify-center rounded-2xl border border-destructive/30 bg-destructive/5 py-14 text-center">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-destructive/20 bg-destructive/10">
              <AlertCircle className="h-5 w-5 text-destructive" />
            </div>
            <p className="mt-4 text-[14px] font-medium text-foreground">{error}</p>
            <Button variant="outline" size="sm" className="mt-4 gap-1.5 border-border" onClick={reset}>
              <RefreshCw className="h-3.5 w-3.5" />
              Try again
            </Button>
          </div>
        )}

        {status === "results" && result && <ComparisonResult result={result} />}
      </div>
    </div>
  );
}