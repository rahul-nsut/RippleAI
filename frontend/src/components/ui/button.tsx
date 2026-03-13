import React from "react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
}

export default function Button({ children, ...props }: ButtonProps) {
  return (
    <button
      {...props}
      className="btn-primary w-full rounded-xl px-4 py-2.5 text-sm font-semibold
                 text-white transition-all duration-200
                 hover:-translate-y-0.5 active:translate-y-0
                 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-300/70
                 disabled:cursor-not-allowed disabled:opacity-55"
    >
      {children}
    </button>
  );
}
