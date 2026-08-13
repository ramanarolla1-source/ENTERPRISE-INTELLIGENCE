# Enterprise Intelligence — Demo Flow

## Purpose

This document explains the demonstration flow for the Enterprise Intelligence prototype.

The demo uses a **synthetic vendor-selection scenario** to show how external public information can become verifiable evidence and ultimately support an authorized enterprise decision.

The demonstration does **not** use real confidential vendor submissions.

---

## Scenario

An enterprise is selecting a strategic vendor from three candidates:

* Vendor A
* Vendor B
* Vendor C

The enterprise has confidential information about each vendor, including:

* quoted price
* technical suitability
* commercial terms
* internal evaluation

This information remains inside the enterprise environment.

The prototype adds a separate layer of external intelligence using public Web2 sources.

---

# Demo Workflow

## 1. Create the Decision

Create:

```text
Decision ID: EI-2026-001
Decision: Strategic Vendor Selection
Candidates: Vendor A, Vendor B, Vendor C
```

The decision begins in:

```text
PROPOSED
```

The enterprise's private information remains outside the public evidence workflow.

---

## 2. Discover External Sources

AI Source Intelligence identifies candidate public sources relevant to the vendors.

Example sources include:

```text
Official Regulatory API
Official Corporate Registry
Recognized Business Data Provider
Corporate Website
Established News Source
Unknown Website
```

The prototype evaluates candidate sources using:

* authority
* provenance
* relevance
* freshness
* corroboration

The objective is to determine which sources are suitable candidates for evidence collection.

### Important boundary

AI does **not** establish that a source is absolutely truthful.

It qualifies the source and assigns an evidence suitability classification.

---

## 3. Rank Preferred Sources

The AI produces a source-quality hierarchy.

Example:

```text
Official Regulatory API       PREFERRED
Official Corporate Registry  PREFERRED
Recognized Data Provider     PREFERRED
Corporate Website            SECONDARY
News Source                  SECONDARY
Unknown Website              REJECTED
```

Only appropriate supported sources proceed to the FDC/Web2Json stage.

---

## 4. Request External Data Through FDC/Web2Json

The selected supported source is submitted through the Flare Data Connector using Web2Json.

Conceptually:

```text
Selected Web2 Source
        ↓
Web2Json Request
        ↓
FDC Attestation Process
        ↓
Attested Response + Proof
        ↓
On-chain Verification
```

The application records the resulting evidence commitment for the decision.

### Important technical boundary

FDC does not make the underlying Web2 source inherently truthful.

It provides an attested and verifiable representation of the selected source response.

The application still controls which sources it accepts as appropriate evidence.

---

## 5. Interpret Verified Evidence

After the evidence has passed the verification stage, AI performs its second role.

### AI Evidence Intelligence

It interprets the verified information to produce structured findings such as:

```text
Regulatory Status      → Active
Registration           → Valid
Recent Update          → Yes
External Risk Signal   → Low
Evidence Confidence    → High
```

The AI is therefore an interpretation layer, not the oracle.

---

## 6. Build Vendor Risk Profiles

The evidence is combined with the enterprise decision context to generate structured vendor profiles.

Example:

```text
Vendor A
Overall Risk: LOW
Evidence Confidence: HIGH
Rank: #1

Vendor B
Overall Risk: MEDIUM
Evidence Confidence: HIGH
Rank: #2

Vendor C
Overall Risk: HIGH
Evidence Confidence: MEDIUM
Rank: #3
```

The prototype demonstrates that the recommended vendor is **not necessarily the vendor with the lowest quoted price**.

The decision considers risk-adjusted value.

---

## 7. Apply Enterprise Policy

The recommendation is evaluated against the applicable enterprise policy.

Example:

```text
Policy:
PROCUREMENT-POLICY-V1.2

Minimum Evidence Confidence: 80%
Maximum Permitted Risk: MEDIUM
Executive Approval: REQUIRED
```

The policy engine determines whether the recommendation satisfies the enterprise's decision requirements.

