"use client";

import { X } from "lucide-react";
import { useState } from "react";
import AISuggestionsModal, {
  AISuggestionsResponse,
} from "@/components/sync-pages/AISuggestionsModal";
import { apiRequestHelper } from "@/lib/api";

interface Diff {
  added: string[];
  removed: string[];
}

export interface DiffPage {
  page_id: string;
  title: string;
  diff: Diff;
}

interface Props {
  open: boolean;
  page: DiffPage | null;
  onClose: () => void;
  onSynced: (pageId: string) => void;
}

const confBaseUrl = "https://rahul-docs-ai-update.atlassian.net";
const confSpaceKey = "~712020d82452f0cb5c492a8b6f69865eb21a08";


export default function DiffTextModal({ open, page, onClose }: Props) {  
  const confluenceUrl = `${confBaseUrl}/wiki/spaces/${confSpaceKey}/pages/${page?.page_id}`;
  const [syncing, setSyncing] = useState(false);
  const [suggestionsOpen, setSuggestionsOpen] = useState(false);
  const [suggestionsLoading, setSuggestionsLoading] = useState(false);
  const [suggestionsError, setSuggestionsError] = useState<string | null>(null);
  const [suggestionsData, setSuggestionsData] = useState<AISuggestionsResponse | null>(null);
  const applySync = async (url: string) => {
    setSyncing(true);

    try {
      await apiRequestHelper("/commit-sync-to-db", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          url: url
        })
      });

      onClose();
    } finally {
      setSyncing(false);
    }
  };
  const getSuggestions = async () => {
    setSuggestionsOpen(true);
    setSuggestionsLoading(true);
    setSuggestionsError(null);
    setSuggestionsData(null);

    try {
      const response = await apiRequestHelper("/get-suggestions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source_page_id: page?.page_id,
          added_lines: page?.diff.added,
          removed_lines: page?.diff.removed,
        }),
      });
      if (!response.ok) {
        throw new Error("Failed to get AI-based suggestions.");
      }

      const data: AISuggestionsResponse = await response.json();
      setSuggestionsData(data);
    } catch {
      setSuggestionsError("Unable to generate suggestions right now. Please try again.");
    } finally {
      setSuggestionsLoading(false);
    }
  };
if (!open || !page) return null;

  return (
    <>
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-md">
        <div className="glass-surface fade-in-up w-[700px] max-h-[80vh] overflow-hidden rounded-2xl text-white">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-white/10 px-4 py-3">
          <div className="flex flex-col gap-2">
            <h2 className="text-sm font-semibold text-white">{page.title}</h2>
            <p className="text-xs text-slate-300/80">Content changes</p>
          </div>
          <a
            href={confluenceUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="ml-24 flex items-center gap-1 text-sm text-indigo-300 underline transition hover:text-indigo-200"
          >
            View in Confluence
            <span aria-hidden>↗</span>
          </a>
          <button onClick={onClose} className="rounded-md p-1 transition hover:bg-white/10">
            <X className="h-4 w-4 text-white hover:text-gray-300" />
          </button>
        </div>

        {/* Body */}
        <div className="max-h-[65vh] overflow-y-auto px-4 py-3 space-y-4">
          {/* Added */}
          <div>
            <h3 className="mb-2 text-xs font-medium text-green-300">
              Added lines
            </h3>

            {page.diff.added.length === 0 ? (
              <p className="text-xs text-slate-400">No additions</p>
            ) : (
              <div className="space-y-1">
                {page.diff.added.map((line, idx) => (
                  <div
                    key={idx}
                    className="rounded-md border border-emerald-400/30 bg-emerald-500/20 px-2 py-1 text-xs text-emerald-200"
                  >
                    + {line}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Removed */}
          <div>
            <h3 className="mb-2 text-xs font-medium text-red-300">
              Removed lines
            </h3>

            {page.diff.removed.length === 0 ? (
              <p className="text-xs text-slate-400">No removals</p>
            ) : (
              <div className="space-y-1">
                {page.diff.removed.map((line, idx) => (
                  <div
                    key={idx}
                    className="rounded-md border border-rose-400/25 bg-rose-500/20 px-2 py-1 text-xs text-rose-200 line-through"
                  >
                    - {line}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="flex flex-row gap-2 justify-end border-t border-white/10 px-4 py-2 text-right">
          <button
            onClick={() => getSuggestions()}
            className="rounded-xl border border-white/20 px-3 py-1.5 text-xs text-white transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={suggestionsLoading}
          >
            {suggestionsLoading ? "Generating..." : "Get AI Suggestions"}
          </button>
          <button
            onClick={() => applySync(confluenceUrl)}
            className="btn-primary rounded-xl px-3 py-1.5 text-xs text-white transition-all duration-200 hover:-translate-y-0.5"
          >
            {syncing ? "Syncing..." : "Sync Page"}
          </button>
          <button
            onClick={onClose}
            className="rounded-xl border border-white/20 px-3 py-1.5 text-xs text-white transition hover:bg-white/10"
          >
            Close
          </button>
        </div>
        </div>
      </div>
      <AISuggestionsModal
        open={suggestionsOpen}
        onClose={() => setSuggestionsOpen(false)}
        sourcePageTitle={page.title}
        data={suggestionsData}
        loading={suggestionsLoading}
        error={suggestionsError}
      />
    </>
  );
}
