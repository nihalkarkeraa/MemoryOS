import React from "react";
import { MessageSquare } from "lucide-react";
import { getRecentQuestions } from "@/services/recentQuestions";

function timeAgo(ts) {
  if (!ts) return "";
  const diff = Date.now() - ts;
  const m = Math.round(diff / 60000);
  if (m < 1) return "just now";
  if (m < 60) return `${m}m ago`;
  const h = Math.round(m / 60);
  if (h < 24) return `${h}h ago`;
  const d = Math.round(h / 24);
  return `${d}d ago`;
}

// Renders real recent questions stored locally (see services/recentQuestions).
export default function RecentQuestions() {
  const questions = getRecentQuestions();
  if (questions.length === 0) return null;

  return (
    <section>
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-[13px] font-medium uppercase tracking-wider text-muted-foreground">
          Recent Questions
        </h3>
      </div>
      <div className="grid grid-cols-1 gap-3 lg:grid-cols-3">
        {questions.map((q) => (
          <div
            key={q.question + (q.ts || "")}
            className="group cursor-pointer rounded-xl border border-border bg-card p-4 transition-all duration-200 hover:border-primary/30 hover:bg-card/80 hover:shadow-lg hover:shadow-black/20"
          >
            <div className="flex items-start gap-2.5">
              <MessageSquare className="mt-0.5 h-4 w-4 shrink-0 text-primary/70" />
              <p className="text-[13.5px] font-medium leading-snug text-foreground">{q.question}</p>
            </div>
            {q.preview ? (
              <p className="mt-2.5 line-clamp-2 pl-6 text-[12.5px] leading-relaxed text-muted-foreground">
                {q.preview}
              </p>
            ) : null}
            <div className="mt-3 pl-6 text-[11.5px] text-muted-foreground/60">{timeAgo(q.ts)}</div>
          </div>
        ))}
      </div>
    </section>
  );
}