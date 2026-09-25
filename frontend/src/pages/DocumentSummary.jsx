import React, { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { ArrowLeft, FileText, ScrollText, RefreshCw, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast";
import { getDocument, summarizeDocument } from "@/services/api";
import SummaryCard from "@/components/documents/SummaryCard";
import DocumentDetailSkeleton from "@/components/documents/DocumentDetailSkeleton";

export default function DocumentSummary() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [doc, setDoc] = useState(null);
  const [loadingDoc, setLoadingDoc] = useState(true);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;
    setLoadingDoc(true);
    getDocument(id)
      .then((d) => active && setDoc(d))
      .catch(() => active && setDoc(null))
      .finally(() => active && setLoadingDoc(false));
    return () => {
      active = false;
    };
  }, [id]);

  const generate = async () => {
    setLoading(true);
    setError(null);
    setSummary(null);
    try {
      const res = await summarizeDocument(id);
      setSummary(res);
    } catch (e) {
      setError(e.message || "MemoryOS couldn't generate the summary.");
      toast({
        variant: "destructive",
        title: "Summary failed",
        description: e.message || "MemoryOS couldn't generate the summary.",
      });
    } finally {
      setLoading(false);
    }
  };

  if (loadingDoc) {
    return (
      <div className="mx-auto w-full max-w-6xl px-5 py-8 sm:px-8 sm:py-10">
        <DocumentDetailSkeleton />
      </div>
    );
  }

  if (!doc) {
    return (
      <div className="mx-auto w-full max-w-4xl px-5 py-8 sm:px-8 sm:py-10">
        <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border py-16 text-center">
          <AlertCircle className="h-6 w-6 text-muted-foreground/60" />
          <p className="mt-4 text-[14px] font-medium text-foreground">Document not found.</p>
          <Button variant="outline" size="sm" className="mt-4 border-border" onClick={() => navigate("/documents")}>
            Back to documents
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-4xl px-5 py-8 sm:px-8 sm:py-10">
      <Link
        to={`/documents/${doc.id}`}
        className="inline-flex items-center gap-1.5 text-[12.5px] font-medium text-muted-foreground transition-colors hover:text-foreground"
      >
        <ArrowLeft className="h-3.5 w-3.5" />
        Back to document
      </Link>

      {/* Header */}
      <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-border bg-muted/40">
            <ScrollText className="h-5 w-5 text-primary" />
          </div>
          <div className="min-w-0">
            <h1 className="truncate text-[20px] font-semibold tracking-tight text-foreground">
              Summary
            </h1>
            <p className="mt-0.5 truncate text-[13px] text-muted-foreground" title={doc.name}>
              {doc.name}
            </p>
          </div>
        </div>
        <Button variant="outline" size="sm" className="gap-1.5 border-border" onClick={generate} disabled={loading}>
          <RefreshCw className={"h-3.5 w-3.5 " + (loading ? "animate-spin" : "")} />
          {loading ? "Generating summary…" : "Generate summary"}
        </Button>
      </div>

      {/* Error */}
      {error && (
        <div className="mt-6 flex items-center gap-2 rounded-xl border border-destructive/30 bg-destructive/5 px-4 py-3 text-[13px] text-destructive">
          <AlertCircle className="h-4 w-4 shrink-0" />
          {error}
        </div>
      )}

      {/* Summary sections */}
      <div className="mt-8 space-y-5">
        <SummaryCard title="Overview" loading={loading}>
          {summary?.overview ? (
            <p className="whitespace-pre-line text-muted-foreground">{summary.overview}</p>
          ) : (
            <p className="text-muted-foreground">
              {loading ? null : "Generate a summary to see an AI-produced overview of this document."}
            </p>
          )}
        </SummaryCard>
        <SummaryCard title="Key Concepts" loading={loading}>
          {summary?.keyConcepts?.length ? (
            <ul className="list-disc space-y-1.5 pl-4 text-muted-foreground">
              {summary.keyConcepts.map((c, i) => (
                <li key={i}>{c}</li>
              ))}
            </ul>
          ) : (
            <p className="text-muted-foreground">
              {loading ? null : "Generate a summary to surface the key concepts discussed in the document."}
            </p>
          )}
        </SummaryCard>
        <SummaryCard title="Important Points" loading={loading}>
          {summary?.importantPoints?.length ? (
            <ul className="list-disc space-y-1.5 pl-4 text-muted-foreground">
              {summary.importantPoints.map((p, i) => (
                <li key={i}>{p}</li>
              ))}
            </ul>
          ) : (
            <p className="text-muted-foreground">
              {loading ? null : "Generate a summary to extract the most important points."}
            </p>
          )}
        </SummaryCard>
      </div>
    </div>
  );
}