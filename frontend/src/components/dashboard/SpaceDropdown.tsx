"use client";

export default function SpaceDropdown() {
  return (
    <select
      className="rounded-xl border border-indigo-200/20 bg-slate-950/40 px-4 py-2.5 text-sm text-slate-100
                 shadow-inner shadow-black/10 transition-all duration-200
                 focus:border-indigo-300/70 focus:outline-none focus:ring-2 focus:ring-indigo-300/30"
    >
      <option>Select Confluence Space</option>
      <option>Engineering</option>
      <option>Platform</option>
      <option>Docs</option>
    </select>
  );
}
