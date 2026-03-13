
"use client";

interface SyncPagesButtonProps {
  onClick: () => void;
}

export default function SyncPagesButton({ onClick }: SyncPagesButtonProps) {
  return (
    <button
      onClick={onClick}
      className="
        btn-primary flex items-center gap-2
        rounded-xl px-4 py-2.5
        text-sm font-medium text-white
        hover:cursor-pointer
        transition-all duration-200
        hover:-translate-y-0.5
      "
    >
      Sync Pages
    </button>
  );
}
