type Props = {
    title: string;
    summary: string;
    url: string;
  };
  
  export default function PageCard({ title, summary }: Props) {
    return (
      <div className="glass-surface surface-hover fade-in-up min-w-[260px] rounded-2xl p-5">
        <div className="mb-3 inline-flex rounded-full border border-indigo-300/25 bg-indigo-400/10 px-2.5 py-1 text-xs font-medium text-indigo-100">
          Confluence
        </div>
  
        <h3 className="mb-2 text-base font-semibold text-slate-100">{title}</h3>
  
        <p className="line-clamp-3 text-sm leading-6 text-slate-300/85">
          {summary+"...."}
        </p>
      </div>
    );
  }
  