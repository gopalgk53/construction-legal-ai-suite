"use client";

import { motion } from "framer-motion";
import { ArrowRight, ArrowUpRight, Bot, Check, FileSearch, ShieldCheck, Sparkles } from "lucide-react";

interface IntroSceneProps { onEnter: () => void; }
const ease = [0.16, 1, 0.3, 1] as const;

export default function IntroScene({ onEnter }: IntroSceneProps) {
  return (
    <motion.section initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0, y: -24 }} transition={{ duration: .5 }} className="min-h-screen bg-[#0f172a] text-white">
      <header className="flex h-[72px] items-center justify-between border-b border-white/10 bg-[#f8fafc] px-6 text-[#0f172a] md:px-12">
        <span className="text-sm font-semibold tracking-[-0.02em]">NTO Operations Copilot</span>
        <span className="text-xs font-medium">System 03 / 05</span>
      </header>
      <div className="mx-auto grid min-h-[calc(100vh-72px)] max-w-[1440px] items-center gap-14 px-6 py-16 md:px-12 lg:grid-cols-[1.08fr_.92fr] lg:py-20">
        <div>
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: .1 }} className="mb-7 inline-flex items-center gap-2 rounded-full border border-white/15 px-3 py-1.5 text-xs font-semibold">
            <span className="h-1.5 w-1.5 rounded-full bg-[#63b3ff]" /> NTO Operations Copilot
          </motion.div>
          <div className="overflow-hidden">
            <motion.h1 initial={{ y: "105%" }} animate={{ y: 0 }} transition={{ duration: .85, ease }} className="max-w-3xl text-[clamp(3rem,6vw,5.6rem)] font-bold leading-[.98] tracking-[-0.055em]">
              Your guide through<br />every <span className="bg-gradient-to-r from-[#63b3ff] to-[#a873db] bg-clip-text text-transparent">NTO research step.</span>
            </motion.h1>
          </div>
          <motion.p initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: .28, duration: .6 }} className="mt-8 max-w-xl text-base leading-7 text-white/72 md:text-lg">
            A step-by-step coach for new researchers. Learn what to check, why it matters and what to do next—especially when a case stops being straightforward.
          </motion.p>
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: .42 }} className="mt-10 flex flex-wrap gap-3">
            <button onClick={onEnter} className="group flex items-center gap-3 rounded-full bg-gradient-to-br from-[#2563eb] to-[#8b3fd1] px-6 py-3.5 text-sm font-semibold shadow-[0_12px_35px_rgba(37,99,235,.28)] transition hover:-translate-y-0.5">
              Start guided research <ArrowUpRight size={16} className="transition group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
            </button>
            <span className="flex items-center gap-2 rounded-full border border-white/15 px-5 py-3.5 text-sm text-white/72"><ShieldCheck size={16} /> Human review enabled</span>
          </motion.div>
        </div>
        <motion.div initial={{ opacity: 0, scale: .96, y: 20 }} animate={{ opacity: 1, scale: 1, y: 0 }} transition={{ delay: .18, duration: .8, ease }} className="relative min-h-[470px] overflow-hidden rounded-[24px] border border-white/10 bg-white text-[#0f172a] soft-shadow">
          <div className="node-grid absolute inset-0 opacity-45" />
          <div className="relative flex min-h-[470px] flex-col justify-between p-7 md:p-10">
            <div className="flex items-center justify-between"><span className="micro-label text-[#2563eb]">Research coach</span><span className="rounded-full bg-[#eff6ff] px-3 py-1 text-xs font-semibold text-[#2563eb]">Guided practice</span></div>
            <CoachPreview onEnter={onEnter} />
            <div className="flex items-center justify-between border-t border-[#0f172a]/10 pt-5 text-xs">
              <div><b className="block text-sm">Learn by doing</b><span className="text-[#64748b]">Agent-guided synthetic case</span></div>
              <span className="rounded-full bg-[#f0fdf4] px-3 py-1.5 font-semibold text-[#16a34a]">Researcher in control</span>
            </div>
          </div>
        </motion.div>
      </div>
    </motion.section>
  );
}

function CoachPreview({ onEnter }: { onEnter: () => void }) {
  return <div className="my-7 overflow-hidden rounded-2xl border border-[#0f172a]/10 bg-white shadow-[0_16px_45px_rgba(15,23,42,.07)]">
    <div className="flex items-center justify-between border-b border-[#0f172a]/10 bg-[#f8fafc] px-5 py-4">
      <div className="flex items-center gap-3"><span className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-[#2563eb] to-[#8b3fd1] text-white"><Bot size={18} /><motion.span animate={{ scale: [1, 1.35, 1], opacity: [1, .45, 1] }} transition={{ duration: 2, repeat: Infinity }} className="absolute -right-1 -top-1 h-3 w-3 rounded-full border-2 border-white bg-[#22c55e]" /></span><div><p className="text-xs font-bold">NTO Research Agent</p><p className="mt-1 text-[11px] text-[#16a34a]">Active · guiding your next step</p></div></div>
      <span className="rounded-full bg-[#eef2ff] px-2.5 py-1 text-[10px] font-bold text-[#4f46e5]">STEP 2 / 6</span>
    </div>

    <div className="p-5">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: .35 }} className="rounded-2xl rounded-tl-md bg-[#eff6ff] p-4">
        <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[.12em] text-[#2563eb]"><Sparkles size={12} /> Your next lesson</div>
        <p className="mt-2 text-sm font-bold leading-5">Let’s locate and validate the recorded Notice of Commencement.</p>
        <p className="mt-2 text-[11px] leading-5 text-[#475569]">I’ll show you what matters. You inspect the official record and confirm the evidence before we continue.</p>
      </motion.div>

      <div className="mt-4 grid grid-cols-[1fr_auto_1fr_auto_1fr] items-center gap-2">
        <AgentLesson icon={<FileSearch size={14} />} number="01" label="Open record" />
        <ArrowRight size={12} className="text-[#94a3b8]" />
        <AgentLesson icon={<Sparkles size={14} />} number="02" label="Learn checks" active />
        <ArrowRight size={12} className="text-[#94a3b8]" />
        <AgentLesson icon={<Check size={14} />} number="03" label="You verify" />
      </div>

      <motion.button type="button" onClick={onEnter} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: .65 }} className="mt-4 flex w-full items-center justify-between rounded-xl border border-[#2563eb]/20 bg-white px-4 py-3 text-left transition hover:border-[#2563eb]/40 hover:bg-[#f8fafc] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563eb]">
        <span><b className="block text-xs">Show me what to check</b><span className="mt-1 block text-[10px] text-[#64748b]">Dates · parties · legal description · expiration</span></span><span className="flex h-8 w-8 items-center justify-center rounded-full bg-[#0f172a] text-white"><ArrowRight size={13} /></span>
      </motion.button>
    </div>
  </div>;
}

function AgentLesson({ icon, number, label, active = false }: { icon: React.ReactNode; number: string; label: string; active?: boolean }) {
  return <div className={`rounded-xl border p-2.5 ${active ? "border-[#2563eb]/25 bg-[#eff6ff]" : "border-[#0f172a]/10 bg-[#f8fafc]"}`}><div className={`flex h-7 w-7 items-center justify-center rounded-lg ${active ? "bg-[#2563eb] text-white" : "bg-white text-[#64748b]"}`}>{icon}</div><p className="mt-2 text-[9px] font-bold text-[#94a3b8]">{number}</p><p className="mt-0.5 whitespace-nowrap text-[10px] font-bold">{label}</p></div>;
}
