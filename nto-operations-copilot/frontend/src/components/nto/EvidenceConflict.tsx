import { ArrowRight, Building2, FileCheck2, ShieldAlert } from "lucide-react";

const steps = [
  ["01", "Preserve conflict", "Do not overwrite either source."],
  ["02", "CC outreach", "Route to the approved coordination path."],
  ["03", "3 calls + 3 emails", "Document each contact attempt."],
  ["04", "Customer review", "Return unresolved evidence to the customer."],
  ["05", "Escalate", "Apply human escalation when required."],
];

export default function EvidenceConflict() {
  return <section className="overflow-hidden rounded-[22px] bg-[#0f172a] text-white shadow-[0_24px_70px_rgba(15,23,42,.16)]">
    <div className="flex flex-col gap-4 border-b border-white/10 p-6 md:flex-row md:items-center md:justify-between">
      <div><p className="micro-label text-[#63b3ff]">Material discrepancy</p><h3 className="mt-2 text-2xl font-bold tracking-[-.035em]">General contractor conflict</h3></div>
      <span className="inline-flex w-fit items-center gap-2 rounded-full bg-[#8b3fd1]/20 px-3 py-1.5 text-xs font-semibold text-[#d8b4fe]"><ShieldAlert size={14} /> Human resolution required</span>
    </div>
    <div className="grid gap-px bg-white/10 md:grid-cols-[1fr_auto_1fr]">
      <EvidenceSide icon={<Building2 size={18} />} label="Customer claim" name="Horizon Builders" source="Customer intake · 12 Sep 2026" tone="blue" />
      <div className="flex items-center justify-center bg-[#0f172a] px-4 py-3"><span className="rounded-full border border-white/15 bg-white/5 px-3 py-1 text-[10px] font-bold tracking-[.14em] text-white/55">DOES NOT MATCH</span></div>
      <EvidenceSide icon={<FileCheck2 size={18} />} label="Recorded NOC" name="Summit Construction" source="Official record · OR-482913" tone="violet" />
    </div>
    <div className="p-6"><div className="mb-4 flex items-center justify-between"><p className="micro-label text-white/45">Approved CC-first path</p><span className="text-xs text-white/40">Procedure preview</span></div>
      <div className="grid gap-2 md:grid-cols-5">{steps.map(([n,title,copy], i) => <div key={n} className="relative rounded-xl border border-white/10 bg-white/[.035] p-3.5">{i < steps.length - 1 && <ArrowRight size={13} className="absolute -right-2.5 top-5 z-10 hidden text-[#63b3ff] md:block" />}<span className="text-[10px] font-bold text-[#63b3ff]">{n}</span><p className="mt-2 text-xs font-semibold">{title}</p><p className="mt-1 text-[11px] leading-4 text-white/42">{copy}</p></div>)}</div>
    </div>
  </section>;
}

function EvidenceSide({ icon, label, name, source, tone }: { icon: React.ReactNode; label: string; name: string; source: string; tone: "blue" | "violet" }) {
  return <div className="bg-[#0f172a] p-6"><div className={`flex h-10 w-10 items-center justify-center rounded-full ${tone === "blue" ? "bg-[#2563eb]/20 text-[#63b3ff]" : "bg-[#8b3fd1]/20 text-[#d8b4fe]"}`}>{icon}</div><p className="mt-6 text-xs font-semibold text-white/45">{label}</p><p className="mt-1 text-xl font-bold tracking-[-.03em]">{name}</p><p className="mt-4 text-xs text-white/35">{source}</p></div>;
}
