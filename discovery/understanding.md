# Project Understanding — BSA AI Agent (BlackLine × SRS Consulting POC)

> Synthesis of every file in `discovery/`: the v2.2 scope PDF, the demo flow markdown, the 19-May-2026 Otter transcript, and the BlackLine financial-systems environment (YAML + diagram).

---

## 1. TL;DR

SRS Consulting is delivering a **POC for BlackLine** of a **Business System Analyst (BSA) AI Agent** that turns meeting transcripts + a short BSA write-up into a **structured BRD**, lets the human BSA review/approve, and then decomposes the BRD into **Jira Epics, User Stories, and Acceptance Criteria** — all driven from a Jira ticket called the *AI Workbench*. Subject-area scope for the POC is **BlackLine's GTM (Go-To-Market) toolkit**. Model preference is **Anthropic Claude**, explicitly *not* Gemini.

The deliverable iterates: when the BSA drops in more documents, the agent re-runs, updates the BRD and stories, and flags **scope creep / story deviation**.

---

## 2. Project Identity

| | |
|---|---|
| **Client** | BlackLine (financial close / SaaS finance platform vendor) |
| **Vendor** | SRS Consulting Inc |
| **Engagement** | POC for a Business System Analyst AI Agent |
| **Subject scope (POC)** | BlackLine GTM toolkit only — explicitly limited |
| **Doc version** | "BSA AI Agent Features and Scope v2.2" |
| **Interaction surface (POC)** | Jira — chosen for the demo; UX can be swapped later (Slack / Teams / dedicated bot) without changing the agent core |
| **Bonus capability** | Conversational sidebar chatbot inside Jira |

### Pivot history (from transcript)
- Earlier discussions covered a **Pricing / Quoting Agent** — *deprioritized*: business already built a pricing calculator, no longer interested in AI experience there.
- A **Recruiting Agent** was floated as "high visibility, well-defined" — *not pursued*.
- A **SKU Creation Agent in Salesforce using Zuora** is on the roadmap but **out of scope** for this POC.
- Ravi confirmed: **fall back to the original BSA agent**; add scope incrementally as the relationship matures.

**Implication:** scope churn is part of the working norm here. Keep the POC architecture flexible so the same agent skeleton can be retargeted at the SKU/Quoting/Recruiting agents later.

---

## 3. POC Scope — What Will Be Demonstrated

End-to-end workflow automation. The PDF and demo-flow markdown agree on six steps:

| # | Step | Trigger / State |
|---|------|----------------|
| 1 | **BSA collects & uploads** meeting transcripts + a Word/one-pager supplement to a Jira ticket named *AI Workbench*; assigns the task to the AI BSA Agent (as a Jira user). | Action: **Generate BRD** |
| 2 | **AI agent ingests** all transcripts + supplements → content merging → context building → reasoning → produces a **structured, review-ready BRD** + a list of **open questions**. BRD is attached back to the same Jira ticket. | State: **BRD Ready** |
| 3 | **Human BSA reviews & approves** the BRD; resolves open questions (possibly by uploading more docs). | Action: **Generate Story** |
| 4 | **AI agent decomposes** the approved BRD into Jira artifacts: **Epics → User Stories → Acceptance Criteria**, delivered into Jira ready for sprint planning. | State: **Story Ready** |
| 5 | **Iterative enhancement** — BSA attaches more docs to the same Jira ticket for the same functionality and re-assigns to the agent. | Action: **Generate Story** (re-run) |
| 6 | **AI updates BRD & stories** based on new input; posts a comment with **story deviation / scope-creep summary** + a summary of new changes. | State: **Story Ready (updated)** |

### Value claims (PDF)
- Eliminate manual BRD creation effort
- Improve consistency & completeness of requirements
- Accelerate story readiness for sprint planning
- Continuously learn and improve from user feedback

---

## 4. How the Agent Actually Works (transcript-level clarifications)

