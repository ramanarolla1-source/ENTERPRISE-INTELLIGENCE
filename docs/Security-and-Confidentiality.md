# Security and Confidentiality

## 1. Purpose

Enterprise Intelligence is designed for consequential enterprise decisions where two properties must coexist:

1. **Confidentiality** — sensitive enterprise information must remain protected.
2. **Integrity** — the historical record of a decision must be resistant to silent alteration.

The architecture therefore separates:

**private enterprise information**

from

**public external evidence**

and uses:

**encryption + access control** for confidentiality, and

**cryptographic commitments + on-chain state** for integrity and provenance.

---

# 2. Core Security Model

The system separates responsibilities across several layers:

```text id="7n7jv5"
PUBLIC WEB
    │
    ▼
AI SOURCE INTELLIGENCE
    │
    ▼
FDC / Web2Json
    │
    ▼
VERIFIED EXTERNAL EVIDENCE
    │
    ▼
AI DECISION INTELLIGENCE
    │
    ▼
ENTERPRISE POLICY
    │
    ▼
SMART ACCOUNT
    │
    ▼
DECISION CONTRACT
    │
    ├───────────────┐
    ▼               ▼
TRUST RECEIPT     EXECUTION
    │
    ▼
Encrypted Protected Record
    +
On-chain Commitment
```

No single component is intended to have unlimited authority.

---

# 3. Confidential Enterprise Information

Enterprise Intelligence does not require confidential vendor submissions to become public or to be passed through the public-data verification layer.

Examples include:

* quoted prices;
* technical proposals;
* technical suitability assessments;
* negotiated terms;
* commercial conditions;
* proprietary documents;
* internal evaluation notes;
* internal risk assessments.

These remain under **enterprise-controlled storage and access policies**.

### Confidentiality boundary

```text id="nv6wz9"
CONFIDENTIAL
────────────
Enterprise Data
    │
    ├── Price
    ├── Technical Fit
    ├── Terms
    ├── Proposals
    └── Internal Analysis
    │
    ▼
Enterprise-Controlled Environment


PUBLIC
──────
External Data
    │
    ├── Public APIs
    ├── Registries
    ├── Public Records
    └── Recognized Data Sources
    │
    ▼
AI Source Intelligence
    ↓
FDC / Web2Json
```

The two streams are combined only at the enterprise decision layer.

---

# 4. No Confidential Data on the Public Blockchain

The prototype intentionally avoids storing confidential enterprise information directly on a public blockchain.

Instead:

### Protected layer

Contains the detailed Trust Receipt and sensitive evidence in encrypted form.

### On-chain layer

Contains only the information required to establish integrity and decision provenance, such as:

* decision identifier;
* non-sensitive policy reference;
* evidence commitment;
* Trust Receipt commitment;
* authorization information;
* decision state;
* timestamps;
* execution state.

Conceptually:

```text id="dvj5er"
Sensitive Receipt
      │
      ▼
Encrypted Storage
      │
      │ Hash / Commitment
      ▼
Flare
```

This provides confidentiality without sacrificing historical integrity.

---

# 5. Trust Receipt Security Model

The Trust Receipt represents the protected record of how a decision was made.

It may include:

* source qualification findings;
* FDC evidence references;
* AI analysis;
* risk profiles;
* decision recommendation;
* policy context;
* authorization;
* execution metadata.

The detailed receipt should be encrypted before storage outside the blockchain.

A cryptographic commitment is then created from the canonical receipt representation.

Conceptually:

```text id="spj7sg"
Decision Evidence
       +
AI Findings
       +
Policy
       +
Authorization
       +
Execution
       ↓
Canonical Trust Receipt
       ↓
Encryption
       ↓
Protected Storage

Canonical Trust Receipt
       ↓
Cryptographic Hash / Commitment
       ↓
On-chain Registry
```

If the protected receipt is later retrieved, the organization can recompute the commitment and compare it with the historical on-chain commitment.

A mismatch indicates that the retrieved record is not identical to the record originally committed.

---

# 6. Historical Integrity

The system is designed to preserve **history rather than freeze business decisions forever**.

A decision can later be:

* reviewed;
* challenged;
* superseded;
* revoked;
* replaced by a new authorized decision.

The original record remains intact.

Example:

