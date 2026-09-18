"use client";

import { motion } from "motion/react";
import {
  Check,
  CircleDot,
  FileSearch,
  FlaskConical,
  Network,
  ScanSearch,
  ShieldCheck,
} from "lucide-react";

type WorkflowRailProps = {
  running: boolean;
  currentStage?: string | null;
  completed: boolean;
  humanReview: boolean;
};

const stages = [
  { name: "Intake", icon: ScanSearch },
  { name: "Research", icon: FileSearch },
  { name: "Evidence", icon: FlaskConical },
  { name: "Discrepancy", icon: Network },
  { name: "QC", icon: ShieldCheck },
];

function stageIndex(stage?: string | null) {
  if (!stage) return -1;

  const normalized = stage.toUpperCase();

  if (normalized.includes("INTAKE")) return 0;
  if (normalized.includes("RESEARCH")) return 1;
  if (normalized.includes("EVIDENCE")) return 2;
  if (normalized.includes("DISCREPANCY")) return 3;
  if (normalized.includes("QC")) return 4;

  if (
    normalized === "COMPLETE_RECOMMENDED" ||
    normalized === "HUMAN_REVIEW"
  ) {
    return stages.length;
  }

  return -1;
}

export function WorkflowRail({
  running,
  currentStage,
  completed,
  humanReview,
}: WorkflowRailProps) {
  const activeIndex = stageIndex(currentStage);

  return (
    <aside className="workflow-rail panel">
      <div className="eyebrow">Agent network</div>

      <div className="workflow-heading">
        <div>
          <h2>Execution graph</h2>
          <p>Deterministic orchestration</p>
        </div>

        <CircleDot
          size={17}
          className={running ? "pulse-icon" : ""}
        />
      </div>

      <div className="workflow-stages">
        {stages.map((stage, index) => {
          const Icon = stage.icon;

          const isPassed =
            completed ||
            humanReview ||
            activeIndex > index;

          const isActive =
            running &&
            (activeIndex === index ||
              (activeIndex === -1 && index === 0));

          return (
            <div className="workflow-stage" key={stage.name}>
              <div className="stage-track">
                <motion.div
                  className={[
                    "stage-node",
                    isPassed ? "stage-node-passed" : "",
                    isActive ? "stage-node-active" : "",
                  ].join(" ")}
                  animate={
                    isActive
                      ? {
                          scale: [1, 1.08, 1],
                        }
                      : { scale: 1 }
                  }
                  transition={{
                    duration: 1.8,
                    repeat: isActive ? Infinity : 0,
                  }}
                >
                  {isPassed ? (
                    <Check size={15} />
                  ) : (
                    <Icon size={15} />
                  )}
                </motion.div>

                {index < stages.length - 1 && (
                  <div
                    className={
                      isPassed
                        ? "stage-line stage-line-active"
                        : "stage-line"
                    }
                  />
                )}
              </div>

              <div className="stage-copy">
                <strong>{stage.name}</strong>
                <span>
                  {isActive
                    ? "Processing"
                    : isPassed
                      ? "Verified"
                      : "Waiting"}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      <div
        className={[
          "terminal-state",
          completed ? "terminal-complete" : "",
          humanReview ? "terminal-review" : "",
        ].join(" ")}
      >
        <div className="terminal-symbol">
          {completed ? "◆" : humanReview ? "!" : "◇"}
        </div>

        <div>
          <strong>
            {completed
              ? "Complete recommended"
              : humanReview
                ? "Human review"
                : "Awaiting outcome"}
          </strong>

          <span>
            {completed
              ? "Workflow recommendation generated"
              : humanReview
                ? "Operator decision required"
                : "Terminal state pending"}
          </span>
        </div>
      </div>
    </aside>
  );
}