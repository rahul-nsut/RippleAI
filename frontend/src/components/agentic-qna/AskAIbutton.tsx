"use client";

export default function AskAIButton({
  onClick,
}: {
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="btn-primary pulse-soft fixed bottom-6 right-6 z-50
                 rounded-full px-6 py-3.5
                 text-sm font-semibold text-white
                 transition-all duration-200 hover:-translate-y-1"
    >
      Ask Anything In Your Documents...
    </button>
  );
}
