import type {
  DemoScenariosResponse,
  ExecutionResponse,
  RunWorkflowResponse,
} from "@/types/workflow";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_WO_API_BASE_URL?.replace(/\/$/, "") ?? "";

async function request<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  if (!API_BASE_URL) {
    throw new Error(
      "NEXT_PUBLIC_WO_API_BASE_URL is not configured.",
    );
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const body = await response.text();

    throw new Error(
      `API request failed (${response.status}): ${body}`,
    );
  }

  return response.json() as Promise<T>;
}

export function getDemoScenarios() {
  return request<DemoScenariosResponse>(
    "/api/v1/demo-scenarios",
  );
}

export function startWorkflow(woId: string) {
  return request<RunWorkflowResponse>(
    `/api/v1/workflows/${encodeURIComponent(woId)}/run`,
    {
      method: "POST",
    },
  );
}

export function getExecution(executionId: string) {
  return request<ExecutionResponse>(
    `/api/v1/executions/${encodeURIComponent(executionId)}`,
  );
}