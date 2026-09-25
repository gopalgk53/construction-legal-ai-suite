export type EvidenceState =
  | "CONFIRMED"
  | "UNVERIFIED"
  | "CONFLICTING"
  | "MISSING"
  | "UNRESOLVED";

export interface DemoScenario {
  id: string;
  index: string;
  title: string;
  eyebrow: string;
  description: string;
  status: EvidenceState;
  workOrder: string;
}

export const demoScenarios: DemoScenario[] = [
  {
    id: "gc-conflict",
    index: "01",
    title: "GC conflict",
    eyebrow: "Evidence review",
    description: "Customer intake and the recorded NOC identify different general contractors.",
    status: "CONFLICTING",
    workOrder: "SYN-WO-000111",
  },
  {
    id: "missing-noc",
    index: "02",
    title: "Missing NOC",
    eyebrow: "Research",
    description: "Property data is available, but an applicable Notice of Commencement is not located.",
    status: "MISSING",
    workOrder: "SYN-WO-000083",
  },
  {
    id: "owner-builder",
    index: "03",
    title: "Owner / Builder",
    eyebrow: "PARTICIPANTS",
    description:
      "Guide participant-role research when ownership and contractor roles overlap.",
    status: "UNRESOLVED",
    workOrder: "SYN-WO-000104",
  },
  {
    id: "public-bond",
    index: "04",
    title: "Public + Bond",
    eyebrow: "PUBLIC PROJECT",
    description:
      "Guide bond research and participant verification for a public Work Order.",
    status: "UNVERIFIED",
    workOrder: "SYN-WO-000126",
  },
  {
    id: "qc-review",
    index: "05",
    title: "QC Review",
    eyebrow: "QUALITY CONTROL",
    description:
      "Review a completed notice against approved evidence and operational procedures.",
    status: "CONFIRMED",
    workOrder: "SYN-WO-000132",
  },
];
