import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Upload, Loader2, AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast";
import UploadArea from "@/components/documents/UploadArea";
import DocumentList from "@/components/documents/DocumentList";
import ConfirmDialog from "@/components/common/ConfirmDialog";
import EmptyKnowledgeState from "@/components/home/EmptyKnowledgeState";
import { getDocuments, uploadDocument, deleteDocument } from "@/services/api";

export default function Documents() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);
  const [upload, setUpload] = useState({ status: "idle", progress: 0, fileName: "", note: "" });
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      setDocuments(await getDocuments());
    } catch (e) {
      setLoadError(e.message || "MemoryOS couldn't load your documents.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const handleFile = async (file) => {
    if (file.type && file.type !== "application/pdf" && !file.name.endsWith(".pdf")) {
      setUpload({ status: "error", progress: 0, fileName: file.name, note: "" });
      return;
    }
    setUpload({ status: "uploading", progress: 0, fileName: file.name, note: "" });
    try {
      const doc = await uploadDocument(file, (p) =>
        setUpload((u) => ({ ...u, progress: p }))
      );
      const note = doc.status === "Processing" ? "Processing document…" : "Uploaded successfully";
      setUpload({ status: "success", progress: 100, fileName: doc.name || file.name, note });
      toast({ title: "Document uploaded", description: doc.name || file.name });
      await load();
    } catch (e) {
      setUpload({ status: "error", progress: 0, fileName: file.name, note: "" });
      toast({
        variant: "destructive",
        title: "Upload failed",
        description: e.message || "The document could not be uploaded.",
      });
    }
  };

  const resetUpload = () =>
    setUpload({ status: "idle", progress: 0, fileName: "", note: "" });

  const confirmDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await deleteDocument(deleteTarget.id);
      setDocuments((prev) => prev.filter((d) => d.id !== deleteTarget.id));
      toast({ title: "Document deleted", description: deleteTarget.name });
      setDeleteTarget(null);
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

  const triggerUpload = () => {
    document.getElementById("documents-upload-input")?.click();
  };

  return (
    <div className="mx-auto w-full max-w-6xl px-5 py-8 sm:px-8 sm:py-10">
      {/* Page header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-[22px] font-semibold tracking-tight text-foreground">Documents</h1>
          <p className="mt-1 text-[14px] text-muted-foreground">Manage and explore your knowledge base.</p>
        </div>
        <Button className="gap-2 self-start sm:self-auto" onClick={triggerUpload}>
          <Upload className="h-4 w-4" />
          Upload document
        </Button>
      </div>

      {/* Upload area */}
      <div className="mt-6">
        <UploadArea
          status={upload.status}
          progress={upload.progress}
          fileName={upload.fileName}
          successNote={upload.note || "Uploaded successfully"}
          onFile={handleFile}
          onReset={resetUpload}
        />
      </div>

      {/* Document list / loading / error / empty */}
      <div className="mt-8">
        {loading ? (
          <div className="space-y-2 rounded-xl border border-border bg-card p-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="flex items-center gap-3 py-2">
                <div className="h-8 w-8 animate-pulse rounded-lg bg-muted" />
                <div className="h-3 w-1/3 animate-pulse rounded bg-muted" />
                <div className="ml-auto h-3 w-16 animate-pulse rounded bg-muted" />
              </div>
            ))}
          </div>
        ) : loadError ? (
          <div className="flex flex-col items-center justify-center rounded-2xl border border-destructive/30 bg-destructive/5 py-14 text-center">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-destructive/20 bg-destructive/10">
              <AlertCircle className="h-5 w-5 text-destructive" />
            </div>
            <p className="mt-4 text-[14px] font-medium text-foreground">{loadError}</p>
            <Button variant="outline" size="sm" className="mt-4 gap-1.5 border-border" onClick={load}>
              <RefreshCw className="h-3.5 w-3.5" />
              Try again
            </Button>
          </div>
        ) : documents.length > 0 ? (
          <DocumentList
            documents={documents}
            onOpen={(doc) => navigate(`/documents/${doc.id}`)}
            onSummarize={(doc) => navigate(`/documents/${doc.id}/summary`)}
            onDelete={(doc) => setDeleteTarget(doc)}
          />
        ) : (
          <EmptyKnowledgeState onUpload={triggerUpload} />
        )}
      </div>

      {/* Delete confirmation */}
      <ConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(open) => !open && !deleting && setDeleteTarget(null)}
        title="Delete document?"
        message="This document and its indexed knowledge will be removed."
        confirmLabel={deleting ? "Deleting…" : "Delete"}
        cancelLabel="Cancel"
        destructive
        onConfirm={confirmDelete}
      />
    </div>
  );
}