"use client";

import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import {
  Activity,
  ArrowUpRight,
  Bot,
  ChevronDown,
  Command,
  Play,
  RotateCw,
  ShieldCheck,
} from "lucide-react";

import { getExecution, startWorkflow } from "@/lib/api";

import type {
  ExecutionResponse,
  ExecutionStatus,
} from "@/types/workflow";

import { IntelligencePanels } from "./intelligence-panels";
import { WorkflowRail } from "./workflow-rail";

const scenarios = [
  {
    woId: "SYN-WO-000001",
    label: "Clean path",
    description: "No material conflict",
    badge: "STRAIGHT-THROUGH",
    title: "Clean / Verified Workflow",
    purpose:
      "Demonstrates autonomous processing when customer claims and available documentary evidence contain no material conflict requiring correction or human intervention.",
    journey: [
      "Intake",
      "Research",
      "Evidence",
      "Discrepancy",
      "QC",
      "Complete",
    ],
    safety:
      "Customer claims remain separate from researched evidence. Unverified information alone does not create a failure, BTP, or human-review requirement.",
    expectedOutcome: "COMPLETE RECOMMENDED",
    expectedDetail: "Human Review NO · Corrections 0",
  },
  {
    woId: "SYN-WO-000116",
    label: "Correction path",
    description: "Customer ↔ evidence mismatch",
    badge: "CONTROLLED CORRECTION",
    title: "Evidence-Supported Correction",
    purpose:
      "Demonstrates how the platform handles a genuine mismatch between a customer-provided participant value and consistent documentary evidence.",
    journey: [
      "Intake",
      "Research",
      "Evidence",
      "Discrepancy",
      "BTP",
      "Correction",
      "QC Re-review",
      "Complete",
    ],
    safety:
      "The original customer claim remains immutable. Research proposes an evidence-supported overlay, QC independently verifies it, and deterministic Python owns final acceptance.",
    expectedOutcome: "COMPLETE RECOMMENDED",
    expectedDetail: "Human Review NO · Corrections ≥ 1",
  },
  {
    woId: "SYN-WO-000111",
    label: "Human review",
    description: "Documentary evidence conflict",
    badge: "SAFETY ESCALATION",
    title: "Unresolved Documentary Conflict",
    purpose:
      "Demonstrates the safety boundary when documentary sources disagree and the system cannot safely determine which value should control.",
    journey: [
      "Intake",
      "Research",
      "Evidence",
      "Discrepancy",
      "QC",
      "Human Review",
    ],
    safety:
      "Conflicting documentary evidence is preserved. The system does not arbitrarily choose a source, invent a correction, or silently overwrite evidence.",
    expectedOutcome: "HUMAN REVIEW",
    expectedDetail: "Human Review YES · Corrections 0",
  },
];

