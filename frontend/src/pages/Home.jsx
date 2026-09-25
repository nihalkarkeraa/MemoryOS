import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import AIQuestionInput from "@/components/home/AIQuestionInput";
import SuggestionChips from "@/components/home/SuggestionChips";
import RecentDocuments from "@/components/home/RecentDocuments";
import RecentQuestions from "@/components/home/RecentQuestions";
import EmptyKnowledgeState from "@/components/home/EmptyKnowledgeState";
import AIAnswer from "@/components/documents/AIAnswer";
import { getDocuments, chat } from "@/services/api";
import { addRecentQuestion } from "@/services/recentQuestions";

function getGreeting() {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 18) return "Good afternoon";
  return "Good evening";
}

export default function Home() {
  const navigate = useNavigate();
  const [question, setQuestion] = useState("");
  const [documents, setDocuments] = useState([]);
  const [loadingDocs, setLoadingDocs] = useState(true);
  const [chatState, setChatState] = useState({ status: "idle", answer: null, sources: [], label: "", error: null });
  const [recentTick, setRecentTick] = useState(0);
  const labelTimerRef = useRef(null);

  useEffect(() => {
    let active = true;
    setLoadingDocs(true);
    getDocuments()
      .then((d) => active && setDocuments(d))
      .catch(() => active && setDocuments([]))
      .finally(() => active && setLoadingDocs(false));
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    return () => {
      if (labelTimerRef.current) clearTimeout(labelTimerRef.current);
    };
  }, []);

  const hasDocuments = documents.length > 0;

  const handleSubmit = async () => {
    const q = question.trim();
    if (!q) return;
    setChatState({ status: "loading", answer: null, sources: [], label: "Searching your knowledge...", error: null });
    if (labelTimerRef.current) clearTimeout(labelTimerRef.current);
    labelTimerRef.current = setTimeout(() => {
      setChatState((s) => (s.status === "loading" ? { ...s, label: "Generating answer..." } : s));
    }, 700);
    try {
      const { answer, sources } = await chat(q, 5, null);
      if (labelTimerRef.current) clearTimeout(labelTimerRef.current);
      setChatState({ status: "done", answer, sources, label: "", error: null });
      addRecentQuestion(q, answer);
      setRecentTick((t) => t + 1);
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

  return (
    <div className="mx-auto w-full max-w-4xl px-5 py-8 sm:px-8 sm:py-12">
      {/* Greeting / hero */}
      <header className="text-center">
        <p className="text-[13px] font-medium text-muted-foreground">{getGreeting()}</p>
        <h1 className="mt-2 text-balance text-[28px] font-semibold tracking-tight text-foreground sm:text-[32px]">
          Your knowledge, connected.
        </h1>
        <p className="mx-auto mt-3 max-w-xl text-[14.5px] leading-relaxed text-muted-foreground">
          Ask questions, explore documents, and discover insights across your knowledge base.
        </p>
      </header>

      {/* AI question area */}
      <div className="mx-auto mt-8 max-w-3xl">
        <AIQuestionInput value={question} onChange={setQuestion} onSubmit={handleSubmit} />
        <div className="mt-4 flex justify-center">
          <SuggestionChips onPick={(text) => setQuestion(text)} />
        </div>

        {/* Chat answer */}
        {chatState.status === "loading" && (
          <p className="mt-6 flex items-center gap-2 text-[13px] font-medium text-muted-foreground">
            <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-primary/40 border-t-primary" />
            {chatState.label}
          </p>
        )}
        {chatState.status === "error" && (
          <p className="mt-6 rounded-xl border border-destructive/30 bg-destructive/5 px-4 py-3 text-[13px] text-destructive">
            {chatState.error}
          </p>
        )}
        {(chatState.status === "loading" || chatState.status === "done") && (
          <div className="mt-6">
            <AIAnswer
              loading={chatState.status === "loading"}
              answer={chatState.answer}
              sources={chatState.sources}
            />
          </div>
        )}
      </div>

      {/* Workspace sections */}
      <div className="mt-12 space-y-10">
        {loadingDocs ? null : hasDocuments ? (
          <>
            <RecentDocuments documents={documents} />
            <div key={recentTick}>
              <RecentQuestions />
            </div>
          </>
        ) : (
          <EmptyKnowledgeState onUpload={() => navigate("/documents")} />
        )}
      </div>
    </div>
  );
}