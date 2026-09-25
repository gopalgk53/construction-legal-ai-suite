"use client";

import { motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { ArrowRight, BookOpen, Check, ChevronDown, CircleHelp, ClipboardCheck, FileSearch, Lightbulb, MessageCircleQuestion, Search, Send, UserRoundCheck } from "lucide-react";
import { demoScenarios } from "@/data/demoScenarios";
import EvidenceConflict from "./EvidenceConflict";
import ScenarioRail from "./ScenarioRail";

const researchSteps = [
  { label: "Understand request", icon: BookOpen },
  { label: "Property", icon: Search },
  { label: "Recorded NOC", icon: FileSearch },
  { label: "Participants", icon: UserRoundCheck },
  { label: "Prepare notice", icon: ClipboardCheck },
  { label: "Quality check", icon: Check },
];

interface WorkOrderIntake {
  customer_name?: string | null;
  job_name?: string | null;
  job_address?: string | { street?: string | null; city?: string | null; state?: string | null; zip?: string | null } | null;
  project_type_claimed?: string | null;
  type_of_work?: string | null;
  first_day_on_job?: string | null;
  job_amount?: number | null;
  owner_claimed?: string | null;
  general_contractor_claimed?: string | null;
  provided_references?: Record<string, string | null>;
}

export default function OperationsWorkspace() {
  const [scenarioId, setScenarioId] = useState("gc-conflict");
  const [step, setStep] = useState(2);
  const [coachOpen, setCoachOpen] = useState(true);
  const [workOrder, setWorkOrder] = useState("SYN-WO-000111");
  const [workOrderLoading, setWorkOrderLoading] = useState(false);
  const [workOrderError, setWorkOrderError] = useState("");
  const [workOrderStatus, setWorkOrderStatus] = useState("Example");
  const [workOrderIntake, setWorkOrderIntake] = useState<WorkOrderIntake | null>(null);
  const scenario = demoScenarios.find(item => item.id === scenarioId) ?? demoScenarios[0];
  const isCustomWorkOrder = workOrder !== scenario.workOrder;

  const loadWorkOrder = async (value: string) => {
    setWorkOrderLoading(true);
    setWorkOrderError("");
    try {
      const baseUrl = process.env.NEXT_PUBLIC_NTO_API_BASE_URL || "http://localhost:8000";
      const response = await fetch(`${baseUrl}/api/work-orders/lookup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ work_order: value }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || "The work order could not be loaded.");
      setWorkOrder(payload.work_order || value);
      setWorkOrderStatus(payload.status || "Retrieved");
      setWorkOrderIntake(payload.intake || null);
      setStep(0);
    } catch (caught) {
      setWorkOrderError(caught instanceof Error ? caught.message : "The work order could not be loaded.");
    } finally {
      setWorkOrderLoading(false);
    }
  };

  return <motion.section initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .55, ease: [0.16, 1, .3, 1] }} className="h-screen overflow-hidden bg-[#f8fafc]">
    <header className="relative z-30 flex h-[73px] shrink-0 items-center justify-between border-b border-[#0f172a]/10 bg-white/95 px-5 backdrop-blur-xl md:px-7">
      <div className="flex items-center gap-3"><span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-[#2563eb] to-[#8b3fd1] text-sm font-bold text-white">N</span><div><p className="text-sm font-bold tracking-[-.02em]">NTO Research Coach</p><p className="text-[10px] font-semibold text-[#64748b]">Learn the process · get unstuck</p></div></div>
      <div className="hidden items-center gap-2 rounded-full bg-[#f0fdf4] px-4 py-2 text-xs font-semibold text-[#166534] sm:flex"><span className="h-2 w-2 rounded-full bg-[#22c55e]" /> Foundry agent · WO data connected</div>
      <button onClick={() => setCoachOpen(value => !value)} className={`flex items-center gap-2 rounded-full border px-4 py-2 text-xs font-bold transition ${coachOpen ? "border-[#2563eb]/25 bg-[#eff6ff] text-[#2563eb]" : "border-[#0f172a]/10 bg-white text-[#475569]"}`}><MessageCircleQuestion size={14} /> {coachOpen ? "Coach open" : "Open coach"} <ChevronDown size={13} /></button>
    </header>

    <div className="grid h-[calc(100vh-73px)] overflow-hidden lg:grid-cols-[280px_minmax(0,1fr)]"><ScenarioRail activeId={scenarioId} workOrder={workOrder} loading={workOrderLoading} loadError={workOrderError} loadedStatus={workOrderStatus} onLoadWorkOrder={loadWorkOrder} onSelect={id => { const selected = demoScenarios.find(item => item.id === id); setScenarioId(id); setWorkOrder(selected?.workOrder ?? workOrder); setWorkOrderStatus("Example"); setWorkOrderIntake(null); setWorkOrderError(""); setStep(id === "gc-conflict" ? 2 : 0); }} />
      <main className="h-full min-w-0 overflow-hidden p-5 md:p-6 xl:px-7 xl:py-6"><div className={`mx-auto grid h-full w-full max-w-[1600px] min-h-0 gap-6 ${coachOpen ? "min-[1280px]:grid-cols-[minmax(0,1fr)_minmax(460px,520px)]" : ""}`}>
        <div className="flex min-h-0 min-w-0 flex-col">
          <div className="shrink-0 pb-4"><p className="micro-label text-[#2563eb]">Active work order · {workOrder}</p><div className="mt-1.5 flex flex-col gap-2 md:flex-row md:items-end md:justify-between"><div><h1 className="text-3xl font-bold tracking-[-.045em]">{isCustomWorkOrder ? "Work order research" : scenario.title}</h1><p className="mt-1.5 max-w-2xl text-xs leading-5 text-[#64748b]">Follow the guided process or ask the coach about the issue blocking your research.</p></div><span className="w-fit rounded-full bg-[#eef2ff] px-3 py-1.5 text-[10px] font-bold text-[#4f46e5]">Step {step + 1} of {researchSteps.length}</span></div></div>

          <div className="shrink-0"><ProcessStepper active={step} onSelect={setStep} /></div>

          <div className="mt-4 min-h-0 min-w-0 flex-1 space-y-4 overflow-y-auto pb-6 pr-1">
            {workOrderIntake && <WorkOrderSnapshot intake={workOrderIntake} status={workOrderStatus} />}
            <CurrentTask step={step} scenarioId={scenarioId} onNext={() => setStep(Math.min(step + 1, researchSteps.length - 1))} />
            {!isCustomWorkOrder && scenarioId === "gc-conflict" && step === 2 && <EvidenceConflict />}
          </div>
        </div>
        {coachOpen && <CoachPanel step={step} scenarioId={scenarioId} workOrder={workOrder} />}
      </div></main>
    </div>
  </motion.section>;
}

function WorkOrderSnapshot({ intake, status }: { intake: WorkOrderIntake; status: string }) {
  const address = typeof intake.job_address === "string" ? intake.job_address : intake.job_address ? [intake.job_address.street, intake.job_address.city, intake.job_address.state, intake.job_address.zip].filter(Boolean).join(", ") : "Not provided";
  const references = intake.provided_references || {};
  const referenceItems = [
    ["NOC", references.noc_reference],
    ["Bond", references.bond_number],
    ["Permit", references.permit_number],
    ["Parcel", references.parcel_or_folio],
  ];
  return <section className="rounded-[22px] border border-[#2563eb]/15 bg-white p-5 shadow-[0_12px_35px_rgba(37,99,235,.07)] md:p-6">
    <div className="flex flex-wrap items-start justify-between gap-3"><div><p className="micro-label text-[#2563eb]">Work order intake</p><h2 className="mt-2 text-lg font-bold tracking-[-.025em]">{intake.job_name || "Customer request"}</h2><p className="mt-1 text-xs text-[#64748b]">{address}</p></div><span className="rounded-full bg-[#f0fdf4] px-3 py-1.5 text-[10px] font-bold text-[#166534]">{status.replaceAll("_", " ")}</span></div>
    <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4"><SnapshotField label="Customer" value={intake.customer_name} /><SnapshotField label="Owner claimed" value={intake.owner_claimed} /><SnapshotField label="GC claimed" value={intake.general_contractor_claimed} /><SnapshotField label="Type of work" value={formatProjectType(intake.project_type_claimed)} /></div>
    <div className="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">{referenceItems.map(([label, value]) => <SnapshotField key={label} label={`${label} reference`} value={value} missingLabel="Not provided" />)}</div>
  </section>;
}

function formatProjectType(value?: string | null) {
  const types: Record<string, string> = {
    PRIVATE_RESIDENTIAL: "Private residential",
    PRIVATE_COMMERCIAL: "Private commercial",
    STATE_COUNTY: "State / county",
    TOWN_MUNICIPALITY: "State / county",
    FEDERAL: "Federal",
  };
  return value ? types[value] || value.replaceAll("_", " ").toLowerCase() : null;
}

function SnapshotField({ label, value, missingLabel = "Missing" }: { label: string; value?: string | number | null; missingLabel?: string }) {
  return <div className="rounded-2xl bg-[#f8fafc] px-4 py-3"><p className="text-[9px] font-bold uppercase tracking-[.12em] text-[#94a3b8]">{label}</p><p className={`mt-1.5 break-words text-xs font-semibold leading-5 ${value ? "text-[#0f172a]" : "text-[#c2410c]"}`}>{value || missingLabel}</p></div>;
}

function ProcessStepper({ active, onSelect }: { active: number; onSelect: (step: number) => void }) {
  return <div className="overflow-x-auto rounded-2xl border border-[#0f172a]/10 bg-white p-2 soft-shadow"><div className="flex min-w-[720px] items-center">{researchSteps.map(({ label, icon: Icon }, index) => <div key={label} className="flex flex-1 items-center last:flex-none"><button onClick={() => onSelect(index)} className={`group flex min-w-[98px] items-center gap-2 rounded-xl border px-2 py-1.5 text-left transition ${index === active ? "border-[#2563eb]/25 bg-gradient-to-br from-[#2563eb] to-[#6d4de5] shadow-[0_6px_16px_rgba(37,99,235,.2)]" : "border-transparent hover:border-[#0f172a]/10 hover:bg-[#f1f5f9]"}`}><span style={index === active ? { color: "white" } : undefined} className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-lg ${index < active ? "bg-[#dcfce7] text-[#16a34a]" : index === active ? "bg-white/15" : "bg-[#f1f5f9] text-[#64748b]"}`}>{index < active ? <Check size={13} /> : <Icon size={13} />}</span><span><b className={`block text-[9px] ${index === active ? "text-white/65" : "text-[#94a3b8]"}`}>0{index + 1}</b><span style={index === active ? { color: "white" } : undefined} className="whitespace-nowrap text-[10px] font-bold">{label}</span></span></button>{index < researchSteps.length - 1 && <span className={`mx-1 h-px min-w-2 flex-1 ${index < active ? "bg-[#86efac]" : "bg-[#cbd5e1]"}`} />}</div>)}</div></div>;
}

function CurrentTask({ step, scenarioId, onNext }: { step: number; scenarioId: string; onNext: () => void }) {
  const content = [
    ["Read before you research", "Identify the job, requested notice type, customer-provided parties and any missing inputs. Do not treat intake information as verified evidence."],
    ["Confirm the correct property", "Match the street address, parcel ID, legal description and current owner using the approved property source."],
    [scenarioId === "gc-conflict" ? "Compare the NOC with the customer claim" : "Find and validate the recorded NOC", "Open the official record. Check execution and recording dates, legal description, owner, contractor and expiration before using any field."],
    ["Build the participant record", "Separate customer claims from verified participants. Record the source for owner, general contractor, lender, surety and other required parties."],
    ["Prepare from verified fields", "Transfer only supported information into the notice. Preserve unresolved items and never silently choose between conflicting sources."],
    ["Run the final quality check", "Compare the draft against every approved source, confirm required fields and route unresolved material issues for review."],
  ][step];
  return <section className="rounded-[22px] border border-[#0f172a]/10 bg-white p-6 soft-shadow md:p-8"><div className="flex flex-col gap-6 md:flex-row md:items-start md:justify-between"><div><p className="micro-label text-[#2563eb]">Your task now</p><h2 className="mt-2 text-2xl font-bold tracking-[-.035em]">{content[0]}</h2><p className="mt-3 max-w-2xl text-sm leading-6 text-[#64748b]">{content[1]}</p></div><span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-[#eff6ff] text-[#2563eb]"><FileSearch size={20} /></span></div>
    <div className="mt-7 grid gap-3 md:grid-cols-3"><Checkpoint label="What to inspect" copy={step === 2 ? "Recording details, parties and dates" : "Source-specific required fields"} /><Checkpoint label="What to record" copy="Finding, source and confidence" /><Checkpoint label="Stop when" copy="Evidence is missing or conflicts" /></div>
    <div className="mt-7 flex flex-wrap items-center justify-between gap-3 border-t border-[#0f172a]/10 pt-5"><button className="flex items-center gap-2 rounded-full border border-[#2563eb]/20 bg-[#eff6ff] px-4 py-3 text-xs font-bold text-[#2563eb] transition hover:border-[#2563eb]/40"><CircleHelp size={15} /> I’m stuck—ask coach</button><button onClick={onNext} style={{ color: "white" }} className="flex items-center gap-2 rounded-full bg-gradient-to-r from-[#2563eb] to-[#7c3aed] px-5 py-3 text-xs font-bold shadow-[0_10px_24px_rgba(37,99,235,.24)] transition hover:-translate-y-0.5">Mark complete and continue <ArrowRight size={14} strokeWidth={2.5} /></button></div>
  </section>;
}

function Checkpoint({ label, copy }: { label: string; copy: string }) { return <div className="rounded-2xl bg-[#f8fafc] p-4"><p className="text-[10px] font-bold uppercase tracking-[.12em] text-[#94a3b8]">{label}</p><p className="mt-2 text-xs font-semibold leading-5">{copy}</p></div>; }

function CoachPanel({ step, scenarioId, workOrder }: { step: number; scenarioId: string; workOrder: string }) {
  const conflict = scenarioId === "gc-conflict" && step === 2;
  const [question, setQuestion] = useState("");
  const [submitted, setSubmitted] = useState("");
  const [answer, setAnswer] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const conversationRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    conversationRef.current?.scrollTo({ top: conversationRef.current.scrollHeight, behavior: "smooth" });
  }, [answer, loading, error]);
  const ask = async (value?: string) => {
    const next = (value ?? question).trim();
    if (!next) return;
    setSubmitted(next);
    setQuestion("");
    setAnswer("");
    setError("");
    setLoading(true);
    try {
      const baseUrl = process.env.NEXT_PUBLIC_NTO_API_BASE_URL || "http://localhost:8000";
      const response = await fetch(`${baseUrl}/api/coach`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ work_order: workOrder, question: next, current_step: researchSteps[step].label }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || "The coach is unavailable.");
      setAnswer(payload.answer);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The coach is unavailable.");
    } finally {
      setLoading(false);
    }
  };
  return <aside className="flex h-full min-h-0 flex-col overflow-hidden rounded-[22px] border border-[#0f172a]/10 bg-white shadow-[0_18px_50px_rgba(15,23,42,.08)]">
    <div className="shrink-0 border-b border-[#0f172a]/8 bg-white px-5 py-4"><div className="flex items-center gap-3"><span className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-[#2563eb] to-[#8b3fd1] text-white"><Lightbulb size={16} /></span><div className="min-w-0"><div className="flex items-center gap-2"><p className="text-sm font-bold">Research coach</p><span className="h-1.5 w-1.5 rounded-full bg-[#22c55e]" /></div><p className="mt-0.5 truncate text-[10px] text-[#64748b]">Using evidence from {workOrder}</p></div></div></div>
    <div className="flex min-h-0 flex-1 flex-col">
      <div ref={conversationRef} className="min-h-0 flex-1 overflow-y-auto bg-white px-6 py-6 [scrollbar-color:#cbd5e1_transparent] [scrollbar-width:thin]">
        {!submitted && <div className="flex h-full min-h-[160px] items-center justify-center"><div className="w-full max-w-[300px]"><span className="flex h-10 w-10 items-center justify-center rounded-full bg-[#f1f5f9] text-[#475569]"><MessageCircleQuestion size={18} /></span><h3 className="mt-4 text-base font-bold tracking-[-.02em]">How can I help with this WO?</h3><p className="mt-2 text-xs leading-5 text-[#64748b]">Describe what you found, what conflicts, or which research step is unclear.</p><div className="mt-5 space-y-2"><CoachPrompt text="Why is this a conflict?" onSelect={ask} /><CoachPrompt text="What should I verify?" onSelect={ask} />{conflict && <CoachPrompt text="Explain the CC-first path" onSelect={ask} />}</div></div></div>}
        {submitted && <div className="space-y-7"><div className="flex justify-end"><div className="max-w-[82%] rounded-[20px] bg-[#f1f5f9] px-4 py-3 text-sm leading-6 text-[#0f172a]">{submitted}</div></div>{loading && <div className="flex gap-3"><span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-[#2563eb] to-[#8b3fd1] text-white"><Lightbulb size={13} /></span><div className="pt-1 text-sm text-[#64748b]">Checking the work-order evidence<span className="animate-pulse">…</span></div></div>}{answer && <CoachAnswer answer={answer} />}{error && <div className="flex gap-3"><span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#fff7ed] text-[#c2410c]">!</span><div className="pt-1 text-sm leading-6 text-[#9a3412]"><b className="block">Connection needed</b>{error}</div></div>}</div>}
      </div>

      <div className="shrink-0 bg-white px-5 pb-5 pt-2">
        <div className="rounded-[22px] border border-[#0f172a]/10 bg-[#f7f7f8] p-3 shadow-sm focus-within:border-[#94a3b8]"><textarea value={question} disabled={loading} onChange={event => setQuestion(event.target.value)} onKeyDown={event => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); void ask(); } }} rows={2} className="max-h-24 min-h-10 w-full resize-none bg-transparent px-1 text-[13px] leading-5 outline-none placeholder:text-[#94a3b8] disabled:opacity-50" placeholder="Message the research coach…" /><div className="mt-1 flex items-center justify-between"><span className="text-[9px] text-[#94a3b8]">Enter to send · Shift+Enter for new line</span><button disabled={loading || !question.trim()} onClick={() => void ask()} aria-label="Ask research coach" style={{ color: "white" }} className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#0f172a] transition hover:bg-[#2563eb] disabled:bg-[#cbd5e1]"><Send size={13} /></button></div></div>
      </div>
    </div>
  </aside>;
}

function CoachPrompt({ text, onSelect }: { text: string; onSelect: (value: string) => void | Promise<void> }) { return <button onClick={() => void onSelect(text)} className="flex w-full items-center justify-between rounded-xl border border-[#0f172a]/10 px-3 py-2.5 text-left text-xs font-medium text-[#334155] transition hover:bg-[#f8fafc]"><span>{text}</span><ArrowRight size={12} className="text-[#94a3b8]" /></button>; }

function CoachAnswer({ answer }: { answer: string }) {
  const sections = answer.split(/\n(?=Answer|Why|Next step)\n?/).filter(Boolean);
  return <div className="flex gap-3"><span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-[#2563eb] to-[#8b3fd1] text-white"><Lightbulb size={13} /></span><div className="min-w-0 flex-1 pt-0.5"><b className="mb-4 block text-sm text-[#0f172a]">Research coach</b><div className="space-y-5">{sections.map((section, index) => { const [heading, ...body] = section.split("\n"); return <div key={`${heading}-${index}`}><p className="text-[10px] font-bold uppercase tracking-[.1em] text-[#64748b]">{heading}</p><p className="mt-1.5 text-sm leading-6 text-[#334155]">{body.join(" ")}</p></div>; })}</div></div></div>;
}
