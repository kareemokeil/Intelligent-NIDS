# Web Attack

## Executive Summary
Web attacks encompass exploitation attempts against web applications, including Cross-Site Scripting (XSS), SQL Injection, and brute-force attempts against web login forms, targeting application-layer vulnerabilities rather than network infrastructure.

## Description
Attackers craft malicious HTTP requests to manipulate application logic, inject unauthorized code, or extract data from backend databases. Unlike network-layer attacks, web attacks exploit insufficient input validation or insecure application design.

## Objectives
Extract sensitive data (SQL Injection), hijack user sessions or deliver malicious scripts to victims (XSS), or gain unauthorized application access.

## Attack Lifecycle
Application reconnaissance (identifying input fields/parameters) → payload crafting → injection attempt → response analysis for success indicators → data extraction or session compromise.

## Typical Network Behaviour
- Traffic pattern: HTTP/S requests with anomalous parameter values or payload structures.
- Packet characteristics: request packets may be larger than typical due to injected payloads or encoded scripts.
- Communication behavior: standard HTTP request-response cycle, but with malformed or suspicious payload content.
- Session behavior: sessions may appear normal until a specific malicious request is submitted.
- Protocol usage: HTTP/HTTPS almost exclusively.
- Timing: often a mix of manual probing (irregular timing) and automated scanning tools (regular timing).
- Flow characteristics: forward flow may show elevated byte length for requests carrying injected payloads.

## Indicators of Compromise (IoCs)
- Network: HTTP requests containing SQL syntax, script tags, or encoded payloads.
- Host: web server error logs indicating malformed queries or unexpected application errors.
- Behavioral: repeated requests to the same endpoint with varying payloads (fuzzing pattern).
- Log-based: WAF logs flagging injection signatures; application logs showing database errors correlated with specific requests.

## MITRE ATT&CK Mapping
- Tactic: Initial Access — Technique: Exploit Public-Facing Application (T1190). Relevant as web attacks directly target internet-facing application vulnerabilities to gain unauthorized access or extract data.

## Detection Methods
Web Application Firewall (WAF) signature and anomaly detection, IDS pattern matching for injection strings, SIEM correlation of application error spikes, and ML classification based on payload structure and request characteristics.

## Explainable AI Feature Interpretation
`Fwd Packet Length Max` and `Total Length of Fwd Packets` can be elevated due to injected payloads (e.g., long SQL strings or script content) embedded in requests. `Average Packet Size` may deviate from typical HTTP request profiles when payloads are unusually long or encoded. `Fwd Packet Length Std` can increase due to variable payload lengths during automated fuzzing attempts. `Bwd Packet Length Mean` may reflect application error responses, which often differ in size from normal successful responses.

## Severity Assessment
- Confidentiality Impact: High (data exposure via SQLi)
- Integrity Impact: Medium to High
- Availability Impact: Low
- Overall Severity: High
- Business Impact: Potential data breach, regulatory exposure, and reputational damage.

## Recommended Mitigation
Web Application Firewall deployment, input validation and parameterized queries, regular security testing (SAST/DAST), and least-privilege database access configuration.

## Incident Response
Preparation (WAF rules, secure coding practices) → Detection (WAF/IDS alerts) → Containment (block malicious source, disable vulnerable endpoint if needed) → Eradication (patch application vulnerability) → Recovery (restore affected data/service) → Lessons Learned (code review and testing improvements).

## SOC Analyst Investigation Guide
Review WAF and application logs for injection signatures, identify affected endpoints and parameters, determine whether any request returned unauthorized data, and assess database query logs for anomalous access patterns.

## Common False Positives
Legitimate requests containing special characters (e.g., apostrophes in names, code snippets in support tickets) can trigger injection-pattern alerts; validate against application context before confirming malicious intent.

## AI Incident Report Context
The flow contains HTTP request characteristics consistent with a web application attack attempt, potentially involving injection or scripting payloads targeting the destination application.

## References
OWASP, MITRE ATT&CK, NIST, Microsoft Security.
