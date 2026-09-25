import React from "react";
import { UploadCloud, FileStack } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function EmptyKnowledgeState({ onUpload }) {
  return (
    <section className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border bg-card/30 px-6 py-14 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-border bg-muted/40">
        <FileStack className="h-6 w-6 text-primary" />
      </div>
      <h3 className="mt-5 text-lg font-semibold tracking-tight text-foreground">
        Your knowledge base is empty.
      </h3>
      <p className="mt-2 max-w-sm text-[13.5px] leading-relaxed text-muted-foreground">
        Upload your first document to start building MemoryOS.
      </p>
      <Button onClick={onUpload} className="mt-6 gap-2">
        <UploadCloud className="h-4 w-4" />
        Upload document
      </Button>
    </section>
  );
}