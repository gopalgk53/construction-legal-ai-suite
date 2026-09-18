import json

from orchestrator import call_agent


WO_ID = "SYN-WO-000111"


def main() -> None:
    message = f"""
Retrieve synthetic Work Order {WO_ID} using get_work_order.

Do not analyze it.
Do not infer anything.
Do not use web search.
Do not provide recommendations.

Return the complete Work Order object exactly as retrieved,
including all available:

- metadata
- customer_input
- project
- work_details
- participants
- contractual_chain
- evidence
- communications
- customer_approvals
- research
- qc

Do not access or request ground_truth.

Return valid JSON only.
"""

    result = call_agent(
        agent_name="wo-intake-agent",
        agent_version="3",
        message=message,
        debug=False,
    )

    try:
        data = json.loads(result)
        print(
            json.dumps(
                data,
                indent=2,
            )
        )

    except json.JSONDecodeError:
        print(result)


if __name__ == "__main__":
    main()