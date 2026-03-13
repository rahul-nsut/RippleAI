"use client";

import { X } from "lucide-react";

export interface AISuggestedChange {
  action: "ADD" | "UPDATE" | "REMOVE" | "DELETE";
  existing_text: string;
  new_text: string;
  reason: string;
}

export interface AISuggestionsByPage {
  page_id: string;
  title: string;
  confidence: number;
  suggested_changes: {
    page_id: string;
    suggestions: AISuggestedChange[];
  };
}

export interface AISuggestionsResponse {
  source_page_id: string;
  suggestions: AISuggestionsByPage[];
}

interface AISuggestionsModalProps {
  open: boolean;
  onClose: () => void;
  sourcePageTitle: string;
  data: AISuggestionsResponse | null;
  loading: boolean;
  error: string | null;
}

const actionStyles: Record<AISuggestedChange["action"], string> = {
  ADD: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
  UPDATE: "bg-amber-500/20 text-amber-300 border-amber-500/30",
  REMOVE: "bg-rose-500/20 text-rose-300 border-rose-500/30",
  DELETE: "bg-rose-500/20 text-rose-300 border-rose-500/30",
};

export default function AISuggestionsModal({
  open,
  onClose,
  sourcePageTitle,
  data,
  loading,
  error,
}: AISuggestionsModalProps) {
  if (!open) return null;
  const actionableSuggestions =
    data?.suggestions.filter(
      (entry) => entry.suggested_changes.suggestions.length > 0
    ) ?? [];

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/70 backdrop-blur-md">
      <div className="glass-surface fade-in-up w-full max-w-4xl rounded-2xl text-white shadow-2xl">
        <div className="flex items-start justify-between gap-4 border-b border-white/10 px-6 py-4">
          <div>
            <h2 className="text-base font-semibold">AI Suggestions</h2>
            <p className="mt-1 text-xs text-gray-400">
              Recommended updates for related pages based on changes in{" "}
              <span className="font-medium text-gray-200">{sourcePageTitle}</span>
            </p>
            <p className="mt-1 text-xs text-gray-400">
              We would suggest you to review the suggestions provided by AI, and only make the changes if you find them accurate. 
            </p>
          </div>
          <button
            onClick={onClose}
            className="rounded-md p-1 text-gray-300 transition hover:bg-white/10 hover:text-white"
            aria-label="Close suggestions modal"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="max-h-[70vh] overflow-y-auto px-6 py-5">
          {loading ? (
            <div className="rounded-lg border border-white/10 bg-white/5 p-4 text-sm text-gray-300">
             🧠 AI is thinking...
            </div>
          ) : error ? (
            <div className="rounded-lg border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-200">
              {error}
            </div>
          ) : !data || actionableSuggestions.length === 0 ? (
            <div className="rounded-lg border border-white/10 bg-white/5 p-4 text-sm text-gray-300">
              No actionable changes were suggested for related pages.
            </div>
          ) : (
            <div className="space-y-4">
              {actionableSuggestions.map((entry) => (
                <section
                  key={entry.page_id}
                  className="surface-hover rounded-xl border border-white/10 bg-[#141824] p-4"
                >
                  <div className="mb-3 flex items-center justify-between gap-3">
                    <h3 className="truncate text-sm font-semibold text-white">
                      {entry.title}
                    </h3>
                    <span className="rounded-full border border-sky-500/30 bg-sky-500/15 px-2.5 py-1 text-xs font-medium text-sky-200">
                      {(entry.confidence * 100).toFixed(1)}% confidence
                    </span>
                  </div>

                  <div className="space-y-3">
                    {entry.suggested_changes.suggestions.map((suggestion, idx) => (
                      <article
                        key={`${entry.page_id}-${idx}`}
                        className="rounded-md border border-white/10 bg-black/25 p-3"
                      >
                        <div className="mb-2">
                          <span
                            className={`inline-flex rounded border px-2 py-0.5 text-[11px] font-semibold tracking-wide ${actionStyles[suggestion.action]}`}
                          >
                            {suggestion.action}
                          </span>
                        </div>

                        {suggestion.existing_text ? (
                          <div className="mb-2">
                            <p className="mb-1 text-[11px] font-medium uppercase tracking-wide text-gray-400">
                              Existing text
                            </p>
                            <p className="rounded bg-white/5 px-2 py-1.5 text-xs text-gray-200">
                              {suggestion.existing_text}
                            </p>
                          </div>
                        ) : null}

                        {suggestion.new_text ? (
                          <div className="mb-2">
                            <p className="mb-1 text-[11px] font-medium uppercase tracking-wide text-gray-400">
                              Suggested text
                            </p>
                            <p className="rounded bg-emerald-500/10 px-2 py-1.5 text-xs text-emerald-100">
                              {suggestion.new_text}
                            </p>
                          </div>
                        ) : null}

                        <div>
                          <p className="mb-1 text-[11px] font-medium uppercase tracking-wide text-gray-400">
                            Why this change
                          </p>
                          <p className="text-xs text-gray-300">{suggestion.reason}</p>
                        </div>
                      </article>
                    ))}
                  </div>
                </section>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
