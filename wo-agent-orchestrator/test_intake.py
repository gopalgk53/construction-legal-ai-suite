from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient


PROJECT_ENDPOINT = (
    "https://gopalg53-5366-resource.services.ai.azure.com/"
    "api/projects/gopalg53-5366"
)

AGENT_NAME = "wo-intake-agent"
AGENT_VERSION = "3"


credential = DefaultAzureCredential()

project_client = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=credential,
)

openai_client = project_client.get_openai_client()

print("Calling:", AGENT_NAME, "v" + AGENT_VERSION)

response = openai_client.responses.create(
    input=[
        {
            "role": "user",
            "content": (
                "Retrieve and analyze synthetic Work Order SYN-WO-000001 "
                "using the configured Work Order retrieval tool."
            ),
        }
    ],
    extra_body={
        "agent_reference": {
            "name": AGENT_NAME,
            "version": AGENT_VERSION,
            "type": "agent_reference",
        }
    },
)

print("\n--- Intake Agent Response ---")
print(response.output_text)