import SpaceDropdown from "../../components/dashboard/SpaceDropdown";
import SyncPagesButton from "../sync-pages/SyncButton";
import Menu from "../ui/menu";

export default function TopBar({ onSyncPagesClick }: { onSyncPagesClick: () => Promise<void> }) {
  return (
    <header className="glass-surface sticky top-0 z-40 mx-auto mt-3 flex w-[calc(100%-2rem)] max-w-7xl items-center justify-between rounded-2xl px-5 py-4 sm:px-6">
      {/* Left */}
      <div className="text-lg font-semibold tracking-tight text-slate-100">
        AI Knowledge Base
      </div>

      {/* Center */}
      <SpaceDropdown />

      {/*Sync Button*/}
      <SyncPagesButton onClick={onSyncPagesClick} />

      {/* Right */}
      <Menu />
    </header>
  );
}
