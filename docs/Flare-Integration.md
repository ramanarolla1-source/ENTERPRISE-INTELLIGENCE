# Flare Integration

## 1. Overview

Enterprise Intelligence is designed around a specific Flare capability:

> **Bringing externally available Web2 information into a programmable on-chain decision workflow.**

The primary Flare primitive used by the prototype is the **Flare Data Connector (FDC), specifically the Web2Json attestation type**.

Flare describes FDC as an enshrined oracle for validating external data for Flare's EVM state, while Web2Json is designed to fetch and process JSON returned by supported Web2 sources and make the resulting data verifiable for on-chain consumption.

Enterprise Intelligence builds an application layer around that capability:

```text
External Web2 Information
            ↓
    AI Source Intelligence
            ↓
     FDC / Web2Json
            ↓
    Verified External Evidence
            ↓
    AI Decision Intelligence
            ↓
     Enterprise Policy
            ↓
     Smart Account Authority
            ↓
   Decision / Trust Receipt
            ↓
     On-chain Decision State
```

---

# 2. Why Flare?

Enterprise decisions frequently depend on information that does not originate on-chain.

Examples include:

* public regulatory information;
* corporate registrations;
* public business records;
* recognized data-provider APIs;
* other public Web2 information relevant to a vendor or counterparty.

A conventional AI workflow can retrieve such information, but the application still has to determine:

1. which source should be used;
2. what the source actually returned;
3. whether that response can be independently verified;
4. how the evidence should influence the decision.

Flare's FDC provides the external-data attestation layer needed for this workflow.

Flare's current developer documentation explicitly positions FDC for external data and identifies Web2Json as the mechanism for fetching and processing supported Web2 JSON data.

---

# 3. Primary Flare Primitive — FDC / Web2Json

Enterprise Intelligence uses **Web2Json** to bring selected public Web2 information into the FDC attestation process.

The current Web2Json request structure includes:

* URL;
* HTTP method;
* headers;
* query parameters;
* body;
* JQ post-processing filter;
* ABI signature for the returned structured data.

The conceptual flow is:

```text
Supported Web2 Source
        ↓
Web2Json Request
        ↓
FDC Attestation
        ↓
Attested Response
        ↓
Proof / Merkle Path
        ↓
On-chain Verification
```

Flare's documentation describes proof verification against the on-chain Merkle root and the use of a hybrid design in which complete datasets are not stored directly on-chain.

---

# 4. Source Qualification Before FDC

FDC does not decide which website or API should be trusted for an enterprise decision.

Enterprise Intelligence therefore introduces an **AI Source Intelligence** layer before FDC.

AI evaluates candidate sources using:

* authority;
* provenance;
* relevance;
* freshness;
* corroboration;
* source consistency.

The output is a preferred source hierarchy:

```text
PREFERRED
     ↓
SECONDARY
     ↓
CONTEXT ONLY
     ↓
REJECTED
```

Only a suitable supported source is selected for the Web2Json workflow.

This creates a deliberate separation:

> **AI qualifies the source. FDC attests the response.**

That is the central technical distinction of the project.

---

# 5. Web2Json Does Not Make the Internet "Truthful"

Enterprise Intelligence deliberately avoids the claim:

> "FDC makes a website trustworthy."

The actual proposition is narrower and technically defensible:

> **FDC provides an attested and verifiable representation of the response associated with a selected supported Web2 request.**

The application must still control:

* which source it considers appropriate;
* what data field is relevant;
* whether the source is supported;
* whether the response satisfies expected schema and policy;
* whether additional corroboration is required.

This is why source qualification and FDC are separate layers.

---

# 6. Evidence Interpretation After FDC

Once the external response has been attested and verified, AI performs a second function.

### AI Decision Intelligence

It interprets the verified response and may produce:

* structured findings;
* risk dimensions;
* evidence confidence;
* vendor or counterparty comparisons;
* recommended preference ordering.

The resulting architecture is:

```text
AI Source Intelligence
        ↓
"Which source should we use?"
        ↓
FDC / Web2Json
        ↓
"What did the selected source return?"
        ↓
AI Decision Intelligence
        ↓
"What does that evidence mean?"
        ↓
Enterprise Policy
        ↓
"Does it satisfy our rules?"
```

This prevents the AI model from becoming the oracle, decision authority, and executor at the same time.

---

# 7. Smart Account Integration

Enterprise Intelligence uses **Smart Account authority as the authorization layer**.

The conceptual sequence is:

```text
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
Enterprise Decision Contract
```

The Flare Smart Accounts architecture provides account-abstraction functionality for XRPL users and includes a proof-based workflow in which an FDC attestation can be submitted to the `MasterAccountController` before a personal account performs the encoded action.

For Enterprise Intelligence, the important design principle is broader:

> **AI intelligence and enterprise authority remain separate.**

AI may recommend a vendor.

The authorized enterprise actor must approve the decision.

---

# 8. Decision Contract Integration

The prototype includes:

```text
contracts/EnterpriseDecisionRegistry.sol
```

The contract anchors decision metadata and commitments such as:

* decision ID;
* policy reference;
* authorized account;
* evidence commitment;
* Trust Receipt commitment;
* approval state;
* execution state;
* timestamps.

The intended decision lifecycle is:

```text
PROPOSED
    ↓
VERIFIED
    ↓
APPROVED
    ↓
EXECUTED
```

