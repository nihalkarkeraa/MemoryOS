import React, { useState, useEffect, useRef } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { ArrowLeft, FileText, MessageCircleQuestion, ScrollText, Trash2, AlertCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast";
import { getDocument, deleteDocument, chat } from "@/services/api";
import AIAnswer from "@/components/documents/AIAnswer";
import DocumentDetailSkeleton from "@/components/documents/DocumentDetailSkeleton";
import ConfirmDialog from "@/components/common/ConfirmDialog";

export default function DocumentDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [doc, setDoc] = useState(null);
  const [loadingDoc, setLoadingDoc] = useState(true);
  const [activePage, setActivePage] = useState(1);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const [question, setQuestion] = useState("");
  const [chatState, setChatState] = useState({ status: "idle", answer: null, sources: [], label: "", error: null });
  const labelTimerRef = useRef(null);
  const askTextareaRef = useRef(null);

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

  useEffect(() => {
    return () => {
      if (labelTimerRef.current) clearTimeout(labelTimerRef.current);
    };
  }, []);

  const ask = async () => {
    const q = question.trim();
    if (!q) return;
    setChatState({ status: "loading", answer: null, sources: [], label: "Searching your knowledge...", error: null });
    if (labelTimerRef.current) clearTimeout(labelTimerRef.current);
    labelTimerRef.current = setTimeout(() => {
      setChatState((s) => (s.status === "loading" ? { ...s, label: "Generating answer..." } : s));
    }, 700);
    try {
      const { answer, sources } = await chat(q, 5, [id]);
      if (labelTimerRef.current) clearTimeout(labelTimerRef.current);
      setChatState({ status: "done", answer, sources, label: "", error: null });
    } catch (e) {
      if (labelTimerRef.current) clearTimeout(labelTimerRef.current);
      setChatState({
        status: "error",
        answer: null,
        sources: [],
        label: "",
        error: e.message || "MemoryOS couldn't generate an answer.",
      });
    }
  };

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await deleteDocument(id);
      toast({ title: "Document deleted", description: doc?.name });
      setConfirmDelete(false);
      navigate("/documents");
    } catch (e) {
      toast({
        variant: "destructive",
        title: "Delete failed",
        description: e.message || "The document could not be deleted.",
      });
    } finally {
      setDeleting(false);
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
      <div className="mx-auto w-full max-w-6xl px-5 py-8 sm:px-8 sm:py-10">
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

  const pages = Array.from({ length: doc.pages || 0 }, (_, i) => i + 1);

  return (
    <div className="mx-auto w-full max-w-6xl px-5 py-8 sm:px-8 sm:py-10">
      {/* Back link */}
      <Link
        to="/documents"
        className="inline-flex items-center gap-1.5 text-[12.5px] font-medium text-muted-foreground transition-colors hover:text-foreground"
      >
        <ArrowLeft className="h-3.5 w-3.5" />
        Back to documents
      </Link>

      {/* Header */}
      <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex items-start gap-3">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border border-border bg-muted/40">
            <FileText className="h-6 w-6 text-primary" />
          </div>
          <div className="min-w-0">
            <h1 className="truncate text-[20px] font-semibold tracking-tight text-foreground" title={doc.name}>
              {doc.name}
            </h1>
            <p className="mt-1 text-[13px] text-muted-foreground">
              {doc.pages} pages · {doc.date}
            </p>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            className="gap-1.5 border-border"
            onClick={() => askTextareaRef.current?.focus()}
          >
            <MessageCircleQuestion className="h-3.5 w-3.5" />
            Ask about document
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="gap-1.5 border-border"
            onClick={() => navigate(`/documents/${doc.id}/summary`)}
          >
            <ScrollText className="h-3.5 w-3.5" />
            Summarize
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="gap-1.5 border-destructive/30 text-destructive hover:bg-destructive/10"
            onClick={() => setConfirmDelete(true)}
          >
            <Trash2 className="h-3.5 w-3.5" />
            Delete
          </Button>
        </div>
      </div>

      {/* Two-column layout */}
      <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-[340px_1fr]">
        {/* LEFT: document info + page navigation */}
        <div className="space-y-5">
          <div className="rounded-xl border border-border bg-card/40 p-4">
            <h2 className="text-[13px] font-semibold uppercase tracking-wider text-muted-foreground">
              Overview
            </h2>
            <dl className="mt-3 space-y-2.5">
              <div className="flex justify-between text-[13px]">
                <dt className="text-muted-foreground">Pages</dt>
                <dd className="font-medium text-foreground">{doc.pages}</dd>
              </div>
              <div className="flex justify-between text-[13px]">
                <dt className="text-muted-foreground">Uploaded</dt>
                <dd className="font-medium text-foreground">{doc.date}</dd>
              </div>
              <div className="flex items-center justify-between text-[13px]">
                <dt className="text-muted-foreground">Status</dt>
                <dd>
                  <span
                    className={
                      doc.status === "Ready"
                        ? "inline-flex items-center gap-1 rounded-md border border-emerald-500/20 bg-emerald-500/10 px-2 py-0.5 text-[11px] font-medium text-emerald-400"
                        : "inline-flex items-center gap-1 rounded-md border border-amber-500/20 bg-amber-500/10 px-2 py-0.5 text-[11px] font-medium text-amber-400"
                    }
                  >
                    {doc.status}
                  </span>
                </dd>
              </div>
            </dl>
          </div>

          {pages.length > 0 && (
            <div className="rounded-xl border border-border bg-card/40 p-4">
              <h2 className="text-[13px] font-semibold uppercase tracking-wider text-muted-foreground">
                Pages
              </h2>
              <div className="mt-3 grid max-h-[320px] grid-cols-6 gap-2 overflow-y-auto pr-1">
                {pages.map((p) => (
                  <button
                    key={p}
                    onClick={() => setActivePage(p)}
                    className={
                      "flex h-9 items-center justify-center rounded-lg border text-[12px] font-medium transition-colors " +
                      (p === activePage
                        ? "border-primary bg-primary/15 text-primary"
                        : "border-border bg-muted/20 text-muted-foreground hover:bg-muted hover:text-foreground")
                    }
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* RIGHT: AI interaction */}
        <div className="space-y-4">
          <div className="rounded-xl border border-border bg-card/40 p-4">
            <h2 className="text-[13px] font-semibold uppercase tracking-wider text-muted-foreground">
              Ask about this document
            </h2>
            <textarea
              ref={askTextareaRef}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask something about this document..."
              rows={3}
              className="mt-3 w-full resize-none rounded-lg border border-input bg-background/60 px-3 py-2.5 text-[13.5px] text-foreground placeholder:text-muted-foreground/60 focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            />
            <div className="mt-3 flex justify-end">
              <Button className="gap-1.5" onClick={ask} disabled={!question.trim() || chatState.status === "loading"}>
                {chatState.status === "loading" ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <MessageCircleQuestion className="h-3.5 w-3.5" />
                )}
                Ask
              </Button>
            </div>
          </div>

          {chatState.status === "loading" && (
            <p className="flex items-center gap-2 text-[13px] font-medium text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin text-primary" />
              {chatState.label}
            </p>
          )}
          {chatState.status === "error" && (
            <div className="flex items-center gap-2 rounded-xl border border-destructive/30 bg-destructive/5 px-4 py-3 text-[13px] text-destructive">
              <AlertCircle className="h-4 w-4 shrink-0" />
              {chatState.error}
            </div>
          )}
          {(chatState.status === "loading" || chatState.status === "done") && (
            <AIAnswer
              loading={chatState.status === "loading"}
              answer={chatState.answer}
              sources={chatState.sources}
            />
          )}
        </div>
      </div>

      <ConfirmDialog
        open={confirmDelete}
        onOpenChange={(open) => !open && !deleting && setConfirmDelete(open)}
        title="Delete document?"
        message="This document and its indexed knowledge will be removed."
        confirmLabel={deleting ? "Deleting…" : "Delete"}
        cancelLabel="Cancel"
        destructive
        onConfirm={handleDelete}
      />
    </div>
  );
}