Bimal and Ravi expanded the workflow during the call. Items that aren't in the PDF but came out of the conversation:

- The BSA submits **a one-pager (high-level) + transcript(s)** — explicitly named as the two input artifacts.
- The agent does its analysis, **breaks it into a BRD if it can**, **and surfaces open questions**, then **assigns the ticket back to the BSA**.
- The BSA answers / attaches more docs and **reassigns to the AI user** in Jira.
- Multiple round-trips of BSA ⇄ AI are expected before the BRD is finalized.
- Only **after** the BSA talks to stakeholders and is satisfied does the BSA say "now build me epics and stories" — story generation is a **separate, second-stage trigger**, not a continuation of the BRD step.
- Chet's understanding (confirmed): trigger is a **Jira ticket with a specific flag** — likely a **webhook** to invoke the agent. Exact mechanism TBD.

### Knowledge sources the agent needs (Ravi)
The agent should be backed by a knowledge base covering:
- **Salesforce data model**
- **Jira tickets** (existing org history)
- **Confluence pages** — design docs, prior technical design docs
- **HubSpot** — feature-usage knowledge
- Goal: "the agent knows a lot about BlackLine and how BlackLine has implemented Salesforce, and has implemented coding"

→ This is the **integrated knowledge base / RAG** future item from the PDF; in the POC it's likely a constrained subset.

---

## 5. Stakeholders

| Name | Org | Role in this work |
|---|---|---|
| **Ravi Sharma** | BlackLine | Client-side lead; sets scope and priorities; drops out of meetings quickly |
| **Bimal Hazarika** | SRS Consulting | Senior engagement lead (25 yrs at HP). Owns success alongside Chet. Hands-on with tooling — actively comparing Claude / Codex / Gemini Anti-Gravity |
| **Chet Gandhi** | SRS Consulting | Oversight; will plug in Forward Deployed Engineers |
| **Gopal Goswami** | BlackLine (IIT) | GTM apps, CPQ side; works alongside Ravi & Vinay |
| **Vinay** | BlackLine | Not on the 19-May call; involved in agent prioritization |

### Engagement model
- **NOT T&M.** Success owned by Chet + Bimal. Whoever does the work, outcomes are owned at the senior level.
- Execution by **Forward Deployed Engineers (FDEs)** — staffed iteratively.
- Offshore resources need **background verification** before onboarding.
- **BlackLine internal onboarding is slow** — identify people early.
- SRS recommends, BlackLine decides — Ravi is plugged in as a decision-maker.

---

## 6. Technical Preferences & Constraints

### Model choice — Claude, not Gemini

Bimal ran the same prompts through three coding tools recently:

| Tool | Score |
|---|---|
| **Claude Code** | 9 / 10 |
| **Codex (OpenAI)** | 8.5 / 10 |
| **Anti-Gravity (Gemini)** | ~3 / 10 |

Ravi independently agreed: *"there's a lot of issues, especially in the enterprise space with the Gemini platform."* Ravi offered to **procure Anthropic licenses** if SRS needs them.

**→ Hard preference for Anthropic / Claude as the LLM provider.** Build with this in mind: prompts, model configs, and any benchmarking should default to Claude (sonnet/opus tiers). LiteLLM-style abstraction is fine, but the default model should never be Gemini for this client.

### Interaction surface
- **Jira** is the POC UX (uploads, assignments, comments, attachments).
- Confirmed flexibility: this can move to Slack / Teams / dedicated chatbot post-POC.

### Trigger mechanism (TBD)
- Likely a **Jira webhook** keyed off a flag/label on the *AI Workbench* ticket, or "assigned to AI user" event.
- Implementation specifics still open.

---

## 7. BlackLine's Financial Systems Environment (Context the Agent Operates In)

The agent's "knowledge" of BlackLine's environment is partly captured in `blackline_financial_systems_environment_yaml.yaml` (machine-readable) and the matching architecture diagram. **This is BlackLine's *internal* finance stack** — the systems the BSA writes requirements *about*. The POC restricts scope to **GTM**, but the agent needs to understand how the GTM pieces tie into the broader spine.

