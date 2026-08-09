# BENIGN

## Executive Summary
Represents normal, non-malicious network traffic. Serves as the baseline class against which all attack categories are differentiated by the classifier.

## Description
Benign traffic reflects legitimate user and application activity: web browsing, file transfers, authenticated sessions, DNS resolution, and standard client-server communication. It exhibits consistent, protocol-compliant behavior without the volumetric, timing, or structural anomalies associated with malicious activity.

## Objectives
Not applicable — this class represents the absence of malicious intent.

## Attack Lifecycle
Not applicable.

## Typical Network Behaviour
- Traffic pattern: bursty but proportionate to user actions; request/response symmetry is typical.
- Packet characteristics: packet sizes vary naturally with payload content (e.g., HTML, images, API responses).
- Communication behavior: bidirectional exchange with expected handshake and teardown sequences.
- Session behavior: sessions have coherent start/end boundaries and reasonable duration relative to activity.
- Protocol usage: standard ports and protocols (HTTP/S, DNS, SMTP) used as intended.
- Timing: inter-arrival times reflect human or application-driven pacing, not automated repetition.
- Flow characteristics: balanced forward/backward byte ratios for typical request-response protocols.

## Indicators of Compromise (IoCs)
Not applicable — absence of IoCs is itself a benign indicator.

## MITRE ATT&CK Mapping
Not applicable.

## Detection Methods
Benign traffic is confirmed by the *absence* of anomaly scores across IDS, SIEM correlation rules, and ML classifiers. Statistical baselining (establishing "normal" traffic profiles) is the primary mechanism used to contrast benign behavior against attack classes.

## Explainable AI Feature Interpretation
For benign predictions, contributing features typically show moderate, non-extreme values: `Bwd Packet Length Std` and `Fwd Packet Length Std` remain within typical variance (no extreme uniformity or extreme spread), `Flow Bytes/s` and `Flow Packets/s` align with expected throughput for the protocol in use, and `Idle Mean`/`Idle Max` reflect natural pauses in user-driven interaction rather than fixed automated intervals. `act_data_pkt_fwd` and `Bwd IAT Total` tend to show organic variability rather than the rigid patterns seen in scripted or automated attack traffic.

## Severity Assessment
- Confidentiality Impact: None
- Integrity Impact: None
- Availability Impact: None
- Overall Severity: None
- Business Impact: None

## Recommended Mitigation
No mitigation required. Continued baseline monitoring ensures benign profiles remain accurate as legitimate usage patterns evolve.

## Incident Response
Not applicable.

## SOC Analyst Investigation Guide
Confirm classification confidence is high and cross-check against recent baseline drift. If a benign classification coincides with unusual business context (e.g., off-hours activity from a sensitive account), consider manual review despite the model's output.

## Common False Positives
Legitimate but unusual traffic (large file uploads, scheduled backups, software updates, VPN reconnections) can occasionally resemble anomalous patterns and should be correlated with asset/business context before dismissal.

## AI Incident Report Context
The observed flow was classified as benign with characteristics consistent with normal application or user-driven network activity. No indicators of malicious behavior were identified across packet timing, size distribution, or flow symmetry.

## References
MITRE ATT&CK, NIST SP 800-61, SANS Reading Room.
