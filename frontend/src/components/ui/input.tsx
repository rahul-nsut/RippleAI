import React from "react";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
}

export default function Input({ label, ...props }: InputProps) {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-sm font-medium text-slate-100/95">
        {label}
      </label>
      <input
        {...props}
        className="rounded-xl border border-white/20 bg-slate-950/45 px-3.5 py-2.5 text-sm text-white
                   placeholder:text-slate-400 focus:border-indigo-300/70
                   focus:outline-none focus:ring-2 focus:ring-indigo-300/40"
      />
    </div>
  );
}
