"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import TopBar from "@/components/dashboard/TopBar";
import PageCard from "@/components/dashboard/PageCard";
import QnaDrawer from "@/components/agentic-qna/QnADrawer";
import AskAIButton from "@/components/agentic-qna/AskAIbutton";
import SyncDocsModal, { SyncPageChange } from "@/components/sync-pages/SyncModal";
import DiffTextModal, { DiffPage } from "@/components/sync-pages/DiffTextModal";
import { toast } from "react-toastify";
import { apiRequestHelper } from "@/lib/api";

type Page = {
  doc_id: string;
  source: string;
  preview: string;
  title: string;
};

export default function DashboardPage() {
  const router = useRouter();
  const [pages, setPages] = useState<Page[]>([]);
  const [open, setOpen] = useState(false);
  const [isSyncModalOpen, setIsSyncModalOpen] = useState(false);
  const [syncLoading, setSyncLoading] = useState(false);
  const [changes, setChanges] = useState<SyncPageChange[]>([]);
  const [selectedPage, setSelectedPage] = useState<DiffPage | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }

    apiRequestHelper("/data/documents")
      .then(res => res.json())
      .then(data => setPages(data));
  }, [router]);

  const handleSyncPages = async () => {
    // Open modal immediately and show loading state
    setIsSyncModalOpen(true);
    setSyncLoading(true);
    setChanges([]);

    // Make the API call
    try {
      const response = await apiRequestHelper("/sync-pages", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          space_key: "~712020d82452f0cb5c492a8b6f69865eb21a08",
        }),
      });
      if (!response.ok) {
        throw new Error("Failed to sync pages");
      }
      const data = await response.json();
      toast.success("Synced pages successfully", {
        position: "top-right",
        autoClose: 5000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
      if (data.status === "CHANGES_FOUND") {
        setChanges(data.changes);
      } else {
        setChanges([]);
      }
    }
    catch (error) {
      console.error("Error syncing pages:", error);
      toast.error("Failed to sync pages", {
        position: "top-right",
        autoClose: 5000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
    }
    finally {
      setSyncLoading(false);
    }
  }

  const fetchPages = async () => {
    const response = await apiRequestHelper("/data/documents");
    if (!response.ok) {
      throw new Error("Failed to fetch pages");
    }
    const data = await response.json();
    setPages(data);
    setIsSyncModalOpen(false);
  }

  return (
    <div className="animated-grid relative min-h-screen overflow-hidden text-white">
      <div className="pointer-events-none absolute -left-28 top-10 h-72 w-72 rounded-full bg-indigo-500/20 blur-3xl" />
      <div className="pointer-events-none absolute -right-20 top-24 h-72 w-72 rounded-full bg-fuchsia-500/15 blur-3xl" />
      <div className="pointer-events-none absolute bottom-0 left-1/2 h-72 w-72 -translate-x-1/2 rounded-full bg-emerald-500/10 blur-3xl" />
      <TopBar onSyncPagesClick={handleSyncPages} />

      <main className="relative z-10 mx-auto w-full max-w-7xl px-6 py-8 sm:px-8">
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-xl font-semibold tracking-tight text-slate-100">
            List of Pages in your Confluence Space
          </h2>
          <span className="rounded-full border border-indigo-300/25 bg-indigo-400/10 px-3 py-1 text-xs font-medium text-indigo-100/90">
            {pages.length} pages
          </span>
        </div>

        <div className="flex flex-col gap-4 overflow-x-auto">
          {pages.map(page => (
            <PageCard
              key={page.doc_id}
              title={page.title}
              summary={page.preview}
              url={page.source}
            />
          ))}
        </div>
        <AskAIButton onClick={() => setOpen(true)} />
        {open && <QnaDrawer onClose={() => setOpen(false)} />}
      </main>

      <SyncDocsModal
        open={isSyncModalOpen}
        onClose={() => setIsSyncModalOpen(false)}
        pages={changes}
        onSyncComplete={fetchPages}
        loading={syncLoading}
        onSelectPage={(page) => {
          if (page.type === "UPDATED") {
            setSelectedPage({
              page_id: page.page_id,
              title: page.title,
              diff: page.diff || { added: [], removed: [] },
            });
          }
        }}
      />
      <DiffTextModal
        open={!!selectedPage}
        page={selectedPage ? {
          page_id: selectedPage.page_id,
          title: selectedPage.title,
          diff: selectedPage.diff || { added: [], removed: [] },
        } : null}
        onClose={() => setSelectedPage(null)}
        onSynced={(pageId) => {
          setChanges(prev =>
            prev.filter(p => p.page_id !== pageId)
          )
          setSelectedPage(null)
        }}
      />
    </div>
  );
}
