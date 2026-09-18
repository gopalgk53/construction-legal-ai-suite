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

import {
  getExecution,
  startWorkflow,
} from "@/lib/api";

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
    description: "Verified workflow",
  },
  {
    woId: "SYN-WO-000116",
    label: "Correction",
    description: "BTP → correction → QC",
  },
  {
    woId: "SYN-WO-000111",
    label: "Human review",
    description: "Evidence conflict",
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

  const pollTimer = useRef<ReturnType<
    typeof setTimeout
  > | null>(null);


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
      const started =
        await startWorkflow(selectedWo);

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

          <ArrowUpRight size={16} />
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
              <Play size={17} fill="currentColor" />
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


      <AnimatePresence>
        {error && (
          <motion.div
            className="error-banner"
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
          >
            {error}
          </motion.div>
        )}
      </AnimatePresence>


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