"use client";

import { ArrowUp, LockKeyhole } from "lucide-react";
import { useState } from "react";

export default function PromptBar() {
  const [value, setValue] = useState("");
  return <div className="rounded-2xl border border-[#0f172a]/10 bg-white p-2 shadow-[0_12px_36px_rgba(15,23,42,.06)]">
    <div className="flex items-center gap-3"><input value={value} onChange={e => setValue(e.target.value)} placeholder="Ask about this synthetic work order…" aria-label="Ask about this synthetic work order" className="min-w-0 flex-1 bg-transparent px-3 py-2 text-sm outline-none placeholder:text-[#94a3b8]" /><button onClick={() => setValue("")} aria-label="Submit demo prompt" className="flex h-9 w-9 items-center justify-center rounded-full bg-[#0f172a] text-white transition hover:bg-[#2563eb]"><ArrowUp size={15} /></button></div>
    <div className="flex items-center gap-1.5 px-3 pb-1 text-[10px] font-medium text-[#94a3b8]"><LockKeyhole size={10} /> Demo only · no agent connection</div>
  </div>;
}
