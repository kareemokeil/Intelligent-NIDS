# Brute Force

## Executive Summary
Brute force attacks involve systematic, repeated authentication attempts against a service (commonly SSH or FTP) to guess valid credentials.

## Description
An attacker submits many username/password combinations sequentially or in parallel against an authentication endpoint, relying on weak, reused, or default credentials. Attacks may be dictionary-based or exhaustive, and can target a single account or spray across many accounts.

## Objectives
Gain unauthorized access to a system or service to enable further exploitation, lateral movement, or data theft.

## Attack Lifecycle
Target/service identification → credential list preparation → automated login attempts → success detection → session establishment → post-access activity.

## Typical Network Behaviour
- Traffic pattern: high-frequency, repetitive connection attempts to a single service port.
- Packet characteristics: small, uniform packet sizes corresponding to login request/response exchanges.
- Communication behavior: rapid sequential TCP connections, often from a single or small set of source IPs.
- Session behavior: many short-lived sessions, most terminating quickly after failed authentication.
- Protocol usage: concentrated on authentication protocols (SSH/22, FTP/21, RDP/3389).
- Timing: attempts occur at machine-driven speed, far exceeding human typing pace.
- Flow characteristics: near-symmetric small flows repeated at high frequency.

## Indicators of Compromise (IoCs)
- Network: repeated connection attempts to the same authentication port from one source.
- Host: multiple failed login entries in authentication logs within a short window.
- Behavioral: attempts spanning many usernames or many passwords against few accounts.
- Log-based: authentication service logs showing sequential failure patterns followed by an anomalous success.

## MITRE ATT&CK Mapping
- Tactic: Credential Access — Technique: Brute Force (T1110), including sub-techniques Password Guessing and Password Spraying. Relevant because the traffic pattern directly reflects automated credential-guessing behavior.

## Detection Methods
IDS/IPS threshold rules on failed logins, SIEM correlation of authentication failures per source/account, account lockout policies, and ML models detecting abnormal login attempt frequency.

## Explainable AI Feature Interpretation
`act_data_pkt_fwd` and `Total Length of Fwd Packets` tend to be low and repetitive, reflecting short credential-submission packets. `Fwd Packet Length Mean`/`Max` often show low variance due to standardized login request formats. `Flow Packets/s` may be elevated relative to benign authentication due to attempt frequency, while `Bwd Header Length` can reflect consistent server response structure (e.g., repeated "authentication failed" responses).

## Severity Assessment
- Confidentiality Impact: High (if successful)
- Integrity Impact: Medium
- Availability Impact: Low
- Overall Severity: High
- Business Impact: Potential full account or system compromise if credentials are guessed successfully.

## Recommended Mitigation
Account lockout thresholds, multi-factor authentication, rate limiting, IP allow-listing for administrative services, and strong password policy enforcement.

## Incident Response
Preparation (MFA, lockout policy) → Detection (failed login correlation) → Containment (block source IP, lock affected account) → Eradication (credential reset) → Recovery (restore access securely) → Lessons Learned (review exposed services).

## SOC Analyst Investigation Guide
Review authentication logs for failure/success ratios, identify source IP reputation, confirm whether any login ultimately succeeded, and check for post-authentication activity on the targeted account.

## Common False Positives
Misconfigured applications or expired credentials generating repeated legitimate failed logins can resemble brute force; correlate with user context before escalation.

## AI Incident Report Context
The flow pattern reflects repeated, automated authentication attempts against a single service, consistent with a credential brute-force attack targeting the exposed authentication endpoint.

## References
MITRE ATT&CK, NIST SP 800-63, OWASP, SANS.
