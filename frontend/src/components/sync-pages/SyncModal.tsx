"use client";

import { apiRequestHelper } from "@/lib/api";
import { X } from "lucide-react";
import { useState } from "react";
import { toast } from "react-toastify";

export interface SyncPageChange {
  type: "NEW" | "UPDATED" | "UNCHANGED";
  page_id: string;
  title: string;
  diff?: {
    added: string[];
    removed: string[];
  };
}

interface SyncDocsModalProps {
  open: boolean;
  onClose: () => void;
  pages: SyncPageChange[];
  onSelectPage: (page: SyncPageChange) => void;
  loading?: boolean;
  onSyncComplete?: () => void;
}

export default function SyncDocsModal({
  open,
  onClose,
  pages,
  onSelectPage,
  loading = false,
  onSyncComplete,
}: SyncDocsModalProps) {
  const changedPages = pages.filter(p => p.type !== "UNCHANGED");
  const syncablePages = pages.filter(
    c => c.type === "UPDATED" || c.type === "NEW"
  )
  const [isSyncingAll, setIsSyncingAll] = useState(false)
  const confBaseUrl = "https://rahul-docs-ai-update.atlassian.net";
  const confSpaceKey = "~712020d82452f0cb5c492a8b6f69865eb21a08";

  if (!open) return null;


const handleSyncAll = async () => {
  if (syncablePages.length > 0 && syncablePages.some(page => page.type === "UPDATED")) {
    if (!confirm("This will synchronize pages without reviewing AI-detected inconsistencies caused by recent source updates. We would suggest you to review the pages before syncing to ensure the consistency of the knowledge base. Still proceed?")) return;
  }
  if (syncablePages.length === 0) return;

  setIsSyncingAll(true);

  try {
    for (const page of syncablePages) {
      const confluenceUrl = `${confBaseUrl}/wiki/spaces/${confSpaceKey}/pages/${page.page_id}`;
      await apiRequestHelper("/commit-sync-to-db", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: confluenceUrl }),
      })
    }

    toast.success("All pages synced successfully")
    onSyncComplete?.();
    onClose();

  } catch {
    toast.error("Failed while syncing pages")
  } finally {
    setIsSyncingAll(false)
  }
}


  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-md">
      <div className="glass-surface fade-in-up w-full max-w-3xl rounded-2xl text-white">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-white/10 px-6 py-4">
          <h2 className="text-lg font-semibold text-white">
            Confluence Pages Updated
          </h2>
          <button
            onClick={onClose}
            className="rounded-md p-1 transition hover:bg-white/10"
          >
            <X className="h-5 w-5 text-white hover:text-gray-300" />
          </button>
        </div>

        {/* Body */}
        <div className="max-h-[60vh] overflow-y-auto px-6 py-4">
          {loading ? (
            <p className="text-sm text-white">Checking updates...</p>
          ) : changedPages.length === 0 ? (
            <p className="text-sm text-white">
              Wohooo! Everything is up to date.
            </p>
          ) : (
            <ul className="space-y-3">
              {changedPages.map(page => (
                <li
                  key={page.page_id}
                  className="surface-hover cursor-pointer rounded-xl border border-white/10 bg-slate-950/35 p-4 text-white"
                  onClick={() => onSelectPage(page)}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{page.title}</span>
                    <span
                      className={`rounded px-2 py-0.5 text-xs font-medium ${
                        page.type === "UPDATED"
                          ? "bg-yellow-500/20 text-yellow-300"
                          : "bg-green-500/20 text-green-300"
                      }`}
                    >
                      {page.type}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-2 border-t border-white/10 px-6 py-4">
          <button
            onClick={onClose}
            className="rounded-xl border border-white/20 px-4 py-2 text-sm text-white transition hover:bg-white/10"
          >
            Close
          </button>
          <button
            onClick={handleSyncAll}
            className="btn-primary rounded-xl px-4 py-2 text-sm text-white transition-all duration-200 hover:-translate-y-0.5"
          >
            {isSyncingAll ? "Syncing..." : "Sync All"}
          </button>
        </div>
      </div>
    </div>
    );
}
