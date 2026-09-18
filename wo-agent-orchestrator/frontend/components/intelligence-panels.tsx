"use client";

import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Clock3,
  Database,
  Fingerprint,
  GitBranch,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

import type {
  CorrectionOverlay,
  ExecutionResponse,
} from "@/types/workflow";

function displayValue(value: unknown) {
  if (value === null || value === undefined) return "—";
  if (typeof value === "string") return value;
  if (
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return String(value);
  }

  return JSON.stringify(value);
}

function extractCount(
  value: unknown,
  keys: string[],
): number {
  if (!value || typeof value !== "object") return 0;

  const record = value as Record<string, unknown>;

  for (const key of keys) {
    const candidate = record[key];

    if (Array.isArray(candidate)) {
      return candidate.length;
    }
  }

  return 0;
}

export function IntelligencePanels({
  execution,
}: {
  execution: ExecutionResponse | null;
}) {
  const result = execution?.result;
  const agentResults = result?.results;

  const evidenceCount = extractCount(
    agentResults?.evidence,
    [
      "evidence_facts",
      "evidence_references",
      "evidence",
    ],
  );

  const conflictCount = extractCount(
    agentResults?.discrepancy,
    [
      "conflicts",
      "material_conflicts",
      "potential_conflicts",
    ],
  );

  const corrections =
    result?.correction_overlay ?? [];

  const complete =
    execution?.status === "COMPLETE_RECOMMENDED";

  const humanReview =
    execution?.status === "HUMAN_REVIEW";

  return (
    <div className="intelligence-stack">
      <section className="hero-metrics panel">
        <div className="metric-primary">
          <div className="eyebrow">QC outcome</div>

          <div className="outcome-row">
            <div>
              <h2>
                {complete
                  ? "Complete recommended"
                  : humanReview
                    ? "Human review"
                    : execution?.status === "RUNNING"
                      ? "Analysis running"
                      : execution?.status === "FAILED"
                        ? "Execution failed"
                        : "Ready for analysis"}
              </h2>

              <p>
                {complete
                  ? "Deterministic gates satisfied. Final action remains externally controlled."
                  : humanReview
                    ? "Material ambiguity requires operator review."
                    : "Select a synthetic Work Order and run intelligence."}
              </p>
            </div>

            <div
              className={[
                "outcome-emblem",
                complete ? "outcome-success" : "",
                humanReview ? "outcome-warning" : "",
              ].join(" ")}
            >
              {complete ? (
                <CheckCircle2 />
              ) : humanReview ? (
                <AlertTriangle />
              ) : (
                <Sparkles />
              )}
            </div>
          </div>
        </div>

        <div className="metric-grid">
          <Metric
            label="Human review"
            value={
              execution
                ? execution.human_review_required
                  ? "YES"
                  : "NO"
                : "—"
            }
            icon={<ShieldCheck size={17} />}
          />

          <Metric
            label="Corrections"
            value={String(
              execution?.correction_attempts ?? 0,
            ).padStart(2, "0")}
            icon={<GitBranch size={17} />}
          />

          <Metric
            label="Evidence"
            value={String(evidenceCount).padStart(2, "0")}
            icon={<Database size={17} />}
          />

          <Metric
            label="Conflicts"
            value={String(conflictCount).padStart(2, "0")}
            icon={<AlertTriangle size={17} />}
          />
        </div>
      </section>

      <section className="two-column-grid">
        <div className="panel detail-panel">
          <SectionHeader
            eyebrow="Evidence intelligence"
            title="Provenance"
            icon={<Fingerprint size={18} />}
          />

          <div className="provenance-flow">
            <SourceNode label="Customer claim" />
            <SourceNode label="Documentary evidence" />
            <SourceNode label="Confirmation" />

            <div className="provenance-target">
              <div className="target-pulse" />
              <div>
                <span>Resolution layer</span>
                <strong>
                  Match · Missing · Conflict
                </strong>
              </div>
            </div>
          </div>

          <p className="panel-footnote">
            Source claims remain distinct from researched
            evidence and resolved workflow truth.
          </p>
        </div>

        <div className="panel detail-panel">
          <SectionHeader
            eyebrow="Decision intelligence"
            title="Discrepancy engine"
            icon={<GitBranch size={18} />}
          />

          <div className="signal-list">
            <Signal
              label="Matches"
              value={extractCount(
                agentResults?.discrepancy,
                ["matches"],
              )}
            />

            <Signal
              label="Conflicts"
              value={conflictCount}
              warning={conflictCount > 0}
            />

            <Signal
              label="Missing"
              value={extractCount(
                agentResults?.discrepancy,
                ["missing_items"],
              )}
            />

            <Signal
              label="Unverified"
              value={extractCount(
                agentResults?.discrepancy,
                ["unverified_items"],
              )}
            />
          </div>
        </div>
      </section>

      <CorrectionPanel corrections={corrections} />

      <section className="panel observability-panel">
        <SectionHeader
          eyebrow="Execution telemetry"
          title="Operational trace"
          icon={<Clock3 size={18} />}
        />

        <div className="trace-grid">
          <TraceItem
            label="Execution"
            value={
              execution?.execution_id
                ? execution.execution_id.slice(0, 12)
                : "Not started"
            }
          />

          <TraceItem
            label="Work Order"
            value={execution?.wo_id ?? "—"}
          />

          <TraceItem
            label="Current stage"
            value={
              execution?.current_stage ??
              execution?.status ??
              "IDLE"
            }
          />

          <TraceItem
            label="Correction attempt"
            value={String(
              execution?.correction_attempts ?? 0,
            )}
          />
        </div>
      </section>
    </div>
  );
}

