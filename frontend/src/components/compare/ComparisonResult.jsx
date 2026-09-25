import React from "react";
import { FileText, CheckCircle2, GitCompare, CircleSlash, BookOpen, Sparkles } from "lucide-react";
import SourceCard from "@/components/documents/SourceCard";

function Section({ icon: Icon, title, tone, children }) {
  const toneClass = {
    primary: "text-primary",
    emerald: "text-emerald-400",
    amber: "text-amber-400",
    muted: "text-muted-foreground",
  }[tone];
  return (
    <div className="rounded-xl border border-border bg-card/40 p-4">
      <div className="flex items-center gap-2">
        <div className={"flex h-7 w-7 items-center justify-center rounded-lg bg-muted/40 " + toneClass}>
          <Icon className="h-3.5 w-3.5" />
        </div>
        <h3 className="text-[13.5px] font-semibold tracking-tight text-foreground">{title}</h3>
      </div>
      <div className="mt-3 text-[13px] leading-relaxed text-muted-foreground">{children}</div>
    </div>
  );
}

function ListBlock({ items }) {
  return (
    <ul className="list-disc space-y-2 pl-4">
      {items.map((it, i) => (
        <li key={i} className="text-foreground/85">{it}</li>
      ))}
    </ul>
  );
}

// result: { answer, document1, document2, similarities, differences, notEstablished, sources }
export default function ComparisonResult({ result }) {
  const hasDoc1 = result.document1?.name || result.document1?.summary;
  const hasDoc2 = result.document2?.name || result.document2?.summary;
  const showDocPair = hasDoc1 || hasDoc2;
  const hasSim = result.similarities?.length > 0;
  const hasDiff = result.differences?.length > 0;
  const hasNotEst = result.notEstablished?.length > 0;
  const hasSources = result.sources?.length > 0;

  return (
    <div className="space-y-4">
      {result.answer ? (
        <Section icon={Sparkles} title="Comparison answer" tone="primary">
          <p className="whitespace-pre-line text-foreground/90">{result.answer}</p>
        </Section>
      ) : null}

      {showDocPair && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <Section icon={FileText} title={result.document1?.name || "Document 1"} tone="primary">
            <p>{result.document1?.summary}</p>
          </Section>
          <Section icon={FileText} title={result.document2?.name || "Document 2"} tone="primary">
            <p>{result.document2?.summary}</p>
          </Section>
        </div>
      )}

      {hasSim && (
        <Section icon={CheckCircle2} title="Similarities" tone="emerald">
          <ListBlock items={result.similarities} />
        </Section>
      )}

      {hasDiff && (
        <Section icon={GitCompare} title="Differences" tone="amber">
          <ListBlock items={result.differences} />
        </Section>
      )}

      {hasNotEst && (
        <Section icon={CircleSlash} title="Information not established" tone="muted">
          <ListBlock items={result.notEstablished} />
        </Section>
      )}

      {hasSources && (
        <div>
          <div className="mb-2.5 flex items-center gap-1.5">
            <BookOpen className="h-3.5 w-3.5 text-muted-foreground" />
            <span className="text-[12px] font-medium text-muted-foreground">Sources</span>
          </div>
          <div className="space-y-2.5">
            {result.sources.map((s, i) => (
              <SourceCard key={i} source={s} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}