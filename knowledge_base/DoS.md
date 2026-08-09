# DoS

## Executive Summary
Denial of Service (DoS) attacks originate from a single source and aim to exhaust a target's resources or exploit protocol weaknesses to degrade or disable service availability.

## Description
Unlike distributed variants, DoS attacks are launched from one host, exploiting connection handling, resource limits, or application logic (e.g., slow HTTP attacks, SYN floods from a single source) to overwhelm the target with fewer but often more targeted requests.

## Objectives
Disable or degrade a specific service, application, or host, potentially to cause outages or as a diversion for other malicious activity.

## Attack Lifecycle
Target reconnaissance → vulnerability/resource-limit identification → attack tool configuration → sustained single-source flooding or slow-attack execution → resource exhaustion.

## Typical Network Behaviour
- Traffic pattern: sustained, high-frequency requests from a single source.
- Packet characteristics: variable depending on technique — small repetitive packets (floods) or deliberately slow, minimal-data packets (slow attacks).
- Communication behavior: many connections or requests concentrated on one target from one origin.
- Session behavior: connections may be intentionally held open (slow attacks) or rapidly cycled (floods).
- Protocol usage: HTTP, TCP SYN, or application-specific protocols depending on attack type.
- Timing: either extremely rapid (flooding) or deliberately delayed (slow-rate attacks like Slowloris).
- Flow characteristics: forward-heavy flows with limited legitimate backward response as the target struggles to respond.

## Indicators of Compromise (IoCs)
- Network: high request rate or abnormally long-held connections from a single IP.
- Host: elevated CPU/memory/connection table usage tied to one source.
- Behavioral: service degradation correlating with sustained single-source activity.
- Log-based: web/application server logs showing repeated requests or incomplete request patterns from one origin.

## MITRE ATT&CK Mapping
- Tactic: Impact — Technique: Endpoint Denial of Service (T1499), including sub-techniques for application or OS exhaustion floods. Relevant as it captures single-source resource exhaustion targeting a specific endpoint.

## Detection Methods
Connection rate thresholds, IDS/IPS signature detection for known DoS tool patterns, SIEM correlation of single-source resource exhaustion, and ML-based anomaly detection on request timing and flow duration.

## Explainable AI Feature Interpretation
`Bwd Packet Length Std` and `Bwd Packet Length Mean` are often distinctive, as target responses under stress become abnormal or minimal. `Idle Mean`/`Idle Max` can be significant for slow-rate attacks that deliberately introduce delays. `Flow Bytes/s` and `Flow Packets/s` are typically elevated relative to benign traffic but less extreme than distributed variants. `Max Packet Length` and `Fwd Packet Length Std` help differentiate flooding (uniform packets) from slow attacks (minimal, irregular packets).

## Severity Assessment
- Confidentiality Impact: None to Low
- Integrity Impact: Low
- Availability Impact: High
- Overall Severity: High
- Business Impact: Service disruption for affected application or host, potential SLA impact.

## Recommended Mitigation
Connection timeout tuning, rate limiting, load balancing, Web Application Firewall (WAF) rules against slow-rate attacks, and IPS signatures for known DoS tools.

## Incident Response
Preparation (timeout hardening, WAF rules) → Detection (resource/connection anomaly alerts) → Containment (block source, adjust connection limits) → Eradication (patch exploited weakness) → Recovery (service restoration) → Lessons Learned (capacity/configuration review).

## SOC Analyst Investigation Guide
Identify the single source IP and request pattern, correlate with server resource metrics, determine attack subtype (flood vs. slow-rate), and confirm whether the target application has known DoS-relevant misconfigurations.

## Common False Positives
Misbehaving legitimate clients (retry loops, broken automation scripts) can generate DoS-like patterns from a single source; verify source legitimacy and intent before escalation.

## AI Incident Report Context
The flow reflects sustained, resource-intensive activity from a single source consistent with a denial-of-service attempt targeting the availability of the destination service.

## References
MITRE ATT&CK, NIST, CISA, OWASP.
