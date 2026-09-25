# User guide

## What the product does

NTO Operations Copilot teaches a new researcher how to complete the Notice to Owner research process. It explains the current task, retrieves synthetic work-order evidence, answers questions and guides the next approved action when the researcher is stuck.

It does not replace the researcher’s judgment or silently resolve evidence conflicts.

## Start a research session

1. Open the application.
2. Select **Start guided research**.
3. Enter the complete work-order identifier in the left panel.
4. Select the arrow button to load it.
5. Confirm that the header shows the correct active WO.

Example identifier:

```text
SYN-WO-000110
```

For the new teaching set, open **Request queue** and select any WO from `SYN-WO-000121` through `SYN-WO-000220`. The queue groups five variants under each of 20 intake scenarios. A selection is not marked loaded until the intake agent confirms the record.

After loading, the **Work order intake** card shows the customer request, job address, claimed owner and GC, work type, and supplied NOC, bond, permit, and parcel references. `Not provided` is intentional scenario data, not a UI error.

## Follow the research process

Use the six-step navigation in order:

1. **Understand request** — identify the requested notice, customer-provided parties and missing inputs.
2. **Property** — confirm the address, parcel, legal description and current owner.
3. **Recorded NOC** — locate the official record and inspect parties, dates and expiration.
4. **Participants** — separate customer claims from verified project participants.
5. **Prepare notice** — transfer only evidence-supported information.
6. **Quality check** — compare the draft with approved sources and route unresolved issues.

Each stage shows:

- What to inspect
- What to record
- When the researcher must stop and ask for help

Use **Mark complete and continue** only after completing the current verification.

## Ask the coach

Use the coach when:

- A customer claim differs from an official record
- A required document is missing
- A participant role is unclear
- Two sources contain different values
- You do not know which research resource to check
- You need the approved contact or escalation procedure

Describe the issue with specific context:

```text
The customer listed one general contractor, but the recorded NOC lists another.
I confirmed the parcel and recording date. What should I do next?
```

Avoid vague questions such as:

```text
What do I do?
```

## Understand the answer

The coach responds in three sections:

- **Answer** — the direct response to the question
- **Why** — the evidence or rule supporting the response
- **Next step** — the next operational action

The coach should distinguish:

- Verified evidence
- Customer-provided claims
- Missing information
- Unresolved conflicts

## General-contractor conflict

When contractor identities conflict:

1. Preserve every name and its source.
2. Do not replace one value with another.
3. Confirm what the recorded NOC actually contains.
4. Use the approved CC-first path.
5. Document three calls and three emails when required.
6. Return the issue to the customer if it remains unresolved.
7. Escalate when the operating procedure requires human review.

## Researcher responsibility

The researcher must:

- Open and inspect the source records
- Confirm the evidence used in the notice
- Record source provenance
- Avoid treating coach output as a source document
- Escalate unresolved material issues
- Complete the final quality-control review

The coach provides guidance. It does not approve or release the notice.

## If the coach is unavailable

If the chat shows a connection error:

1. Confirm the active WO remains correct.
2. Retry the question once.
3. Check the API health endpoint if you operate the environment.
4. Continue documenting completed research while the connection is investigated.
5. Do not invent or assume missing facts.
