# BSA AI Agent — Demo Flow

**Step 1 — BSA Collects & Uploads**

- BSA gathers multiple meeting transcripts + a Word supplement document
- Uploads them to a Jira ticket
- Assigns the task to the "AI BSA Agent" in Jira
- Action trigger: **Generate BRD**

**Step 2 — AI Agent Processes & Generates BRD**

- AI Agent ingests all transcripts and supplement docs
- Performs content merging, builds context, reasons through requirements
- Generates a structured BRD
- BRD is uploaded back to the same Jira ticket
- State: **BRD Ready**

**Step 3 — BSA Reviews & Approves**

- Human BSA reviews the generated BRD for completeness and accuracy
- Approves to proceed
- Action trigger: **Generate Story**

**Step 4 — AI Agent Creates Epic & Stories**

- Agent decomposes the approved BRD into Jira artifacts:
  - Epics
  - User stories
  - Acceptance criteria
- Stories delivered directly into Jira, ready for sprint planning
- State: **Story Ready**

**Step 5 — Iterative Enhancement (Real-World Use Case)**

- BSA receives a new document for the same functionality
- Attaches new document to the existing Jira ticket
- Assigns to AI Agent
- Action trigger: **Generate Story** (re-run with new context)

**Step 6 — AI Agent Updates BRD & Stories**

- Analyzes new input against existing BRD/stories
- Updates BRD and Jira stories accordingly
- Posts comments with:
  - Story deviation / scope creep summary
  - Summary of new changes added
- State: **Story Ready (updated)**

------

**Bonus capability shown in demo:** Conversational interface — chat-based interaction within the Jira flow (sidebar chatbot).

**Demo platform note:** Jira is the chosen interaction surface for this POC. UX layer can be swapped later (Slack, Teams, dedicated chatbot) without changing the agent core.