# Production Operations Runbook

## Autonomous Work Order Intelligence & Operations Platform

**Environment:** Portfolio Production  
**Data:** Synthetic only  
**Runtime:** Azure Container Apps  
**AI Platform:** Microsoft Foundry  
**Retrieval:** AWS  
**CI/CD:** GitHub Actions

---

## 1. Purpose

This runbook defines the operational procedures for validating, deploying, monitoring, and troubleshooting the Autonomous Work Order Intelligence & Operations Platform.

The application consists of:

```text
AWS Synthetic Retrieval
        ↓
MCP
        ↓
Microsoft Foundry Agents
        ↓
Deterministic Python Control Plane
        ↓
FastAPI
        ↓
Next.js Operations Console
        ↓
Azure Container Apps
```

---

## 2. Production Components

### AWS

```text
Amazon S3
AWS Lambda retrieval
API Gateway
MCP Lambda adapter
```

### Microsoft Foundry

```text
Intake Agent
Research Agent
Evidence Agent
Discrepancy Agent
QC Agent
GPT-5-mini
```

### Azure

```text
Azure Container Registry
Azure Container Apps Environment
wo-intelligence-api
wo-intelligence-web
```

### GitHub

```text
Source repository
Backend deployment workflow
Frontend deployment workflow
OIDC federation
```

---

## 3. Production Frontend

Application:

```text
wo-intelligence-web
```

Production URL:

```text
https://wo-intelligence-web.victoriousmoss-788bd572.southeastasia.azurecontainerapps.io
```

Accepted frontend revision:

```text
wo-intelligence-web--0000005
```

Accepted source commit:

```text
fd1bd66
```

---

## 4. Production Backend

Application:

```text
wo-intelligence-api
```

Production hostname:

```text
wo-intelligence-api.victoriousmoss-788bd572.southeastasia.azurecontainerapps.io
```

The backend currently operates with one replica because execution state is stored in memory.

---

## 5. Health Verification

Check the backend health endpoint:

```bash
curl -sS https://wo-intelligence-api.victoriousmoss-788bd572.southeastasia.azurecontainerapps.io/health
```

Expected result:

```text
healthy application response
```

A health failure should be investigated before executing synthetic workflows.

---

## 6. Demo Scenario Verification

Check available demo scenarios:

```bash
curl -sS https://wo-intelligence-api.victoriousmoss-788bd572.southeastasia.azurecontainerapps.io/api/v1/demo-scenarios
```

The production demonstration should expose the approved synthetic scenarios.

---

## 7. Golden-Path Production Test

Three scenarios form the minimum production acceptance suite.

### Clean Path

```text
SYN-WO-000001
```

Expected:

```text
COMPLETE_RECOMMENDED
Human Review = NO
Corrections = 0
```

### Controlled Correction

```text
SYN-WO-000116
```

Expected:

```text
COMPLETE_RECOMMENDED
Human Review = NO
Corrections >= 1
```

### Human Review

```text
SYN-WO-000111
```

Expected:

```text
HUMAN_REVIEW
Human Review = YES
Corrections = 0
```

These scenarios validate three separate properties:

```text
Autonomy
Correction
Escalation
```

---

## 8. Local Automated Validation

Before backend deployment:

```bash
python -m pytest tests/ -q
```

Accepted baseline:

```text
75 passed
```

A failing core test blocks intentional production deployment until the failure is understood.

---

## 9. Frontend Validation

Before frontend deployment:

```bash
cd frontend
npm run lint
npm run build
```

Both commands must succeed.

Return to the project root when finished:

```bash
cd ..
```

---

## 10. Git Validation

Before committing:

```bash
git status --short
git diff --check
```

`git diff --check` should produce no output.

Review the intended change set before committing.

---

## 11. Azure Frontend Revision Verification

Use:

```bash
az containerapp revision list \
  --name wo-intelligence-web \
  --resource-group rg-gopalg53-2640 \
  --query "[?properties.active==\`true\`].{Revision:name,Traffic:properties.trafficWeight,Image:properties.template.containers[0].image}" \
  -o table
```

Verify:

```text
Active revision
100% traffic
Expected container image SHA/tag
```

---

## 12. Azure Backend Revision Verification

Use:

```bash
az containerapp revision list \
  --name wo-intelligence-api \
  --resource-group rg-gopalg53-2640 \
  --query "[?properties.active==\`true\`].{Revision:name,Traffic:properties.trafficWeight,Image:properties.template.containers[0].image}" \
  -o table
```

Verify the expected backend image is receiving production traffic.

---

## 13. Container App Status

Frontend:

```bash
az containerapp show \
  --name wo-intelligence-web \
  --resource-group rg-gopalg53-2640 \
  --query "{name:name,fqdn:properties.configuration.ingress.fqdn,latestRevision:properties.latestRevisionName}" \
  -o table
```

Backend:

```bash
az containerapp show \
  --name wo-intelligence-api \
  --resource-group rg-gopalg53-2640 \
  --query "{name:name,fqdn:properties.configuration.ingress.fqdn,latestRevision:properties.latestRevisionName}" \
  -o table
```

---

## 14. Container Logs

If the backend fails:

```bash
az containerapp logs show \
  --name wo-intelligence-api \
  --resource-group rg-gopalg53-2640 \
  --type console \
  --tail 100
```

For frontend failures:

```bash
az containerapp logs show \
  --name wo-intelligence-web \
  --resource-group rg-gopalg53-2640 \
  --type console \
  --tail 100
```

Do not copy sensitive credentials into debugging logs or documentation.

---

## 15. Troubleshooting — Frontend Loads but Execution Fails

Check in this order:

```text
1. Backend health
2. Frontend API base URL
3. Backend Container App revision
4. Backend logs
5. Foundry authentication
6. Foundry agent execution
7. MCP availability
8. AWS synthetic retrieval
```

