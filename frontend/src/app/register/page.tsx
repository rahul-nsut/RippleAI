import SignUpForm from "@/components/auth/SignUpForm";
import Link from "next/link";

export default function RegisterPage() {
  return (
    <div className="animated-gradient animated-grid relative flex min-h-screen items-center justify-center overflow-hidden px-4">
      <div className="pointer-events-none absolute -left-24 top-14 h-72 w-72 rounded-full bg-indigo-500/20 blur-3xl" />
      <div className="pointer-events-none absolute -right-28 bottom-10 h-72 w-72 rounded-full bg-fuchsia-500/20 blur-3xl" />

      <div className="glass-surface fade-in-up relative w-full max-w-md rounded-3xl p-8 md:p-9">
        <div className="mb-6 text-center">
          <h1 className="text-3xl font-bold tracking-tight text-white">
            AI Knowledge Base
          </h1>
          <p className="mt-2 text-sm text-slate-300">
            Confluence-powered documentation intelligence
          </p>
        </div>

        <SignUpForm />

      </div>
    </div>
  );
}
