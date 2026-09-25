import React, { useRef } from "react";
import { ArrowUp, Paperclip, Slash } from "lucide-react";
import { cn } from "@/lib/utils";

export default function AIQuestionInput({ value, onChange, onSubmit }) {
  const ref = useRef(null);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (value.trim()) onSubmit?.();
    }
  };

  return (
    <div
      className="group relative rounded-2xl border border-border bg-card shadow-lg shadow-black/20 transition-colors focus-within:border-primary/50 focus-within:ring-2 focus-within:ring-primary/15"
      onClick={() => ref.current?.focus()}
    >
      <textarea
        ref={ref}
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        onKeyDown={handleKeyDown}
        rows={3}
        placeholder="Ask anything about your knowledge..."
        className="block w-full resize-none rounded-2xl bg-transparent px-4 pt-4 pb-12 text-[15px] leading-relaxed text-foreground placeholder:text-muted-foreground/70 focus:outline-none"
      />
      {/* Bottom toolbar */}
      <div className="absolute inset-x-0 bottom-0 flex items-center justify-between px-3 pb-3">
        <div className="flex items-center gap-1">
          <button
            type="button"
            className="flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
            title="Attach file"
          >
            <Paperclip className="h-[17px] w-[17px]" />
          </button>
          <span className="flex items-center gap-1 rounded-lg px-2 py-1 text-[11px] text-muted-foreground/70">
            <Slash className="h-3 w-3" />
            Shift + Enter for new line
          </span>
        </div>
        <button
          type="button"
          disabled={!value.trim()}
          onClick={onSubmit}
          className={cn(
            "flex h-9 w-9 items-center justify-center rounded-xl transition-all",
            value.trim()
              ? "bg-primary text-primary-foreground shadow-md shadow-primary/25 hover:bg-primary/90"
              : "cursor-not-allowed bg-muted text-muted-foreground/40"
          )}
          title="Send"
        >
          <ArrowUp className="h-[18px] w-[18px]" />
        </button>
      </div>
    </div>
  );
}