Example:

```text
Vendor A
Evidence Confidence: 92%
Risk: LOW
Policy Result: PASSED
```

---

## 8. Executive Authorization Through Smart Account

AI cannot authorize the enterprise decision.

The authorized executive approves through the configured Smart Account.

The decision transitions:

```text
PROPOSED
    ↓
VERIFIED
    ↓
APPROVED
```

The Smart Account therefore represents the **authority layer**, not the intelligence layer.

---

## 9. Generate the Trust Receipt

After authorization, the system creates a Trust Receipt.

The receipt represents the decision provenance and may contain:

* decision identifier
* vendor candidates
* source assessments
* FDC evidence references
* AI findings
* risk profiles
* policy/version
* authorization information
* execution metadata
* cryptographic commitments

Sensitive receipt contents remain protected.

The expected storage model is:

```text
Detailed Trust Receipt
        ↓
Encrypted / Access Controlled Storage

Cryptographic Commitment
        ↓
On-chain
```

The blockchain does not expose confidential enterprise information merely because the decision is anchored on-chain.

---

## 10. Anchor the Trust Receipt

The Trust Receipt commitment and decision state are recorded in the Enterprise Decision Registry / Trust Receipt Registry architecture.

The resulting lifecycle is:

```text
Decision
   ↓
Verified Evidence
   ↓
Executive Approval
   ↓
Trust Receipt
   ↓
Cryptographic Commitment
   ↓
On-chain Decision State
```

This creates a tamper-evident reference to the historical decision record.

---

## 11. Execute the Decision

An approved decision may transition to:

```text
EXECUTED
```

The current prototype records the execution state.

Future implementations can connect an approved decision to:

* payment
* escrow
* asset release
* other conditional on-chain actions

The prototype does not claim a production enterprise settlement rail unless such functionality is explicitly implemented.

---

# 12. Future Board / Audit Review

The final demonstration illustrates the long-term value of the Trust Receipt.

Assume the original decision was made in 2026.

In 2029, a new board asks:

> **Why was Vendor A selected?**

An authorized reviewer retrieves the Trust Receipt and reconstructs:

```text
What was known
       ↓
What sources were selected
       ↓
What evidence was verified
       ↓
What AI concluded
       ↓
What policy applied
       ↓
Who authorized the decision
       ↓
What happened after approval
```

The organization may later issue a new decision.

However, the historical decision is not silently rewritten.

### Core principle

> **The enterprise can change its future without rewriting its past.**

---

# End-to-End Architecture

```text
                PRIVATE ENTERPRISE DATA
             Price / Technical / Terms
                        │
                        │
                        ▼
                Enterprise Context
                        │
                        │
PUBLIC WEB              │
    │                   │
    ▼                   │
AI Source Intelligence  │
    │                   │
    ▼                   │
Preferred Sources       │
    │                   │
    ▼                   │
FDC / Web2Json          │
    │                   │
    ▼                   │
Verified Evidence       │
    │                   │
    ▼                   │
AI Decision Intelligence
    │                   │
    └─────────┬─────────┘
              ▼
       Enterprise Policy
              │
              ▼
        Smart Account
       Executive Approval
              │
              ▼
     Enterprise Decision
          Contract
              │
        ┌─────┴─────┐
        ▼           ▼
   Trust Receipt   Execution
        │
        ▼
 Cryptographic Commitment
        │
        ▼
   On-chain History
```

---

# Prototype Status

This demo contains a mixture of implemented and demonstration components.

Where a component is simulated, mocked, or represented by placeholder data, the repository should identify that explicitly.

The synthetic vendor dataset in `data/vendors.json` is for demonstration only.

Placeholder transaction hashes, addresses, and evidence commitments are **not live production values** unless replaced with actual deployment data.

The prototype's objective is to demonstrate the architecture and the role of Flare FDC/Web2Json in transforming external Web2 information into evidence that can participate in an authorized enterprise decision workflow.