```text id="7lvp8w"
2026
Decision A
Vendor A Approved
      │
      ▼
Trust Receipt V1
      │
      ▼
On-chain Commitment


2029
New Evidence
      │
      ▼
New Review
      │
      ▼
Decision B
Vendor A Decision Superseded
      │
      ▼
Trust Receipt V2
```

This prevents a later administration from silently rewriting the historical record of the earlier decision.

### Principle

> **The enterprise can change its future without rewriting its past.**

---

# 7. Source Security and Web2Json

Enterprise Intelligence deliberately avoids treating arbitrary Web2 sources as trusted.

AI Source Intelligence evaluates candidate sources before they enter the FDC workflow.

Factors include:

* authority;
* provenance;
* relevance;
* freshness;
* corroboration.

The application then selects an appropriate supported source.

The FDC/Web2Json layer provides an attested representation of the selected source response.

### Important distinction

FDC does **not** establish that an external source is universally truthful.

The architecture instead establishes:

> **This supported source returned this attested response for this request.**

The application must still enforce source-selection and evidence-use policies.

---

# 8. AI Security Boundaries

AI has two distinct roles.

## AI Source Intelligence

Determines which candidate external sources are suitable for the evidence workflow.

It may:

* identify sources;
* assess source characteristics;
* rank sources;
* recommend corroboration.

It must not:

* manufacture evidence;
* bypass source controls;
* declare arbitrary data cryptographically verified.

---

## AI Decision Intelligence

Interprets verified evidence.

It may:

* extract structured findings;
* assess risk dimensions;
* compare candidates;
* recommend a preference order.

It must not:

* alter FDC proof data;
* fabricate supporting evidence;
* bypass enterprise policy;
* independently authorize an enterprise decision;
* independently move enterprise funds.

---

# 9. Separation of Intelligence and Authority

One of the core security principles is:

> **AI recommendation is not authorization.**

The intended sequence is:

```text id="amjgxq"
AI Recommendation
       ↓
Enterprise Policy
       ↓
Authorization Required
       ↓
Authorized Executive
       ↓
Smart Account
       ↓
Decision Contract
```

This limits the authority of the AI system.

Even if an AI recommendation is incorrect, the enterprise still retains an explicit human authorization boundary.

---

# 10. Smart Account Security

The Smart Account acts as the controlled enterprise authority for the decision.

The account should be governed according to the organization's authorization model.

The prototype demonstrates the conceptual separation between:

**AI intelligence**

and

**executive authorization**.

A production implementation should additionally consider:

* role-based permissions;
* approval thresholds;
* multi-signature governance;
* account recovery;
* key rotation;
* separation of duties;
* transaction simulation;
* emergency revocation.

These are production-governance extensions and are not all implemented by the current prototype.

---

# 11. Decision Contract Security

The `EnterpriseDecisionRegistry` contract provides explicit state transitions.

The prototype lifecycle is:

```text id="qrl6zu"
PROPOSED
    ↓
VERIFIED
    ↓
APPROVED
    ↓
EXECUTED
```

Invalid transitions should be rejected by contract-level conditions.

For example:

* an unverified decision cannot be approved;
* an unapproved decision cannot be executed;
* a nonexistent decision cannot be queried;
* a decision cannot be silently deleted.

The objective is to move important decision-state rules from informal application logic into an independently verifiable contract.

---

# 12. Trust Receipt Access Control

The blockchain cannot make public data private.

Therefore, the prototype treats access control as a separate layer.

The `TrustReceiptRegistry` can record which addresses are authorized by the application to access a protected receipt.

However:

> **The authorization mapping itself does not encrypt the receipt.**

Actual confidentiality must be provided by:

* encrypted storage;
* secure key management;
* identity/authentication;
* enterprise access-control infrastructure.

The blockchain provides an auditable authorization record and integrity commitment, not private storage.

---

# 13. Data Integrity

The system uses commitments to connect off-chain records with on-chain history.

Important commitments may include:

```text id="a96vvk"
Evidence Commitment
Trust Receipt Commitment
Decision Commitment
```

If a receipt or evidence record is modified after commitment, its newly calculated hash should no longer match the on-chain commitment.

This provides tamper detection.

---

# 14. Replay and Duplication Considerations