### Swimlanes (system owners)
- **FinSys EA** (black) — core finance applications
- **HR EA** (orange) — HRIS / payroll
- **SF EA** (blue) — likely *"SaaS Finance / Shared Finance EA"* (Q1 open question in YAML — could also mean Salesforce EA)
- **Business Managed** (green) — Salesforce (CRM) sits here

### Systems map (21 apps)
| Cluster | Systems |
|---|---|
| **Central hub** | **NetSuite** (ERP) |
| **Quote-to-Cash** | Klarity (CLM) → Salesforce (CRM) → Zuora Billing → Zuora Revenue (ASC 606) → Avalara (tax) |
| **Tax / FP&A / Reporting / Lease** | OneSource (Tax), Adaptive Insights (FP&A), Workiva (10-K/SOX), LeaseQuery (ASC 842) |
| **Close & Cash** | BlackLine Close, BlackLine Cash App, Bank of America |
| **Procure-to-Pay** | Coupa |
| **T&E** | SAP Concur (expense), Navan (travel) |
| **Sales comp** | SAP SuccessFactors (Commissions) |
| **HRIS / Payroll** | Workday (HRIS hub), ADP (US payroll), CloudPay (intl payroll), Fidelity (stock plan) |

### Integration types (legend)
| Type | Style | |
|---|---|---|
| Manual | dashed black | |
| Automated | solid black | |
| **Workato** (middleware) | solid orange | |
| Employee Data | dotted orange | (Workday is the source) |

**36 integrations** are catalogued (INT-001 … INT-036). The YAML uses explicit `verify: true` / `confidence: low` markers for inferred edges, plus an `open_questions` section (Q1–Q6) — the analyst is signaling which arrows in the diagram are best-guess and which are observed.

### GTM-relevant slice (what the BSA agent will likely touch first)
For the GTM-scoped POC, the systems most likely to appear in transcripts:
- **Salesforce** (CRM)
- **Zuora Billing** (subscription billing — quotes, billings)
- **Zuora Revenue** (rev rec)
- **Klarity** (contract review for order forms)
- **Avalara** (tax on billings)
- **NetSuite** (where opportunities land after Closed Won, where Zuora posts billings/orders/JEs)
- **HubSpot** (mentioned as a knowledge source; not in the diagram)

The Quote-to-Cash spine is essentially: **Klarity → SFDC → Zuora Billing ⇄ Avalara → Zuora Revenue → NetSuite**, with SFDC also feeding NetSuite directly on Closed Won.

---

## 8. Future Vision (PDF section 4 — beyond POC)

For roadmap awareness only — none of these are POC scope:

1. **Continuous learning** from BSA edits to BRDs (feedback loop)
2. **Customizable BRD & story templates** per team/domain
3. **Interactive context accumulation** in the Jira sidebar chatbot — multi-session memory + targeted gap-resolution Q&A
4. **Integrated knowledge base** — Confluence, Zuora docs, Salesforce docs, internal wikis
5. **Process flow diagram generation** alongside the BRD
6. **Comprehensive RAG** over Confluence + Jira history + existing BRDs + ERDs + object models + vendor docs
7. **Channel strategy** — Slack / Teams / dedicated chatbot evaluation
8. **Observability & cost tracking** — full traceability of inputs → processing → outputs → spend, so failed BRDs can be diagnosed at the parsing / context / generation stage
9. **QA test-case + automation generation** — a QA agent that reads approved stories and produces happy-path / edge / negative cases and executable scripts
10. **Story dependency mapping** — agent suggests likely sprint sequencing (e.g., backend before frontend)

---

## 9. Mapping to the Existing `dynpro/` Codebase

