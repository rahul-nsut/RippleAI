"use client";

import { useEffect, useRef, useState } from "react";

export default function Menu() {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const full_name = typeof window !== "undefined"
    ? localStorage.getItem("full_name") || ""
    : "";

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleLogout = () => {
    localStorage.clear();
    window.location.href = "/login";
  };

  return (
    <div ref={menuRef} className="relative flex items-center gap-3">
      <span className="text-sm text-slate-300">{full_name}</span>
      <button
        onClick={() => setIsOpen((prev) => !prev)}
        className="flex h-9 w-9 items-center justify-center rounded-full border border-indigo-200/25 bg-gradient-to-br from-indigo-500 to-violet-500 text-sm font-semibold text-white shadow-lg shadow-indigo-500/35"
      >
        {full_name.charAt(0).toUpperCase()}
      </button>

      {isOpen && (
        <div className="glass-surface absolute right-0 top-12 z-50 w-36 rounded-xl p-1.5">
          <button
            onClick={handleLogout}
            className="w-full rounded-lg px-3 py-2 text-left text-sm text-slate-100 transition hover:bg-white/10"
          >
            Logout
          </button>
        </div>
      )}
    </div>
  );
}