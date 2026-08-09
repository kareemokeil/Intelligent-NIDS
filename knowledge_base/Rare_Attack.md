# Rare Attack

## Executive Summary
This category aggregates low-frequency, heterogeneous attack types (e.g., infiltration attempts and exploitation of specific vulnerabilities such as Heartbleed-style flaws) that occur too infrequently in the training data to be modeled as individual classes reliably.

## Description
Because the underlying attacks in this group differ significantly in mechanism (e.g., internal network infiltration versus a specific cryptographic vulnerability exploit), this class should be treated as a flag for manual review rather than a single well-defined behavior. Common underlying patterns include unauthorized internal access attempts and exploitation of specific protocol/implementation vulnerabilities.

## Objectives
Varies by underlying attack — may include establishing an internal foothold (infiltration) or extracting sensitive memory contents via a vulnerable service (e.g., Heartbleed-style exploitation).

## Attack Lifecycle
Highly variable; infiltration typically follows initial access → internal reconnaissance → lateral movement, while vulnerability exploitation follows vulnerability discovery → crafted malicious request → data or memory leakage.

## Typical Network Behaviour
- Traffic pattern: irregular and inconsistent across instances due to heterogeneous attack mechanisms.
- Packet characteristics: may include abnormally malformed or crafted packets exploiting specific protocol handling flaws.
- Communication behavior: often originates from within the network (infiltration) or targets a specific vulnerable service directly.
- Session behavior: sessions may appear legitimate initially before deviating (e.g., malformed heartbeat requests).
- Protocol usage: varies; TLS/heartbeat protocols relevant for vulnerability-based exploits.
- Timing: no consistent pattern given the class's heterogeneity.
- Flow characteristics: no single consistent profile; requires case-by-case analysis.

## Indicators of Compromise (IoCs)
- Network: unexpected internal-to-internal connections; malformed protocol requests.
- Host: unauthorized access to systems not normally reached by the source.
- Behavioral: activity inconsistent with the source host's typical role or baseline.
- Log-based: application logs showing malformed requests or unexpected memory/data responses.

## MITRE ATT&CK Mapping
- Tactic: Initial Access / Credential Access — varies by specific sub-case; general association with T1190 (Exploit Public-Facing Application) for vulnerability-based cases and Lateral Movement tactics for infiltration cases.

## Detection Methods
Given heterogeneity, detection relies on anomaly-based ML classification (as used here), manual SOC review, vulnerability scanning for known CVEs, and behavioral baselining to flag deviations from expected host roles.

## Explainable AI Feature Interpretation
Because this class merges dissimilar attacks, feature importance varies significantly by instance. `Total Length of Fwd Packets` and `Fwd Packet Length Max` may spike for vulnerability-exploitation payloads carrying crafted data. `Bwd IAT Total` and `Idle Max` can reflect irregular session timing inconsistent with either normal traffic or well-defined attack classes. Analysts should treat SHAP explanations for this class as investigative starting points rather than definitive attack signatures.

## Severity Assessment
- Confidentiality Impact: Potentially Critical (data/memory leakage scenarios)
- Integrity Impact: Variable
- Availability Impact: Low to Medium
- Overall Severity: High (due to uncertainty and potential critical underlying causes)
- Business Impact: Uncertain but potentially severe; treat as high priority pending investigation.

## Recommended Mitigation
Immediate manual triage, vulnerability patching for known exploit classes (e.g., OpenSSL Heartbleed), internal network segmentation to limit infiltration impact, and enhanced logging on sensitive internal systems.

## Incident Response
Preparation (asset patching, internal monitoring) → Detection (anomaly flag from ML classifier) → Containment (isolate affected host/segment) → Eradication (patch vulnerability or remove unauthorized access) → Recovery (validate system integrity) → Lessons Learned (root cause the specific rare event).

## SOC Analyst Investigation Guide
Given the ambiguous nature of this class, prioritize full packet capture review, correlate with vulnerability scanner results, verify source/destination legitimacy against network architecture, and escalate to senior analysts for manual classification.

## Common False Positives
Legitimate but unusual internal administrative traffic or non-standard application behavior can trigger this classification; always validate against asset ownership and business justification before treating as confirmed malicious.

## AI Incident Report Context
The flow was classified into a low-frequency, heterogeneous attack category requiring manual analyst review, as its characteristics do not clearly align with a single well-established attack pattern.

## References
MITRE ATT&CK, NIST, CISA, OpenSSL Security Advisories.