The current `dynpro/` repo (per `SYSTEM_ARCHITECTURE.md`) is a **Context-Aware Question Generation Tool**: transcript + one-pager → MCP-aggregated context → categorized questions + resource snapshot. That maps cleanly onto **Steps 1–2 of the BSA POC**, plus part of the "open questions" deliverable.

| BSA POC step | dynpro/ analogue today | Gap to close |
|---|---|---|
| 1. Intake transcripts + one-pager | Input processor + entity extractor ✅ | Need Jira-side intake (webhook / ticket assignment), not file uploads |
| 2a. Context build | MCP fan-out (Confluence / Jira / SFDC / HubSpot) ✅ | Already matches the knowledge sources Ravi named |
| 2b. **Generate BRD** | Question generator generates *questions*, not a *BRD* ❌ | Add a BRD-generation agent (Claude Opus tier); output structured BRD doc |
| 2c. Open questions surfaced | Question generator ✅ | Reuse — but tie questions to the BRD draft, not standalone |
| 3. Human review in Jira | n/a (file outputs today) ❌ | Need Jira attachment + comment integration |
| 4. **Generate Epics / Stories / AC** | Not present ❌ | New agent: BRD → Jira epics/stories with acceptance criteria via Jira API |
| 5–6. Iterative re-run + scope-creep diff | Not present ❌ | New: diff against prior BRD/story state; comment with deviation summary |

**Net work:** Two new agents (BRD generator, Story decomposer + scope-creep diff), Jira write-back integration, and a webhook-driven trigger. The MCP-context machinery and the resource-storage layer transfer largely as-is.

---

## 10. Open Decisions to Resolve

Compiled from across the materials:

1. **Trigger mechanism** — webhook on Jira ticket flag vs. "assigned to AI user" event vs. polling?
2. **Jira write surface** — write back to ticket attachments + comments only, or also create child Epics/Stories programmatically?
3. **BRD format** — is there a BlackLine BRD template to match? (Future-vision item suggests templates are coming; what does the POC default to?)
4. **Knowledge base scope for the POC** — full Confluence + Jira + SFDC + HubSpot, or a curated GTM subset?
5. **Anthropic licenses** — Ravi to procure. Confirm model tier (Sonnet vs Opus) + spend ceiling.
6. **Conversational sidebar** — bonus / demo capability or core POC?
7. **YAML environment ambiguities** (Q1–Q6 in the YAML): SF EA meaning, Coupa middleware, Navan non-airfare path, Fidelity cadence, BL ↔ ADP/CloudPay direction, Avalara return path. These are BlackLine-internal to resolve and feed back into the agent's context store.
8. **FDE staffing & background verification** — names + start dates from BlackLine side.

---

## 11. Working Norms (from the transcript)

- **Start narrow, succeed visibly.** Bimal's framing: pick a use case with a good boundary that can really succeed — that makes both teams look good. Translate: resist scope expansion in the POC.
- **Scope can pivot quickly.** Quoting/Pricing → Recruiting → BSA in a single round of conversations. Architecture should isolate the "agent skeleton" from the domain so retargeting is cheap.
- **Senior ownership, FDE execution.** Bimal + Chet own outcomes; engineers run with framework once it's set.
- **Onboarding has lead time.** Identify resources early.

---

## 12. Quick Reference — File Inventory

| File | What it is |
|---|---|
| `BSA AI Agent Features and Scope v2.2.pdf` | Authoritative scope doc — 5 pages, POC scope + future vision |
| `BSA AI Agent — Demo Flow.md` | Condensed 6-step demo flow (the same steps as the PDF, faster to skim) |
| `Quoting Agent Use Case follow up_otter_ai_transcript_19Mat2026.txt` | 19-May-2026 Otter transcript — pivot context, model preference (Claude > Gemini), knowledge sources, engagement model |
| `blackline_financial_systems_environment_yaml.yaml` | Machine-readable map of BlackLine's 21 finance systems + 36 integrations, with confidence markers + open questions |
| `blackline_financial_system_environment.jpg` | Source diagram the YAML was derived from |
