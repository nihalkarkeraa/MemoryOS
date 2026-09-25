import React, { useRef, useState } from "react";
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Loader2, X } from "lucide-react";
import { cn } from "@/lib/utils";

// status: 'idle' | 'uploading' | 'success' | 'error'
export default function UploadArea({ status = "idle", progress = 0, fileName, successNote = "Uploaded successfully", onFile, onReset }) {
  const [isDragOver, setIsDragOver] = useState(false);
  const inputRef = useRef(null);

  const handleFiles = (files) => {
    const file = files?.[0];
    if (file) onFile?.(file);
  };

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragOver(true);
      }}
      onDragLeave={(e) => {
        e.preventDefault();
        setIsDragOver(false);
      }}
      onDrop={(e) => {
        e.preventDefault();
        setIsDragOver(false);
        handleFiles(e.dataTransfer.files);
      }}
      className={cn(
        "relative overflow-hidden rounded-2xl border bg-card/40 transition-colors",
        isDragOver
          ? "border-primary/60 bg-accent/30 ring-2 ring-primary/20"
          : "border-dashed border-border",
        status === "idle" && "p-10"
      )}
    >
      {/* Idle / drag state */}
      {status === "idle" && (
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          className="flex w-full flex-col items-center justify-center text-center"
        >
          <div
            className={cn(
              "flex h-14 w-14 items-center justify-center rounded-2xl border border-border transition-colors",
              isDragOver ? "bg-accent/50" : "bg-muted/40"
            )}
          >
            <UploadCloud className={cn("h-6 w-6 transition-colors", isDragOver ? "text-primary" : "text-muted-foreground")} />
          </div>
          <p className="mt-4 text-[15px] font-semibold text-foreground">Drop your document here</p>
          <p className="mt-1 text-[13px] text-muted-foreground">
            or <span className="font-medium text-primary">browse files</span>
          </p>
          <p className="mt-3 text-[11.5px] text-muted-foreground/60">PDF files supported</p>
        </button>
      )}

      {/* Uploading state */}
      {status === "uploading" && (
        <div className="p-6">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-border bg-muted/40">
              <FileText className="h-5 w-5 text-primary" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-[13.5px] font-medium text-foreground">{fileName || "Uploading…"}</p>
              <p className="mt-0.5 flex items-center gap-1.5 text-[12px] text-muted-foreground">
                <Loader2 className="h-3 w-3 animate-spin" />
                Uploading document…
              </p>
            </div>
            <span className="text-[12.5px] font-medium text-muted-foreground">{progress}%</span>
          </div>
          <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-primary transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Success state */}
      {status === "success" && (
        <div className="p-6">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-emerald-500/20 bg-emerald-500/10">
              <CheckCircle2 className="h-5 w-5 text-emerald-400" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-[13.5px] font-medium text-foreground">{fileName}</p>
              <p className="mt-0.5 text-[12px] text-emerald-400">{successNote}</p>
            </div>
            <button
              onClick={onReset}
              className="rounded-md p-1 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      {/* Error state */}
      {status === "error" && (
        <div className="p-6">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-destructive/20 bg-destructive/10">
              <AlertCircle className="h-5 w-5 text-destructive" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-[13.5px] font-medium text-foreground">{fileName || "Upload failed"}</p>
              <p className="mt-0.5 text-[12px] text-destructive">Something went wrong. Please try again.</p>
            </div>
            <button
              onClick={onReset}
              className="rounded-md p-1 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      <input
        id="documents-upload-input"
        ref={inputRef}
        type="file"
        accept="application/pdf"
        className="hidden"
        onChange={(e) => {
          handleFiles(e.target.files);
          e.target.value = "";
        }}
      />
    </div>
  );
}