function Metric({
  label,
  value,
  icon,
}: {
  label: string;
  value: string;
  icon: React.ReactNode;
}) {
  return (
    <div className="metric-card">
      <div className="metric-label">
        {icon}
        <span>{label}</span>
      </div>

      <strong>{value}</strong>
    </div>
  );
}

function SectionHeader({
  eyebrow,
  title,
  icon,
}: {
  eyebrow: string;
  title: string;
  icon: React.ReactNode;
}) {
  return (
    <div className="section-heading">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h3>{title}</h3>
      </div>

      <div className="section-icon">{icon}</div>
    </div>
  );
}

function SourceNode({
  label,
}: {
  label: string;
}) {
  return (
    <div className="source-node">
      <span>{label}</span>
      <ArrowRight size={15} />
    </div>
  );
}

function Signal({
  label,
  value,
  warning = false,
}: {
  label: string;
  value: number;
  warning?: boolean;
}) {
  return (
    <div className="signal-row">
      <div>
        <span
          className={
            warning
              ? "signal-dot signal-dot-warning"
              : "signal-dot"
          }
        />

        {label}
      </div>

      <strong>{String(value).padStart(2, "0")}</strong>
    </div>
  );
}

function CorrectionPanel({
  corrections,
}: {
  corrections: CorrectionOverlay[];
}) {
  return (
    <section className="panel correction-panel">
      <SectionHeader
        eyebrow="Resolution layer"
        title="Correction intelligence"
        icon={<Sparkles size={18} />}
      />

      {corrections.length === 0 ? (
        <div className="empty-correction">
          <GitBranch size={22} />

          <div>
            <strong>No correction overlay</strong>
            <span>
              Immutable source values remain untouched.
            </span>
          </div>
        </div>
      ) : (
        <div className="correction-list">
          {corrections.map((correction, index) => (
            <div
              className="correction-row"
              key={`${correction.field}-${index}`}
            >
              <div className="correction-index">
                {String(index + 1).padStart(2, "0")}
              </div>

              <div className="correction-field">
                <span>Field</span>
                <strong>
                  {correction.field ?? "Unknown"}
                </strong>
              </div>

              <div className="correction-value">
                <span>Original</span>
                <strong>
                  {displayValue(
                    correction.original_value,
                  )}
                </strong>
              </div>

              <ArrowRight
                size={18}
                className="correction-arrow"
              />

              <div className="correction-value proposed">
                <span>Proposed resolution</span>
                <strong>
                  {displayValue(
                    correction.proposed_value,
                  )}
                </strong>
              </div>

              <div className="correction-status">
                {correction.resolution_status ??
                  "PROPOSED"}
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

function TraceItem({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="trace-item">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}