Do not immediately modify application code before locating the failing layer.

---

## 16. Troubleshooting — Workflow Remains Running

The API uses an asynchronous execution model.

If an execution remains non-terminal:

```text
Check backend logs
        ↓
Check orchestrator execution
        ↓
Check Foundry call
        ↓
Check MCP approval/tool response
        ↓
Check parser
        ↓
Check deterministic router
```

Because the execution store is in memory, a backend restart can remove an existing execution record.

---

## 17. Troubleshooting — Incorrect Workflow Route

Do not first change the agent prompt.

Inspect:

```text
Raw specialist outcome
        ↓
Structured parser result
        ↓
Router input
        ↓
Router decision
        ↓
Workflow state
```

Routing authority belongs to deterministic application logic.

An incorrect route may therefore originate from:

- agent semantics
- parser interpretation
- deterministic routing logic
- incorrect scenario/evaluation expectation

The failing layer must be identified before changing behavior.

---

## 18. Troubleshooting — Unexpected Human Review

Check whether the escalation came from:

```text
Explicit specialist human-review recommendation
Unresolved documentary conflict
QC HUMAN_REVIEW
Correction retry limit
Structured parsing
```

Do not remove human review simply to force a successful demonstration.

Human escalation is an intended safety outcome.

---

## 19. Troubleshooting — Unexpected BTP

Verify whether the underlying issue is actually correctable.

Remember:

```text
UNVERIFIED alone ≠ BTP
```

and:

```text
MISSING alone ≠ BTP
```

unless an established requirement makes the information necessary.

Customer claims must not be treated as independently verified evidence.

---

## 20. Troubleshooting — Correction Loop

Check:

```text
correction_attempts
max correction attempts
correction overlay
QC re-review
router decision
```

The system must never enter an unlimited correction loop.

Repeated unresolved correction must terminate in human review.

---

## 21. Troubleshooting — MCP

Current approved operation:

```text
get_work_order
```

Validate that:

```text
Server = expected MCP server
Tool = get_work_order
Data = synthetic
Operation = read-only
```

Do not broaden automatic approval to future write-capable tools while troubleshooting.

---

## 22. Troubleshooting — AWS Retrieval

Verify the chain:

```text
Synthetic S3 object
      ↓
Retrieval Lambda
      ↓
API Gateway
      ↓
MCP Lambda
      ↓
Foundry
```

Determine which boundary fails before modifying downstream agent logic.

---

## 23. Privacy Incident Rule

If real customer information is accidentally introduced into the portfolio system:

```text
STOP
```

Do not continue processing it.

The portfolio architecture is synthetic-only.

The affected information should not be committed, deployed, indexed, embedded, copied into prompts, or used for demonstration.

Follow the appropriate organizational handling process for any real data involved.

---

## 24. Secrets Rule

Never place credentials in:

```text
Git source
README
Screenshots
Prompt examples
Frontend code
Evaluation datasets
Terminal transcripts committed to Git
```

Secrets belong in the appropriate managed environment/configuration mechanism.

---

## 25. Deployment Failure

When a GitHub Actions deployment fails:

```text
1. Identify failing workflow step
2. Determine authentication/build/push/deploy layer
3. Read exact error
4. Correct only that layer
5. Re-run validation
6. Commit
7. Deploy
8. Verify active Azure revision
```

Do not create long-lived credentials merely to bypass an identity or policy problem.

---

## 26. Rollback Principle

Azure Container Apps revisions provide deployment history.

If a new revision introduces a production regression, route traffic back to a previously verified healthy revision using the appropriate Azure deployment procedure.

Before rollback, record:

```text
Failing revision
Expected revision
Reason
Observed failure
```

After rollback, rerun the golden-path validation.

---

## 27. Execution Store Limitation

Current architecture:

```text
FastAPI
   ↓
In-memory ExecutionStore
```

Operational consequence:

```text
Container restart
→ execution state may disappear
```

This is accepted for the current synthetic portfolio demonstration.

It is not the intended persistence architecture for a scaled production system.

---

## 28. Scaling Rule

Do not increase backend replicas above the architecture's supported configuration while using process-local execution state.

Before horizontal scaling:

```text
Introduce durable shared execution state
        ↓
Test concurrency
        ↓
Test restart recovery
        ↓
Test multi-replica execution
        ↓
Then scale
```

---

## 29. Post-Deployment Checklist

After an intentional deployment verify:

```text
[ ] GitHub Actions succeeded
[ ] Correct container image deployed
[ ] Correct Azure revision active
[ ] Expected traffic percentage
[ ] Backend health passes
[ ] Frontend loads
[ ] Demo scenarios load
[ ] Clean path passes
[ ] Correction path passes
[ ] Human-review path passes
[ ] No unexpected sensitive information exposed
```

---

## 30. Current Production Acceptance

Frontend accepted revision:

```text
wo-intelligence-web--0000005
```

Frontend accepted commit:

```text
fd1bd66
```

Production traffic:

```text
100%
```

Core automated suite:

```text
75 passed
```

Golden paths:

```text
SYN-WO-000001  PASS
SYN-WO-000116  PASS
SYN-WO-000111  PASS
```

---

## 31. Operational Definition of Healthy

The system is considered healthy for its current portfolio scope when:

```text
Backend responds
        +
Frontend responds
        +
Synthetic scenarios available
        +
Agent pipeline executes
        +
Deterministic routing works
        +
Golden paths preserve expected invariants
        +
No privacy boundary violation
```

---

## 32. Scope

This runbook covers operation of the synthetic portfolio demonstration.

It does not define procedures for processing real customer information or executing real-world legal actions.

Those capabilities are outside the current system boundary.