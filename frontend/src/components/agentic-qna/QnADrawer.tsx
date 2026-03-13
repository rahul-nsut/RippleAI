"use client";

import { useState } from "react";
import { apiRequestHelper } from "@/lib/api";

export default function QnaDrawer({
  onClose,
}: {
  onClose: () => void;
}) {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  async function askQuestion() {
    if (!question.trim()) return;

    setLoading(true);
    setAnswer("");

    const res = await apiRequestHelper(
      `/agentic-qna?question=${encodeURIComponent(question)}`,
      { method: "POST" }
    );

    const data = await res.json();
    setAnswer(data.answer.answer.content || data.answer.answer);
    setLoading(false);
  }

  return (
    <div
      className="glass-surface fade-in-up fixed bottom-4 right-4 z-50 h-[62vh] w-[420px]
                 rounded-2xl p-4 shadow-2xl"
    >
      {/* Header */}
      <div className="mb-3 flex items-center justify-between border-b border-white/10 pb-3">
        <h3 className="text-sm font-semibold tracking-wide text-slate-100">AI Assistant</h3>
        <button
          onClick={onClose}
          className="rounded-md p-1 text-slate-400 transition hover:bg-white/10 hover:text-white"
        >
          ✕
        </button>
      </div>

      {/* Answer */}
      <div className="mb-3 h-[38vh] overflow-y-auto rounded-xl border border-white/10 bg-slate-950/50 p-3 text-sm">
        {loading && <p className="text-slate-300">Thinking…</p>}
        {!loading && answer && <p>{answer}</p>}
        {!loading && !answer && (
          <p className="text-slate-400">
            Ask anything about your Confluence docs.
          </p>
        )}
      </div>

      {/* Input */}
      <textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask a question..."
        className="mb-2 w-full resize-none rounded-xl border border-white/15
                   bg-slate-950/60 p-3 text-sm text-slate-100 outline-none
                   placeholder:text-slate-400 focus:border-indigo-300/70 focus:ring-2 focus:ring-indigo-300/30"
        rows={3}
      />

      <button
        onClick={askQuestion}
        disabled={loading}
        className="btn-primary w-full rounded-xl py-2.5
                   text-sm font-medium text-white transition-all duration-200
                   hover:-translate-y-0.5 disabled:opacity-50"
      >
        Ask
      </button>
    </div>
  );
}