The blockchain therefore provides programmable decision state rather than functioning only as a passive audit database.

---

# 9. Trust Receipt Integration

The **Trust Receipt** is the project's long-lived decision-provenance layer.

The protected receipt can contain:

* source assessments;
* FDC evidence references;
* AI findings;
* risk profiles;
* policy context;
* executive authorization;
* execution metadata.

Sensitive content remains encrypted and access-controlled.

The on-chain layer anchors the relevant cryptographic commitment and decision metadata.

Conceptually:

```text
Detailed Trust Receipt
        ↓
Encrypted Protected Storage
        ↓
Cryptographic Commitment
        ↓
Flare
```

This gives the enterprise a mechanism to establish that the protected decision record retrieved years later corresponds to the record committed at the time of approval.

---

# 10. Why This Is Interoperability

Enterprise Intelligence demonstrates **information interoperability**.

The information lifecycle crosses three environments:

```text
           WEB2
     External Information
            │
            ▼
          FLARE
   FDC / Web2Json
            │
            ▼
      Verifiable Evidence
            │
            ▼
       AI + Enterprise
          Decision
            │
            ▼
   Programmable On-chain
          Action
```

The project is therefore not using Flare merely as a generic EVM deployment environment.

Flare provides the bridge through which supported external information can become verifiable input to a programmable application.

Flare's developer hub explicitly positions the network for **data-intensive, interoperable applications** and identifies FDC as an enshrined protocol for external data.

---

# 11. Why We Use FDC / Web2Json Instead of Adding Unnecessary Flare Features

The prototype deliberately does not add FTSO, FAssets, or other Flare primitives merely to increase the number of integrations.

FDC/Web2Json is central because the core problem begins with:

> **external public information that must become usable as evidence in a consequential enterprise decision.**

Flare's current grant criteria explicitly highlight meaningful integration of its enshrined data oracles, including FDC for retrieving data from **other blockchains and the internet**.

Our use of FDC therefore addresses the core problem rather than serving as a decorative blockchain integration.

---

# 12. Mainnet / Testnet Considerations

The current Flare documentation identifies **Web2Json as available on Coston and Coston2**, while the broader FDC supports additional attestation types and environments.

Accordingly, the repository must clearly distinguish between:

### Demonstration configuration

Synthetic sources, placeholder commitments, and simulated responses.

### Live testnet integration

Actual supported Web2Json requests, attestation retrieval and proof verification on the appropriate Flare test environment.

### Production configuration

Whitelisted/supported sources, production network configuration, application governance and enterprise-grade key management.

The repository should never imply that a demonstration placeholder is a live FDC proof.

---

# 13. Contract Address Handling

Where the application interacts with Flare's official protocol contracts, contract addresses should be resolved through the **Flare Contract Registry** rather than hardcoded.

Flare's documentation identifies the registry as the trusted source for resolving protocol contract addresses and specifically lists contracts such as `FdcHub` in the registry.

This reduces the risk of relying on stale or incorrect off-chain contract-address configuration.

---

# 14. Flare Ecosystem Value

Enterprise Intelligence demonstrates a potential non-crypto-native use case for Flare's external-data infrastructure.

The application consumes the external-data capability of FDC and transforms it into enterprise utility:

```text
Public Web2 Data
       ↓
     FDC
       ↓
Verifiable Evidence
       ↓
Enterprise Intelligence
       ↓
Authorized Decision
       ↓
On-chain State / Action
```

This creates a path from enterprise information workflows into programmable blockchain infrastructure.

At the ecosystem level, this aligns with Flare's positioning around data-intensive and interoperable applications and its emphasis on meaningful use of enshrined data protocols.

---

# 15. Future Flare Extensions

The current MVP intentionally focuses on FDC/Web2Json.

The architecture can later incorporate additional Flare capabilities where they solve a real business requirement.

Potential extensions include:

### Confidential Compute

Private enterprise information or sensitive decision computations could be processed using an appropriate confidential execution architecture.

### Interoperable Assets

An approved decision could eventually control an asset-facing workflow involving Flare-connected assets.

### Conditional Settlement

Verified evidence could become a prerequisite for:

* payment;
* escrow release;
* asset transfer;
* other on-chain execution.

These are **extensions**, not claims that the current MVP already implements them.

---

# 16. Integration Summary

Enterprise Intelligence uses Flare in the following way:

| Flare capability            | Role                                                                   |
| --------------------------- | ---------------------------------------------------------------------- |
| **FDC / Web2Json**          | External Web2 data attestation and proof                               |
| **Flare EVM**               | Programmable decision state and execution                              |
| **Smart Accounts**          | Controlled enterprise authorization model                              |
| **Flare Contract Registry** | Reliable resolution of official protocol contract addresses            |
| **Future extensions**       | Confidential computation, interoperable assets, conditional settlement |

The primary integration is intentionally focused:

> **FDC/Web2Json is the critical Flare primitive because external evidence is the critical input to the decision.**

---

# 17. Core Integration Principle

The Enterprise Intelligence Flare integration can be summarized in one sentence:

> **Flare turns external information into verifiable input for a programmable enterprise decision workflow; AI interprets that evidence, authorized humans control the decision, and the resulting provenance can be anchored on-chain.**

The objective is not to force enterprises into crypto-native workflows.

The objective is to demonstrate why **Flare's data and programmable execution infrastructure can become useful to enterprises whose most important information still lives outside the blockchain.**

