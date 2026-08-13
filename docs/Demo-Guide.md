# Enterprise Intelligence — Demo Guide

## 1. Purpose

This guide explains how to reproduce the Enterprise Intelligence demonstration.

The demo shows how an enterprise can combine:

**Confidential enterprise information + public external intelligence → AI source qualification → FDC/Web2Json evidence verification → AI decision intelligence → enterprise policy → Smart Account authorization → Trust Receipt → on-chain decision provenance**

The demonstration uses **synthetic vendor data** and is intended to illustrate the architecture rather than represent a production procurement system.

---

# 2. Demo Scenario

The enterprise must select a strategic vendor from:

```text id="u8n1j2"
Vendor A
Vendor B
Vendor C
```

The enterprise has private information about each vendor:

* quoted price
* technical suitability
* commercial terms
* internal evaluation

This information is treated as confidential and remains within the enterprise-controlled environment.

The system supplements that information with independently assessed public external intelligence.

---

# 3. Repository Components Used in the Demo

The demonstration uses:

```text id="2q0m9q"
data/
├── sources.json
├── vendors.json
└── sample_decision.json

src/
├── source_intelligence.py
├── evidence_pipeline.py
├── decision_engine.py
├── trust_receipt.py
└── pipeline.py

contracts/
└── EnterpriseDecisionRegistry.sol
```

Supporting architectural explanations are available under `docs/`.

---

# 4. Run the Demonstration

## Prerequisites

Recommended environment:

* Python 3.10+
* Git
* Node.js / Solidity tooling if interacting with the contract locally
* A Flare-compatible test environment if performing live FDC or contract verification

Create a Python environment:

```bash
python -m venv .venv
```

Activate it.

### Linux / macOS

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

---

# 5. Synthetic Data

The demo uses synthetic data so that no real vendor or confidential enterprise information is exposed.

The three vendors are defined in:

```text
data/vendors.json
```

Public data sources are defined in:

```text
data/sources.json
```

The complete demonstration decision is represented in:

```text
data/sample_decision.json
```

---

# 6. Step 1 — Source Intelligence

The first stage is source qualification.

Conceptually:

```text id="yt9w1p"
Candidate Web2 Sources
        ↓
AI Source Intelligence
        ↓
Authority
Provenance
Relevance
Freshness
Corroboration
        ↓
Preferred / Secondary / Context / Rejected
```

The AI does not declare a website absolutely truthful.

It determines which sources are appropriate candidates for the evidence workflow.

Example:

```text id="2mrj5a"
Official Regulatory API       PREFERRED
Official Corporate Registry  PREFERRED
Recognized Data Provider     PREFERRED
Corporate Website            SECONDARY
News Source                  SECONDARY
Unknown Website              REJECTED
```

---

# 7. Step 2 — FDC / Web2Json

A preferred supported public source is selected for the external-data verification step.

The intended flow is:

```text id="g4t0o4"
Selected Web2 Source
        ↓
Web2Json Request
        ↓
FDC Attestation Process
        ↓
Attested Response + Proof
        ↓
Application Verification
        ↓
Evidence Commitment
```

The repository treats this as an important trust boundary.

### FDC does not:

* declare a website inherently trustworthy;
* determine which vendor should be selected;
* replace enterprise policy;
* replace AI interpretation.

### FDC does:

> Provide an attested, verifiable representation of the selected supported Web2 response.

---

# 8. Step 3 — Evidence Interpretation

Once the external response has been verified, AI performs its second role.

Example:

```text id="m7skx6"
Verified Evidence

Regulatory Status: Active
Registration: Valid
Recent Update: Yes
External Risk Signal: Low
Evidence Confidence: High
```

AI converts verified evidence into structured enterprise intelligence.

Example output:

```text id="hy7e2a"
Vendor A
Overall Risk: LOW
Confidence: 0.92
Rank: #1

Vendor B
Overall Risk: MEDIUM
Confidence: 0.87
Rank: #2

Vendor C
Overall Risk: HIGH
Confidence: 0.79
Rank: #3
```

---

# 9. Step 4 — Enterprise Policy

The recommendation is evaluated against enterprise rules.

Example:

```text id="4e5f6v"
Policy: PROCUREMENT-POLICY-V1.2

Minimum Evidence Confidence: 80%
Maximum Permitted Risk: MEDIUM
Executive Approval: REQUIRED
```

The policy engine evaluates whether the recommendation is eligible for authorization.

For the demonstration:

```text id="0s8fko"
Vendor A
Risk: LOW
Evidence Confidence: 92%

Policy Result:
PASSED
```

---

# 10. Step 5 — Smart Account Authorization

AI can recommend a decision but does not have independent enterprise authority.

The authorized executive approves through the Smart Account.

Conceptually:

```text id="p94j6x"
AI Recommendation
        ↓
Enterprise Policy
        ↓
Eligible for Approval
        ↓
Authorized Executive
        ↓
Smart Account
        ↓
Decision Contract
```

