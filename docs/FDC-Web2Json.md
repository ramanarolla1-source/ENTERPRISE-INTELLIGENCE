# FDC / Web2Json

## 1. Purpose

Enterprise Intelligence uses **Flare Data Connector (FDC) Web2Json** as its external evidence-verification layer.

The problem is straightforward:

> Enterprise decisions often depend on information that exists outside the blockchain in public Web2 systems.

Examples include:

* regulatory APIs
* corporate registries
* public business databases
* recognized data providers
* other supported public Web2 endpoints

The application must not simply allow an AI model to retrieve this information and treat its output as trusted evidence.

Instead, Enterprise Intelligence separates:

**source qualification → data attestation → AI interpretation → enterprise decision**

FDC/Web2Json provides the attestation layer in that sequence.

---

# 2. What Web2Json Does

Web2Json allows a supported Web2 API response to be brought into the FDC attestation workflow.

At a high level:

```text id="t7ixu2"
Web2 API
   ↓
Web2Json Request
   ↓
FDC Attestation Process
   ↓
Attested Response
   ↓
Proof
   ↓
On-chain Verification
```

The consuming application can then use the verified result as an input to its decision logic.

The important distinction is:

> **FDC verifies the attested response associated with the request. It does not establish that the external source is inherently truthful.**

That distinction is fundamental to Enterprise Intelligence.

---

# 3. Why Enterprise Intelligence Uses Web2Json

Without an evidence-verification layer, a conventional AI workflow might look like:

```text id="q3tt8m"
Web2 Source
    ↓
AI
    ↓
"Vendor appears safe"
```

The enterprise is still trusting the application's data retrieval and AI interpretation pipeline.

Enterprise Intelligence instead uses:

```text id="yd1h82"
Candidate Web2 Sources
        ↓
AI Source Intelligence
        ↓
Selected Supported Source
        ↓
FDC / Web2Json
        ↓
Attested Response
        ↓
Verified Evidence
        ↓
AI Decision Intelligence
        ↓
Enterprise Policy
```

This creates a deliberate separation between:

**what the source reported**

and

**what the AI concludes from that information.**

---

# 4. Source Qualification Happens Before FDC

Enterprise Intelligence does not treat every public website as an acceptable evidence source.

AI Source Intelligence evaluates candidate sources according to factors including:

### Authority

Who operates or publishes the source?

### Provenance

Can the origin of the information be established?

### Relevance

Is this source appropriate for the particular enterprise decision?

### Freshness

How current is the information?

### Corroboration

Is the information supported by other relevant sources?

The output is a source classification such as:

```text id="7m2r9g"
PREFERRED
SECONDARY
CONTEXT ONLY
REJECTED
```

Only a suitable supported source proceeds to the FDC/Web2Json stage.

### Important principle

> **AI recommends source suitability; FDC provides attestation; the enterprise application remains responsible for source policy.**

---

# 5. Web2Json Request

A Web2Json request identifies the target Web2 resource and the transformation required to extract the relevant data.

Conceptually:

```text id="3r7q8u"
Source URL
    +
JQ Transformation
    +
ABI Type / Encoding
    ↓
Web2Json Request
```

The transformation identifies the portion of the response that the application needs for its decision.

For example, an API may return a large JSON response while the application requires only:

```json
{
  "registration_status": "active"
}
```

The Web2Json request can define the transformation needed to obtain the relevant structured value.

The exact request schema and ABI encoding should follow the current Flare FDC/Web2Json implementation and the supported network configuration.

---

# 6. FDC Attestation Process

The request is then processed through the Flare Data Connector attestation workflow.

Conceptually:

```text id="4c2kqt"
Web2Json Request
       ↓
FDC Providers
       ↓
Response Collection
       ↓
Consensus / Attestation
       ↓
Merkle Root / Proof
       ↓
Verifiable Result
```

The important architectural property is that the application does not rely solely on a single off-chain component returning a value.

The FDC architecture provides a consensus-based attestation mechanism through which the resulting data can be proven to the consuming application.

---

# 7. Proof Verification

The application can verify the resulting proof against the relevant FDC verification mechanism.

Conceptually:

```text id="d9z5p2"
Attested Response
       +
Proof
       +
Expected Request / Source Context
       ↓
FDC Verification
       ↓
VALID
```

The resulting evidence can then be referenced by the Enterprise Intelligence decision pipeline.

### Application-level source validation

A valid FDC proof does not eliminate the need for application-level source controls.

The consuming system should ensure that:

* the requested source is the intended source;
* the source is an approved source for the decision;
* the expected data structure is satisfied;
* the response is relevant to the decision;
* the evidence is not being misinterpreted outside its intended context.

This is why **AI Source Intelligence** remains a separate layer.

---

# 8. Evidence Commitment

After verification, Enterprise Intelligence can create a cryptographic commitment representing the evidence used by the decision.

Conceptually:

```text id="j90g5x"
Verified FDC Evidence
        ↓
Normalized Evidence Object
        ↓
Cryptographic Commitment
        ↓
Enterprise Decision Registry
```

The prototype does not need to store the complete external response on-chain.

Instead, the system can preserve:

* evidence commitment;
* FDC/proof reference;
* source identifier;
* decision identifier;
* relevant metadata.

The detailed protected evidence can remain in the enterprise-controlled evidence/Trust Receipt system.

---

# 9. Example

Assume Enterprise Intelligence needs to assess a vendor's regulatory status.

### Candidate sources

```text id="jpt8aa"
Official Regulatory API
Corporate Website
News Source
Unknown Industry Website
```

