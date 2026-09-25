"use client";

import { demoScenarios } from "@/data/demoScenarios";
import { requestQueue } from "@/data/requestQueue";
import { ArrowRight, Check, ChevronDown, CircleAlert, FileQuestion, Search } from "lucide-react";
import { useState } from "react";

interface Props {
  activeId: string;
  onSelect: (id: string) => void;
  workOrder: string;
  onLoadWorkOrder: (value: string) => Promise<void>;
  loading: boolean;
  loadError: string;
  loadedStatus: string;
}

const icons = { CONFLICTING: CircleAlert, MISSING: Search, UNRESOLVED: FileQuestion, UNVERIFIED: FileQuestion, CONFIRMED: Check };

export default function ScenarioRail({ activeId, onSelect, workOrder, onLoadWorkOrder, loading, loadError, loadedStatus }: Props) {
  const [value, setValue] = useState(workOrder);
  const [inputError, setInputError] = useState("");
  const submitWorkOrder = () => {
    const normalized = value.trim().toUpperCase();
    if (!/^SYN-WO-\d{6}$/.test(normalized)) {
      setInputError("Use the format SYN-WO-000023.");
      return;
    }
    setInputError("");
    void onLoadWorkOrder(normalized);
  };
  return <aside className="h-full overflow-y-auto border-r border-[#0f172a]/10 bg-white">
    <div className="border-b border-[#0f172a]/10 p-5 lg:p-6">
      <p className="micro-label text-[#2563eb]">Start research</p>
      <h2 className="mt-2 text-xl font-bold tracking-[-.03em]">Enter a work order</h2>
      <p className="mt-2 text-xs leading-5 text-[#64748b]">Load the WO you are researching, then explain where you need guidance.</p>
      <form onSubmit={event => { event.preventDefault(); if (!loading) submitWorkOrder(); }} className="mt-4 flex gap-2 rounded-xl border border-[#0f172a]/10 bg-[#f8fafc] p-2 focus-within:border-[#2563eb]/40">
        <input value={value} disabled={loading} maxLength={13} autoCapitalize="characters" spellCheck={false} onChange={event => { setValue(event.target.value.toUpperCase()); setInputError(""); }} aria-label="Work order number" aria-describedby="work-order-message" placeholder="SYN-WO-000023" className="min-w-0 flex-1 bg-transparent px-2 text-xs font-semibold uppercase outline-none placeholder:font-normal placeholder:text-[#94a3b8] disabled:opacity-60" />
        <button disabled={loading || !value.trim()} type="submit" aria-label="Load work order" title="Load work order" style={{ color: "white" }} className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-[#2563eb] to-[#8b3fd1] shadow-[0_6px_16px_rgba(37,99,235,.28)] transition hover:-translate-y-0.5 disabled:cursor-wait disabled:opacity-50 disabled:hover:translate-y-0"><ArrowRight size={15} strokeWidth={2.5} className={loading ? "animate-pulse" : ""} /></button>
      </form>
      {loading && <div className="mt-3 flex items-center gap-2 text-[10px] font-semibold text-[#2563eb]"><span className="h-1.5 w-1.5 animate-pulse rounded-full bg-[#2563eb]" /> Retrieving work order…</div>}
      {!loading && (inputError || loadError) && <div id="work-order-message" role="alert" className="mt-3 text-[10px] font-semibold leading-4 text-[#c2410c]">{inputError || loadError}</div>}
      {!loading && !inputError && !loadError && <div id="work-order-message" className="mt-3 flex items-center gap-2 text-[10px] font-semibold text-[#16a34a]"><span className="h-1.5 w-1.5 rounded-full bg-[#22c55e]" /> Loaded: {workOrder}{loadedStatus ? ` · ${loadedStatus.replaceAll("_", " ")}` : ""}</div>}
      <details className="group mt-4 overflow-hidden rounded-xl border border-[#0f172a]/10 bg-white">
        <summary className="flex cursor-pointer list-none items-center justify-between px-3 py-2.5 text-xs font-bold text-[#334155]">Request queue <span className="flex items-center gap-2 text-[10px] font-semibold text-[#64748b]">100 WOs <ChevronDown size={13} className="transition group-open:rotate-180" /></span></summary>
        <div className="max-h-64 space-y-1 overflow-y-auto border-t border-[#0f172a]/10 p-2 [scrollbar-width:thin]">{requestQueue.map(item => <button key={item.id} disabled={loading} onClick={() => { setValue(item.id); setInputError(""); void onLoadWorkOrder(item.id); }} className="flex w-full items-center justify-between gap-3 rounded-lg px-2.5 py-2 text-left transition hover:bg-[#eff6ff] disabled:opacity-50"><span><b className="block text-[10px] text-[#2563eb]">{item.id}</b><span className="mt-0.5 block text-[10px] leading-4 text-[#64748b]">{item.scenario}</span></span><span className="shrink-0 text-[9px] font-bold text-[#94a3b8]">V{item.variant}</span></button>)}</div>
      </details>
    </div>
    <p className="micro-label px-5 pt-5 text-[#94a3b8] lg:px-6">Example situations</p>
    <nav aria-label="Demo scenarios" className="flex gap-2 overflow-x-auto p-3 lg:block lg:space-y-1 lg:overflow-visible">
      {demoScenarios.map(s => {
        const Icon = icons[s.status]; const active = s.id === activeId;
        return <button key={s.id} onClick={() => onSelect(s.id)} className={`relative min-w-[220px] overflow-hidden rounded-2xl border p-4 text-left transition lg:min-w-0 lg:w-full ${active ? "border-[#2563eb]/30 bg-[#eef2ff] shadow-[0_10px_28px_rgba(37,99,235,.12)]" : "border-transparent hover:border-[#0f172a]/10 hover:bg-[#f8fafc]"}`}>
          {active && <span className="absolute inset-y-3 left-0 w-1 rounded-r-full bg-gradient-to-b from-[#2563eb] to-[#8b3fd1]" />}
          <div className="flex items-center justify-between"><span className="text-[10px] font-bold tracking-[.14em] text-[#2563eb]">{s.index} / {s.eyebrow.toUpperCase()}</span><Icon size={14} className={active ? "text-[#8b3fd1]" : "text-[#64748b]"} /></div>
          <p className="mt-3 text-sm font-bold text-[#0f172a]">{s.title}</p><p className="mt-1 line-clamp-2 text-xs leading-5 text-[#64748b]">{s.description}</p>
        </button>;
      })}
    </nav>
  </aside>;
}
