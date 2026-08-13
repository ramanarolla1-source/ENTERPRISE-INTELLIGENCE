<img width="1536" height="1024" alt="Enterprise Intelligence" src="https://github.com/user-attachments/assets/f8b1fc00-bf82-4a90-ac53-0d5ef05d602b" />
One Pager: https://docs.google.com/document/d/1pDKU3oymbQ6wB-lB_5DRB8tmYB_gfmaBPeyoNBNNQko/edit?usp=sharing

Demo Video: https://youtu.be/yX2-WQo0p0w


# Enterprise Intelligence

**Verifiable External Evidence → AI Intelligence → Authorized Enterprise Decisions**

Enterprise Intelligence is a prototype for evidence-backed enterprise decision-making built around **Flare FDC / Web2Json**.

It addresses a simple but important problem:

> Enterprises make consequential decisions using information that exists outside their own systems, but the provenance and integrity of that external information—and the historical record of how a decision was made—can be difficult to establish years later.

Enterprise Intelligence creates a workflow in which:

**public external sources → AI source intelligence → FDC/Web2Json verification → AI evidence analysis → enterprise policy → executive authorization → Trust Receipt → on-chain decision record**

The prototype demonstrates this using **vendor / counterparty selection** as the initial use case.

---

## Why Enterprise Intelligence?

Traditional enterprise decision-making often combines internal submissions with fragmented external intelligence.

A vendor may offer the lowest price while carrying external regulatory, corporate, operational, or reputational risks that are not visible in the commercial proposal.

Enterprise Intelligence changes the question from:

> **“Who offers the lowest price?”**

to:

> **“Who offers the best risk-adjusted value based on evidence we can verify?”**

The system does not replace enterprise procurement or governance.

It adds a verifiable external-evidence layer and a tamper-evident decision history.

---

## Core Principle

Enterprise Intelligence separates four responsibilities:

| Layer                                | Responsibility                                                                                              |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| **AI Source Intelligence**           | Qualifies candidate public sources based on authority, provenance, relevance, freshness, and corroboration. |
| **FDC / Web2Json**                   | Provides an attested, verifiable response from the selected supported Web2 source.                          |
| **AI Decision Intelligence**         | Interprets verified evidence, builds risk profiles, and ranks vendors / counterparties.                     |
| **Enterprise Authority & Contracts** | Applies policy, obtains authorized approval, records decision state, and preserves decision provenance.     |

The key boundary is:

> **AI does not become the oracle. FDC does not declare the internet truthful.**

AI qualifies and interprets.

FDC attests to the external response.

Deterministic policy establishes the decision condition.

The authorized Smart Account controls who can approve.

The decision contract anchors the resulting state.

---

## Key Features

### 1. AI Source Intelligence

The system can identify candidate public sources relevant to a decision and evaluate them using factors such as:

* authority
* provenance
* relevance
* freshness
* corroboration
* source consistency

The objective is not to declare a source absolutely trustworthy.

The objective is to establish an evidence-quality hierarchy and identify suitable supported sources for verification.

---

### 2. FDC / Web2Json Evidence Layer

Selected supported Web2 sources are processed through **Flare Data Connector (FDC) Web2Json**.

Conceptually:

```text
Supported Web2 Source
        ↓
Web2Json Request
        ↓
FDC Attestation Process
        ↓
Attested Response + Proof
        ↓
On-chain Verification
```

The application can then distinguish between:

**what an AI model claims a source said**

and

**what the verified attestation represents as the selected source response.**

For technical background, see:

* `docs/FDC-Web2Json.md`
* `docs/Flare-Integration.md`

---

## 3. AI Decision Intelligence

After external evidence is attested, AI performs a separate task:

> **What does the verified evidence mean for the enterprise decision?**

The system can produce:

* evidence-backed findings
* risk dimensions
* confidence indicators
* vendor / counterparty comparisons
* recommended order of preference

AI is therefore an **interpretation and intelligence layer**, not the final authority.

---

## 4. Confidentiality by Design

Enterprise Intelligence does **not** require confidential vendor submissions to become public data.

Information such as:

* quoted price
* technical suitability
* negotiated terms
* commercial proposals
* proprietary documents
* internal evaluation notes

remains within the enterprise-controlled environment.

The public-data workflow is separated from confidential enterprise information.

Sensitive Trust Receipt contents are intended to remain **encrypted and access-controlled**, while the blockchain can preserve the relevant cryptographic commitment and decision state.

---

## 5. Smart Account Authorization

AI can recommend a decision.

**AI cannot authorize the enterprise decision.**

An authorized executive uses a **Smart Account** to approve the decision according to enterprise policy.

This separates:

**Intelligence** from **Authority**.

---

## 6. Trust Receipt

The **Trust Receipt** is the project's long-lived decision-provenance layer.

It records or commits the information needed to reconstruct how a consequential decision was made, including:

* decision identifier
* evaluated candidates
* source assessments
* FDC evidence references
* AI findings
* risk profile
* policy/version context
* authorization
* execution state
* timestamp
* cryptographic commitment

Sensitive details remain protected rather than being exposed as public blockchain data.

### Why this matters

A later board, executive, auditor, or authorized reviewer may ask:

> **“Why was this vendor selected?”**

The Trust Receipt is designed to allow the organization to reconstruct:

**what was known → what was verified → what AI concluded → what policy applied → who approved → what happened next**

A later board can make a new decision.

It should not be able to silently rewrite the historical decision record.

---

## 7. On-Chain Decision Record

The blockchain is not used simply as a database.

The purpose is to create a **tamper-evident institutional memory** for consequential enterprise decisions.

Conceptually:

```text
Decision Proposed
       ↓
Evidence Verified
       ↓
Policy Evaluated
       ↓
Executive Approved
       ↓
Trust Receipt Anchored
       ↓
Decision Executed
```

Future decisions can supersede previous decisions without rewriting the historical record.

Where appropriate, the same architecture can be extended to conditional on-chain payment, escrow, or asset release.

---

# Why Flare?

Enterprise Intelligence uses Flare because the problem begins **outside the blockchain**.

Public information exists in Web2 systems, APIs, registries, and other external sources.

The application needs that information to become usable as verifiable input to an on-chain decision workflow.

That creates the interoperability path:

```text
External Web2 Information
          ↓
       FDC / Web2Json
          ↓
    Verifiable Evidence
          ↓
   AI Decision Intelligence
          ↓
Enterprise Policy + Authority
          ↓
 Programmable Flare Action
```

This demonstrates a form of **information interoperability**:

> **bringing external Web2 evidence into a programmable Flare environment.**

The project deliberately avoids adding Flare primitives that are not required by the MVP. FDC/Web2Json is central because external evidence is central to the problem being solved.

---

# Architecture

```text
                         ENTERPRISE
                              │
          ┌───────────────────┴───────────────────┐
          │                                       │
 Confidential Enterprise Data              Public External Data
          │                                       │
          │                                       ▼
          │                              AI Source Intelligence
          │                                       │
          │                              Preferred Sources
          │                                       │
          │                                       ▼
          │                                FDC / Web2Json
          │                                       │
          │                              Attested Response
          │                                       │
          │                                       ▼
          │                              AI Decision Intelligence
          │                                       │
          └───────────────────┬───────────────────┘
                              ▼
                       Enterprise Policy
                              │
                              ▼
                       Smart Account
                       Executive Approval
                              │
                              ▼
                 Enterprise Decision Contract
                              │
                 ┌────────────┴────────────┐
                 │                         │
                 ▼                         ▼
          Trust Receipt              Decision State
          + Commitment                 + Execution
                 │
                 ▼
       Long-Lived Decision Provenance
```

See `docs/Architecture.md` for the detailed architecture.

---

# Repository Structure

```text
enterprise-intelligence/
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── requirements.txt
├── docs/
│   ├── Architecture.md
│   ├── Flare-Integration.md
│   ├── FDC-Web2Json.md
│   ├── Trust-Receipt.md
│   ├── Security-and-Confidentiality.md
│   └── Demo-Guide.md
├── contracts/
│   └── EnterpriseDecisionRegistry.sol
├── src/
│   ├── source_intelligence.py
│   ├── evidence_pipeline.py
│   ├── decision_engine.py
│   ├── trust_receipt.py
│   └── pipeline.py
├── data/
│   ├── sources.json
│   ├── vendors.json
│   └── sample_decision.json
└── demo/
    └── demo-flow.md
```

---

# Demo Flow

The prototype demonstrates:

```text
1. Create enterprise decision
2. Keep confidential enterprise information private
3. Discover and qualify external sources
4. Select preferred supported source
5. Retrieve / attest external data through FDC Web2Json
6. Interpret verified evidence with AI
7. Build vendor risk profiles
8. Apply enterprise policy
9. Obtain executive authorization
10. Generate Trust Receipt
11. Anchor decision commitment / state on-chain
12. Reconstruct the decision for future audit
```

See `docs/Demo-Guide.md`.

---

# Prototype Status

This repository is a **hackathon prototype**.

The architecture distinguishes between:

* **Implemented functionality**
* **Demonstration / simulated components**
* **Conceptual extensions**

Where a component is simulated, the documentation should identify it explicitly rather than implying production readiness.

The objective is to demonstrate the architecture and the meaningful role of Flare FDC/Web2Json in the workflow.

---

# Design Principles

### Evidence before interpretation

External information should be qualified and verified before it becomes a decision input.

### AI without autonomous authority

AI can analyze and recommend, but enterprise authority remains controlled by humans and explicit policy.

### Confidentiality by default

Private enterprise submissions should not become public simply because the decision is eventually anchored on-chain.

### Immutable history, not irreversible business decisions

An enterprise can change its mind through a new authorized decision.

The historical record should remain intact.

### Meaningful Flare integration

The project uses Flare primitives because they solve actual problems in the architecture—not because additional integrations make the project look larger.

---

# Future Extensions

The architecture can extend beyond vendor selection into:

* counterparty risk
* institutional RWA diligence
* treasury decisions
* regulated asset workflows
* conditional settlement
* confidential computation
* continuous external-data monitoring

These are extensions of the architecture, not requirements of the current MVP.

---

# Submission

**Project:** Enterprise Intelligence
**Track:** Interoperable Asset Products
**Network:** Flare
**Primary Flare Primitive:** FDC / Web2Json

> **External evidence. Verified by Flare. Interpreted by AI. Authorized by humans. Preserved on-chain.**