The on-chain decision lifecycle becomes:

```text id="3kqccf"
PROPOSED
    ↓
VERIFIED
    ↓
APPROVED
```

---

# 11. Step 6 — Trust Receipt

The Trust Receipt preserves the decision provenance.

A demonstration receipt contains:

```text id="j3l7x9"
Decision ID
Vendor Candidates
Source Assessments
FDC Evidence References
AI Findings
Risk Profile
Policy Version
Authorization
Execution State
Timestamp
Cryptographic Commitments
```

Sensitive information is not intentionally exposed on-chain.

The expected storage model is:

```text id="4nc2qq"
Detailed Receipt
      ↓
Encrypted / Access-Controlled Storage

Receipt Commitment
      ↓
On-Chain Registry
```

---

# 12. Step 7 — On-Chain Decision Registry

The prototype contract is:

```text
contracts/EnterpriseDecisionRegistry.sol
```

Its purpose is to anchor the public decision metadata and cryptographic commitments.

Key lifecycle:

```text id="xq7h9m"
Decision Created
      ↓
Evidence Verified
      ↓
Decision Approved
      ↓
Decision Executed
```

The contract also preserves historical state when a decision is cancelled or superseded.

It does not erase the historical record.

---

# 13. Step 8 — Long-Term Audit Scenario

The final part of the demonstration illustrates the institutional-memory use case.

Assume the original decision was made in 2026.

Three years later, a new board asks:

> **Why was Vendor A selected?**

The authorized reviewer retrieves the Trust Receipt and reconstructs:

```text id="p0u9z2"
What was known
      ↓
Which sources were selected
      ↓
What evidence was verified
      ↓
What AI concluded
      ↓
Which enterprise policy applied
      ↓
Who approved the decision
      ↓
What happened after approval
```

A later board may issue a new decision.

The original record remains part of the historical decision chain.

### Core principle

> **The enterprise can change its future without rewriting its past.**

---

# 14. Demonstrating the Flare Connection

The most important part of the demo is not simply showing a smart contract.

The demonstrator should make the following relationship clear:

```text id="7me6m3"
External Web2 Information
          ↓
   AI Source Intelligence
          ↓
     FDC / Web2Json
          ↓
    Verified Evidence
          ↓
   AI Decision Intelligence
          ↓
   Enterprise Policy
          ↓
    Smart Account
          ↓
 Decision Contract / Trust Receipt
```

This is the project's principal Flare contribution:

> **External Web2 information becomes verifiable input to a programmable enterprise decision workflow.**

---

# 15. Live vs Demonstration Components

The repository should clearly distinguish between live and illustrative components.

### Live / implemented

Only describe a component as live when the repository and deployed environment actually demonstrate it.

### Demonstration / simulated

The synthetic vendor dataset, placeholder commitments, example sources, and simulated responses may be used to demonstrate the workflow.

### Conceptual extensions

Examples include:

* full production enterprise key management;
* Confidential Compute integration;
* continuous monitoring;
* payment settlement;
* escrow;
* asset release;
* production-grade multi-party governance.

These should not be represented as implemented features unless they are actually deployed.

---

# 16. FDC / Web2Json Technical Honesty

A live Web2Json deployment requires appropriate supported/whitelisted sources and a response that can participate in the FDC attestation process.

Therefore, example URLs in this repository are illustrative unless explicitly replaced with live supported endpoints.

The demo should never imply:

> “Any website can automatically become trusted.”

The accurate architecture is:

> **AI qualifies the source → the selected supported source is requested through FDC/Web2Json → the resulting response is attested → the application verifies the proof → AI interprets the verified evidence.**

---

# 17. What the Demo Proves

The demonstration is designed to prove five things:

### 1. External information can become structured enterprise evidence.

### 2. AI can qualify sources and interpret evidence without becoming the oracle.

### 3. FDC/Web2Json provides the external-data verification layer.

### 4. Human authority remains separate from AI recommendation.

### 5. A consequential enterprise decision can have long-lived, tamper-evident provenance.

---

# 18. Expected Demonstration Result

The demonstration should conclude with:

```text id="kq3e3e"
Decision ID:
EI-2026-001

Recommended Vendor:
Vendor A

Risk:
LOW

Evidence Confidence:
HIGH

Policy:
PASSED

Executive Authorization:
APPROVED

Trust Receipt:
ANCHORED

Decision State:
EXECUTED
```

The important conclusion is not merely:

> **Vendor A was selected.**

It is:

> **The enterprise can demonstrate why Vendor A was selected, what evidence supported that decision, who authorized it, and that the historical decision record has not been silently rewritten.**

---

# 19. Demo Walkthrough Video

The repository's accompanying product demonstration follows this sequence:

**Problem → Confidentiality Boundary → AI Source Intelligence → FDC/Web2Json → AI Evidence Intelligence → Vendor Risk Profile → Enterprise Policy → Smart Account → Trust Receipt → On-Chain Decision → Future Board Review**

See the project README for the high-level architecture and product overview.