AI Source Intelligence might rank them:

```text id="7o4c2f"
Official Regulatory API       PREFERRED
Corporate Website             SECONDARY
News Source                   SECONDARY
Unknown Website               REJECTED
```

The preferred supported source is selected.

### Web2Json

```text id="aq6u6c"
Request:
Official Regulatory API

Required field:
registration.status

Expected result:
"active"
```

The FDC process produces an attested response and corresponding proof.

The application verifies the proof.

The evidence layer can then produce:

```text id="9mptqv"
Verified External Evidence

registration.status = active
verification = valid
source = approved regulatory API
```

AI Decision Intelligence can then interpret the evidence:

```text id="m5wcvf"
Regulatory Risk:
LOW

Evidence Confidence:
HIGH

Decision Relevance:
POSITIVE
```

The final enterprise decision still depends on the enterprise policy and other evidence.

---

# 10. FDC Is Not the AI

The architecture intentionally keeps these responsibilities separate.

### AI Source Intelligence

> **Which external sources are suitable candidates?**

### FDC / Web2Json

> **What did the selected supported source return, according to the attestation?**

### AI Decision Intelligence

> **What does the verified evidence mean?**

### Enterprise Policy

> **Does the evidence satisfy the organization's decision rules?**

### Smart Account

> **Who is authorized to approve the decision?**

### Decision Contract

> **What state/action is permitted and recorded?**

This separation is one of the central architectural principles of Enterprise Intelligence.

---

# 11. Web2Json and Confidentiality

Web2Json is used for **public external information**.

Enterprise Intelligence does not expose private vendor submissions through Web2Json.

Private information such as:

* quoted price;
* proprietary technical proposals;
* negotiated terms;
* internal evaluation;
* confidential commercial conditions

remains in the enterprise-controlled environment.

The intended boundary is:

```text id="ydl95p"
PUBLIC DATA
    ↓
AI Source Intelligence
    ↓
FDC / Web2Json
    ↓
Verified Evidence


PRIVATE DATA
    ↓
Enterprise-Controlled Environment
    ↓
Decision Context
```

The two streams can be combined at the enterprise decision layer without exposing the private stream through the public-data verification pipeline.

---

# 12. Why Not Treat the Web2 Source as "Truth"?

The project deliberately avoids the statement:

> "FDC makes the website trustworthy."

That would be too broad.

The actual model is:

```text id="2jkqkz"
Source suitability
       ↓
AI qualification
       ↓
Supported source selection
       ↓
FDC/Web2Json attestation
       ↓
Verifiable response
       ↓
AI interpretation
       ↓
Enterprise decision
```

This means the project treats external information as **evidence with provenance**, not as unquestionable truth.

The enterprise can also require corroboration or multiple sources when the risk of a single-source decision is unacceptable.

---

# 13. Why Web2Json Is Central to the Project

The project is designed around the proposition that enterprise intelligence should not depend entirely on information already stored on-chain.

The important information often remains in:

**registries, APIs, public records and Web2 data services.**

Web2Json creates the bridge:

```text id="kqp2m9"
External Web2
     ↓
    FDC
     ↓
Flare-verifiable evidence
     ↓
Enterprise Intelligence
     ↓
Authorized on-chain decision
```

This is the project's principal Flare integration.

The project therefore does not use FDC as a decorative blockchain feature.

**The external evidence workflow depends on it.**

---

# 14. Current Prototype Boundary

The repository may use synthetic sources, placeholder commitments, and demonstration responses.

These should not be interpreted as live FDC attestations unless explicitly identified as such.

A production deployment requires:

* supported/appropriate Web2Json sources;
* correct request construction;
* current FDC network configuration;
* actual attestation retrieval;
* correct proof verification;
* production-grade source governance.

The prototype separates the architecture from the deployment-specific configuration so that those details can be replaced without changing the core decision model.

---

# 15. Security Considerations

### Source validation

The consuming application must validate that the verified response corresponds to an approved source/request.

### Response determinism

Web2Json requests should use supported sources and response structures appropriate for the FDC attestation process.

### Data minimization

Only the information necessary for the decision should be extracted.

### Confidentiality

Sensitive enterprise information should not be written to the public blockchain.

### Commitment integrity

Evidence and Trust Receipt commitments should be generated from canonicalized data so the same protected record produces the expected commitment.

### AI boundaries

AI should not be permitted to:

* bypass source controls;
* manufacture evidence;
* directly authorize a decision;
* directly execute settlement without policy and authorization.

---

# 16. End-to-End Example

```text id="8c6v6m"
Public Regulatory API
        ↓
AI Source Intelligence
        ↓
Source classified as PREFERRED
        ↓
FDC / Web2Json Request
        ↓
FDC Attestation
        ↓
Proof Verification
        ↓
Verified Regulatory Evidence
        ↓
AI Decision Intelligence
        ↓
Vendor Risk Profile
        ↓
Enterprise Policy
        ↓
Executive Approval
        ↓
Smart Account
        ↓
Trust Receipt
        ↓
Cryptographic Commitment
        ↓
Enterprise Decision Registry
```

---

# 17. Core Principle

The role of Web2Json in Enterprise Intelligence can be summarized as:

> **Web2Json does not make the external world inherently trustworthy. It gives the enterprise application a verifiable attestation of what a selected supported Web2 source returned, so that AI and enterprise policy can reason over evidence with a stronger provenance boundary.**

That distinction is central to the design and should remain consistent throughout the codebase, demo, and submission.