export function IntelligenceConsole() {
  const [selectedWo, setSelectedWo] =
    useState("SYN-WO-000001");

  const [execution, setExecution] =
    useState<ExecutionResponse | null>(null);

  const [status, setStatus] =
    useState<ExecutionStatus>("IDLE");

  const [error, setError] =
    useState<string | null>(null);

  const pollTimer = useRef<ReturnType<typeof setTimeout> | null>(
    null,
  );

  useEffect(() => {
    return () => {
      if (pollTimer.current) {
        clearTimeout(pollTimer.current);
      }
    };
  }, []);

  async function pollExecution(
    executionId: string,
  ): Promise<void> {
    try {
      const next = await getExecution(executionId);

      setExecution(next);
      setStatus(next.status);

      if (next.status === "RUNNING") {
        pollTimer.current = setTimeout(
          () => void pollExecution(executionId),
          1800,
        );
      }
    } catch {
      setStatus("FAILED");
      setError(
        "Execution status could not be retrieved.",
      );
    }
  }

  async function runIntelligence() {
    if (pollTimer.current) {
      clearTimeout(pollTimer.current);
    }

    setExecution(null);
    setStatus("RUNNING");
    setError(null);

    try {
      const started = await startWorkflow(selectedWo);

      setStatus(started.status);

      await pollExecution(started.execution_id);
    } catch {
      setStatus("FAILED");
      setError(
        "The cloud intelligence service is unavailable.",
      );
    }
  }

  const running = status === "RUNNING";

  const complete =
    status === "COMPLETE_RECOMMENDED";

  const humanReview =
    status === "HUMAN_REVIEW";

  const selectedScenario =
    scenarios.find(
      (scenario) => scenario.woId === selectedWo,
    ) ?? scenarios[0];

  return (
    <main className="console-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">
            <Command size={18} />
          </div>

          <div>
            <strong>WO INTELLIGENCE</strong>
            <span>
              Autonomous Operations Platform
            </span>
          </div>
        </div>

        <div className="topbar-right">
          <div className="environment-chip">
            <span className="status-light" />
            CLOUD SYSTEM
          </div>

          <div className="model-chip">
            <Bot size={14} />
            MULTI-AGENT
          </div>
        </div>
      </header>

      <section className="command-hero">
        <div className="hero-copy">
          <div className="eyebrow">
            Construction payment protection
          </div>

          <h1>
            Autonomous Work Order
            <span> Intelligence.</span>
          </h1>

          <p>
            Evidence-aware multi-agent reasoning with
            deterministic operational control, provenance,
            QC and human review.
          </p>
        </div>

        <div className="hero-system">
        <Activity size={16} />

        <div>
            <span>Orchestration</span>
            <strong>
            Deterministic control plane
            </strong>
        </div>
        </div>
      </section>

      <section className="scenario-command panel">
        <div className="scenario-header">
          <div>
            <div className="eyebrow">
              Synthetic demonstration
            </div>

            <h2>Select Work Order</h2>
          </div>

          <ShieldCheck size={20} />
        </div>

        <div className="scenario-controls">
          <div className="scenario-selector">
            {scenarios.map((scenario) => (
              <button
                key={scenario.woId}
                type="button"
                onClick={() =>
                  !running &&
                  setSelectedWo(scenario.woId)
                }
                className={
                  selectedWo === scenario.woId
                    ? "scenario-option scenario-option-active"
                    : "scenario-option"
                }
              >
                <div className="scenario-radio">
                  <span />
                </div>

                <div>
                  <strong>{scenario.woId}</strong>
                  <span>
                    {scenario.label} ·{" "}
                    {scenario.description}
                  </span>
                </div>
              </button>
            ))}
          </div>

          <motion.button
            type="button"
            className="run-button"
            disabled={running}
            onClick={() =>
              void runIntelligence()
            }
            whileHover={
              running ? {} : { y: -2 }
            }
            whileTap={
              running ? {} : { scale: 0.985 }
            }
            transition={{
              type: "spring",
              stiffness: 200,
              damping: 25,
            }}
          >
            {running ? (
              <RotateCw
                size={17}
                className="spin"
              />
            ) : (
              <Play
                size={17}
                fill="currentColor"
              />
            )}

            <span>
              {running
                ? "Running intelligence"
                : "Run intelligence"}
            </span>

            <ChevronDown
              size={15}
              className="run-chevron"
            />
          </motion.button>
        </div>
      </section>

      {/* Scenario Intelligence */}

      <AnimatePresence mode="wait">
        <motion.section
          key={selectedScenario.woId}
          className="scenario-intelligence panel"
          initial={{
            opacity: 0,
            y: 10,
          }}
          animate={{
            opacity: 1,
            y: 0,
          }}
          exit={{
            opacity: 0,
            y: -8,
          }}
          transition={{
            type: "spring",
            stiffness: 200,
            damping: 25,
          }}
        >
          <div className="scenario-intelligence-head">
            <div>
              <div className="eyebrow">
                Scenario intelligence
              </div>

              <h2>
                {selectedScenario.title}
              </h2>

              <p>
                {selectedScenario.purpose}
              </p>
            </div>

            <div className="scenario-intelligence-badge">
              {selectedScenario.badge}
            </div>
          </div>

          <div className="scenario-intelligence-grid">
            <div className="scenario-intelligence-block">
              <span className="scenario-block-label">
                Expected agent journey
              </span>

              <div className="scenario-journey">
                {selectedScenario.journey.map(
                  (stage, index) => (
                    <div
                      key={`${selectedScenario.woId}-${stage}`}
                      className="scenario-journey-item"
                    >
                      <span>
                        {stage}
                      </span>

                      {index <
                        selectedScenario.journey.length -
                          1 && (
                        <ArrowUpRight
                          size={13}
                          className="scenario-journey-arrow"
                        />
                      )}
                    </div>
                  ),
                )}
              </div>
            </div>

            <div className="scenario-intelligence-block">
              <span className="scenario-block-label">
                Safety behavior
              </span>

              <p>
                {selectedScenario.safety}
              </p>
            </div>

            <div className="scenario-intelligence-block scenario-outcome-block">
              <span className="scenario-block-label">
                Expected outcome
              </span>

              <strong>
                {selectedScenario.expectedOutcome}
              </strong>

              <small>
                {selectedScenario.expectedDetail}
              </small>
            </div>
          </div>
        </motion.section>
      </AnimatePresence>

      {/* Runtime Error */}

      <AnimatePresence>
        {error && (
          <motion.div
            className="error-banner"
            initial={{
              opacity: 0,
              y: -8,
            }}
            animate={{
              opacity: 1,
              y: 0,
            }}
            exit={{
              opacity: 0,
            }}
          >
            {error}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Live Workflow Results */}

      <section className="workspace-grid">
        <WorkflowRail
          running={running}
          currentStage={
            execution?.current_stage ??
            execution?.status
          }
          completed={complete}
          humanReview={humanReview}
        />

        <IntelligencePanels
          execution={execution}
        />
      </section>

      <footer className="console-footer">
        <div>
          <span className="footer-dot" />
          SYNTHETIC DATA ENVIRONMENT
        </div>

        <div>
          FOUNDRY AGENTS
          <span>×</span>
          DETERMINISTIC PYTHON
          <span>×</span>
          MCP
          <span>×</span>
          CLOUD EVIDENCE
        </div>
      </footer>
    </main>
  );
}