Decision identifiers should be unique.

The prototype contract prevents duplicate decision IDs and duplicate Trust Receipt IDs.

The decision model also preserves version information so that a subsequent review can create a new receipt rather than overwriting an earlier one.

Conceptually:

```text id="x19xy5"
Decision ID: EI-2026-001

Receipt V1
     ↓
Receipt V2
     ↓
Receipt V3
```

Each version remains part of the historical chain.

---

# 15. Evidence Integrity

The evidence pipeline should preserve enough metadata to establish:

* source identifier;
* source request context;
* relevant Web2Json request;
* attestation/proof reference;
* extracted value;
* normalization rules;
* evidence commitment;
* associated decision ID.

This enables the enterprise to distinguish:

**raw external response**

from

**normalized evidence**

from

**AI interpretation**

from

**final decision**.

That separation is important for future review.

---

# 16. Data Minimization

Enterprise Intelligence should collect and retain only the information needed for the decision.

For public data:

* extract only relevant fields;
* avoid unnecessarily storing complete responses;
* preserve evidence references and commitments where appropriate.

For private enterprise data:

* keep confidential material within the enterprise environment;
* avoid unnecessary duplication;
* avoid placing sensitive material on public networks.

---

# 17. Confidentiality vs Immutability

The system deliberately separates two security properties.

### Confidentiality

> **Who can see the information?**

Implemented through encryption, identity, access control and protected storage.

### Integrity

> **Can we prove that the recorded information has not been silently altered?**

Implemented through cryptographic commitments and on-chain decision history.

These properties should not be conflated.

```text id="70gd3m"
CONFIDENTIALITY
Encryption + Access Control
          │
          ▼
   Protected Receipt


INTEGRITY
Cryptographic Commitment
          │
          ▼
   On-chain Record
```

---

# 18. Future Board / Auditor Verification

A future authorized executive or auditor can retrieve the protected Trust Receipt and independently verify its historical commitment.

Conceptually:

```text id="w6trgz"
Retrieve Protected Receipt
          ↓
Decrypt / Authenticate
          ↓
Canonicalize Receipt
          ↓
Calculate Commitment
          ↓
Compare with On-chain Commitment
          ↓
MATCH
```

A successful match establishes that the retrieved record corresponds to the committed historical record.

The reviewer can then reconstruct:

* available evidence;
* selected sources;
* FDC evidence references;
* AI findings;
* applicable policy;
* approval;
* execution state.

---

# 19. Threat Model

The prototype is designed with the following potential threats in mind.

### Threat: AI hallucination

**Mitigation:** AI cannot generate FDC evidence or independently authorize decisions.

### Threat: Low-quality Web2 source

**Mitigation:** AI source qualification, source policy, supported-source controls and optional corroboration.

### Threat: Altered Trust Receipt

**Mitigation:** cryptographic commitment anchored on-chain.

### Threat: Unauthorized approval

**Mitigation:** Smart Account / explicit authorization boundary.

### Threat: Confidential data exposure

**Mitigation:** keep sensitive enterprise information outside the public evidence pipeline and public chain; use encryption and access control.

### Threat: Historical record rewriting

**Mitigation:** append-only on-chain decision history and receipt versioning.

### Threat: Incorrect application interpretation

**Mitigation:** preserve source evidence references, AI findings, policy context and decision provenance for later review.

---

# 20. Prototype Limitations

This repository is a **hackathon prototype**, not a production enterprise security system.

The following areas require further engineering for production:

* enterprise identity integration;
* secure key management;
* production encryption infrastructure;
* hardware-backed key storage;
* multi-party approval;
* formal contract audits;
* production FDC source governance;
* complete Web2Json request lifecycle;
* production monitoring and alerting;
* secure confidential-compute implementation;
* enterprise retention and compliance policies.

Placeholder hashes, addresses and synthetic data must not be interpreted as production security controls.

---

# 21. Security Principle

The overall security model can be summarized as:

> **Private information stays protected. Public evidence is independently qualified and attested. AI interprets but does not hold authority. Smart Accounts control authorization. Cryptographic commitments protect historical integrity. On-chain state preserves the decision history.**

This allows Enterprise Intelligence to combine AI, external data and blockchain without treating any individual component as an absolute source of truth or unlimited authority.

