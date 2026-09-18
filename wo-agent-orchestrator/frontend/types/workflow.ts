export type ExecutionStatus =
  | "IDLE"
  | "RUNNING"
  | "COMPLETE_RECOMMENDED"
  | "HUMAN_REVIEW"
  | "FAILED";

export type DemoScenario = {
  wo_id: string;
  scenario: string;
  expected_path: string;
};

export type DemoScenariosResponse = {
  scenarios: DemoScenario[];
};

export type RunWorkflowResponse = {
  execution_id: string;
  wo_id: string;
  status: Exclude<ExecutionStatus, "IDLE">;
};

export type CorrectionOverlay = {
  field?: string;
  original_value?: unknown;
  proposed_value?: unknown;
  reason?: string;
  evidence_ids?: string[];
  resolution_status?: string;
};

export type WorkflowResult = {
  wo_id?: string;
  current_stage?: string;
  human_review_required?: boolean;
  correction_attempts?: number;
  max_correction_attempts?: number;
  correction_overlay?: CorrectionOverlay[];
  audit_log?: string[];
  results?: {
    intake?: unknown;
    research?: unknown;
    evidence?: unknown;
    discrepancy?: unknown;
    qc?: unknown;
  };
};

export type ExecutionResponse = {
  execution_id: string;
  wo_id: string;
  status: Exclude<ExecutionStatus, "IDLE">;
  current_stage?: string | null;
  human_review_required?: boolean | null;
  correction_attempts?: number | null;
  result?: WorkflowResult | null;
  error_type?: string | null;
  created_at: string;
  updated_at: string;
};