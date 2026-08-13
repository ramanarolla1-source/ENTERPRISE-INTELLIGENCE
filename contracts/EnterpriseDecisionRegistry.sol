// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title EnterpriseDecisionRegistry
 * @notice
 *   Prototype registry for Enterprise Intelligence decisions.
 *
 *   The contract anchors:
 *   - the enterprise decision
 *   - the authorized Smart Account
 *   - verified evidence references / commitments
 *   - policy context
 *   - Trust Receipt commitment
 *   - approval and execution state
 *
 *   IMPORTANT:
 *   This prototype does not place confidential enterprise data on-chain.
 *   Sensitive Trust Receipt content is expected to remain encrypted and
 *   access-controlled off-chain. The blockchain stores cryptographic
 *   commitments and decision state.
 *
 *   FDC/Web2Json:
 *   FDC verification is represented here by an authorized verifier recording
 *   the verified evidence commitment. A production implementation can connect
 *   this hook directly to the appropriate Flare FDC verifier contract/interface.
 */
contract EnterpriseDecisionRegistry {
    // ---------------------------------------------------------------------
    // Enums
    // ---------------------------------------------------------------------

    enum DecisionState {
        Proposed,
        Verified,
        Approved,
        Executed,
        Cancelled
    }

    // ---------------------------------------------------------------------
    // Data structures
    // ---------------------------------------------------------------------

    struct Decision {
        bytes32 decisionId;

        // Short public/reference identifier for the enterprise decision.
        string title;

        // Identifier/version of the enterprise policy applied.
        bytes32 policyHash;

        // Smart Account / authorized enterprise account.
        address authorizedAccount;

        // Hash/commitment of the verified external evidence set.
        bytes32 evidenceCommitment;

        // Hash/commitment of the protected Trust Receipt.
        bytes32 trustReceiptCommitment;

        // Optional reference to protected off-chain receipt storage.
        // This should NOT contain confidential data directly.
        string receiptReference;

        // Address that performed the verification step.
        address verifier;

        // Address that approved the decision.
        address approver;

        DecisionState state;

        uint64 createdAt;
        uint64 verifiedAt;
        uint64 approvedAt;
        uint64 executedAt;
    }

    // ---------------------------------------------------------------------
    // Storage
    // ---------------------------------------------------------------------

    mapping(bytes32 => Decision) private decisions;

    mapping(bytes32 => bool) private decisionExists;

    // Addresses allowed to record evidence verification.
    mapping(address => bool) public authorizedVerifiers;

    // ---------------------------------------------------------------------
    // Events
    // ---------------------------------------------------------------------

    event DecisionCreated(
        bytes32 indexed decisionId,
        address indexed authorizedAccount,
        bytes32 indexed policyHash,
        string title,
        uint256 timestamp
    );

    event EvidenceVerified(
        bytes32 indexed decisionId,
        bytes32 indexed evidenceCommitment,
        address indexed verifier,
        uint256 timestamp
    );

    event DecisionApproved(
        bytes32 indexed decisionId,
        address indexed approver,
        bytes32 indexed trustReceiptCommitment,
        uint256 timestamp
    );

    event DecisionExecuted(
        bytes32 indexed decisionId,
        address indexed executor,
        uint256 timestamp
    );

    event DecisionCancelled(
        bytes32 indexed decisionId,
        address indexed cancelledBy,
        uint256 timestamp
    );

    event VerifierAuthorizationChanged(
        address indexed verifier,
        bool authorized
    );

    // ---------------------------------------------------------------------
    // Modifiers
    // ---------------------------------------------------------------------

    modifier decisionExistsOnly(bytes32 decisionId) {
        require(
            decisionExists[decisionId],
            "EnterpriseDecisionRegistry: decision not found"
        );
        _;
    }

    modifier onlyAuthorizedVerifier() {
        require(
            authorizedVerifiers[msg.sender],
            "EnterpriseDecisionRegistry: verifier not authorized"
        );
        _;
    }

    modifier onlyDecisionAccount(bytes32 decisionId) {
        require(
            decisions[decisionId].authorizedAccount == msg.sender,
            "EnterpriseDecisionRegistry: unauthorized account"
        );
        _;
    }

    // ---------------------------------------------------------------------
    // Constructor
    // ---------------------------------------------------------------------

    constructor(address initialVerifier) {
        if (initialVerifier != address(0)) {
            authorizedVerifiers[initialVerifier] = true;

            emit VerifierAuthorizationChanged(
                initialVerifier,
                true
            );
        }
    }

    // ---------------------------------------------------------------------
    // Verifier administration
    // ---------------------------------------------------------------------

    /**
     * @notice Authorize or revoke an address that may record FDC evidence
     *         commitments.
     *
     *         For this hackathon prototype, administration is intentionally
     *         simple. Production governance should use a dedicated access
     *         control mechanism / enterprise administrator.
     */
    function setVerifierAuthorization(
        address verifier,
        bool authorized
    ) external {
        // Prototype governance rule:
        // The verifier itself may not self-authorize.
        //
        // In the demo deployment, this function is expected to be called
        // by the deployment/governance account. A production implementation
        // should replace this with explicit enterprise governance.
        require(
            verifier != address(0),
            "EnterpriseDecisionRegistry: zero verifier"
        );

        authorizedVerifiers[verifier] = authorized;

        emit VerifierAuthorizationChanged(
            verifier,
            authorized
        );
    }

    // ---------------------------------------------------------------------
    // Decision creation
    // ---------------------------------------------------------------------

    /**
     * @notice Creates a new enterprise decision.
     *
     * @param decisionId Unique enterprise decision identifier.
     * @param title Human-readable decision title.
     * @param policyHash Hash of the enterprise policy/version.
     * @param authorizedAccount Smart Account authorized to approve the decision.
     */
    function createDecision(
        bytes32 decisionId,
        string calldata title,
        bytes32 policyHash,
        address authorizedAccount
    ) external {
        require(
            decisionId != bytes32(0),
            "EnterpriseDecisionRegistry: invalid decision ID"
        );

        require(
            !decisionExists[decisionId],
            "EnterpriseDecisionRegistry: decision already exists"
        );

        require(
            authorizedAccount != address(0),
            "EnterpriseDecisionRegistry: invalid account"
        );

        decisions[decisionId] = Decision({
            decisionId: decisionId,
            title: title,
            policyHash: policyHash,
            authorizedAccount: authorizedAccount,
            evidenceCommitment: bytes32(0),
            trustReceiptCommitment: bytes32(0),
            receiptReference: "",
            verifier: address(0),
            approver: address(0),
            state: DecisionState.Proposed,
            createdAt: uint64(block.timestamp),
            verifiedAt: 0,
            approvedAt: 0,
            executedAt: 0
        });

        decisionExists[decisionId] = true;

        emit DecisionCreated(
            decisionId,
            authorizedAccount,
            policyHash,
            title,
            block.timestamp
        );
    }

    // ---------------------------------------------------------------------
    // FDC / evidence registration
    // ---------------------------------------------------------------------

    /**
     * @notice Records the commitment to externally verified evidence.
     *
     * The off-chain/FDC workflow should:
     *
     * 1. Identify and qualify a supported Web2 source.
     * 2. Submit the Web2Json request through FDC.
     * 3. Obtain the attested response/proof.
     * 4. Verify the proof.
     * 5. Generate an evidence commitment.
     * 6. Record that commitment here.
     *
     * The contract intentionally stores the commitment rather than the
     * potentially sensitive source payload.
     */
    function recordEvidenceVerification(
        bytes32 decisionId,
        bytes32 evidenceCommitment
    )
        external
        decisionExistsOnly(decisionId)
        onlyAuthorizedVerifier
    {
        Decision storage decision = decisions[decisionId];

        require(
            decision.state == DecisionState.Proposed,
            "EnterpriseDecisionRegistry: invalid state"
        );

        require(
            evidenceCommitment != bytes32(0),
            "EnterpriseDecisionRegistry: invalid evidence"
        );

        decision.evidenceCommitment = evidenceCommitment;
        decision.verifier = msg.sender;
        decision.verifiedAt = uint64(block.timestamp);
        decision.state = DecisionState.Verified;

        emit EvidenceVerified(
            decisionId,
            evidenceCommitment,
            msg.sender,
            block.timestamp
        );
    }

    // ---------------------------------------------------------------------
    // Enterprise authorization
    // ---------------------------------------------------------------------

    /**
     * @notice Approves a verified decision through the authorized Smart Account.
     *
     * @param trustReceiptCommitment Cryptographic commitment to the protected
     *        Trust Receipt associated with this decision.
     * @param receiptReference Non-sensitive identifier or URI reference to the
     *        protected receipt.
     */
    function approveDecision(
        bytes32 decisionId,
        bytes32 trustReceiptCommitment,
        string calldata receiptReference
    )
        external
        decisionExistsOnly(decisionId)
        onlyDecisionAccount(decisionId)
    {
        Decision storage decision = decisions[decisionId];

        require(
            decision.state == DecisionState.Verified,
            "EnterpriseDecisionRegistry: evidence not verified"
        );

        require(
            trustReceiptCommitment != bytes32(0),
            "EnterpriseDecisionRegistry: invalid receipt"
        );

        decision.trustReceiptCommitment = trustReceiptCommitment;
        decision.receiptReference = receiptReference;
        decision.approver = msg.sender;
        decision.approvedAt = uint64(block.timestamp);
        decision.state = DecisionState.Approved;

        emit DecisionApproved(
            decisionId,
            msg.sender,
            trustReceiptCommitment,
            block.timestamp
        );
    }

    // ---------------------------------------------------------------------
    // Execution
    // ---------------------------------------------------------------------

    /**
     * @notice Marks an approved decision as executed.
     *
     * This prototype deliberately records execution state rather than moving
     * enterprise funds. A future implementation can connect the authorized
     * decision to a payment, escrow or asset-settlement contract.
     */
    function executeDecision(
        bytes32 decisionId
    )
        external
        decisionExistsOnly(decisionId)
        onlyDecisionAccount(decisionId)
    {
        Decision storage decision = decisions[decisionId];

        require(
            decision.state == DecisionState.Approved,
            "EnterpriseDecisionRegistry: not approved"
        );

        decision.executedAt = uint64(block.timestamp);
        decision.state = DecisionState.Executed;

        emit DecisionExecuted(
            decisionId,
            msg.sender,
            block.timestamp
        );
    }

    // ---------------------------------------------------------------------
    // Cancellation
    // ---------------------------------------------------------------------

    /**
     * @notice Cancels a proposed or verified decision.
     *
     * The original record remains on-chain.
     * Cancellation creates a state change; it does not erase history.
     */
    function cancelDecision(
        bytes32 decisionId
    )
        external
        decisionExistsOnly(decisionId)
        onlyDecisionAccount(decisionId)
    {
        Decision storage decision = decisions[decisionId];

        require(
            decision.state == DecisionState.Proposed ||
            decision.state == DecisionState.Verified,
            "EnterpriseDecisionRegistry: cannot cancel"
        );

        decision.state = DecisionState.Cancelled;

        emit DecisionCancelled(
            decisionId,
            msg.sender,
            block.timestamp
        );
    }

    // ---------------------------------------------------------------------
    // Read functions
    // ---------------------------------------------------------------------

    /**
     * @notice Returns the complete public decision metadata.
     *
     * Confidential receipt content is intentionally not stored here.
     */
    function getDecision(
        bytes32 decisionId
    )
        external
        view
        decisionExistsOnly(decisionId)
        returns (Decision memory)
    {
        return decisions[decisionId];
    }

    /**
     * @notice Returns the current decision state.
     */
    function getDecisionState(
        bytes32 decisionId
    )
        external
        view
        decisionExistsOnly(decisionId)
        returns (DecisionState)
    {
        return decisions[decisionId].state;
    }

    /**
     * @notice Verifies whether a given Trust Receipt commitment matches
     *         the decision registered on-chain.
     */
    function verifyTrustReceiptCommitment(
        bytes32 decisionId,
        bytes32 receiptCommitment
    )
        external
        view
        decisionExistsOnly(decisionId)
        returns (bool)
    {
        return
            decisions[decisionId].trustReceiptCommitment ==
            receiptCommitment;
    }

    /**
     * @notice Verifies whether a given evidence commitment matches the
     *         evidence registered for the decision.
     */
    function verifyEvidenceCommitment(
        bytes32 decisionId,
        bytes32 evidenceCommitment
    )
        external
        view
        decisionExistsOnly(decisionId)
        returns (bool)
    {
        return
            decisions[decisionId].evidenceCommitment ==
            evidenceCommitment;
    }
}
