# PortScan

## Executive Summary
Port scanning is a reconnaissance technique used to identify open ports and active services on a target host, typically as a precursor to further exploitation.

## Description
An attacker (or automated tool) systematically probes a range of ports on one or more hosts to determine which are open, closed, or filtered, revealing running services and potential attack surface. Scans may be sequential, randomized, or stealthy (e.g., SYN/half-open scans) to evade detection.

## Objectives
Map the target's exposed services and identify potential vulnerabilities to plan subsequent exploitation or lateral movement.

## Attack Lifecycle
Target identification → port range selection → scan execution (full connect, SYN, or stealth scan) → service/version fingerprinting → vulnerability mapping → follow-on attack planning.

## Typical Network Behaviour
- Traffic pattern: sequential or rapid connection attempts across many ports on one or few hosts.
- Packet characteristics: minimal payload; primarily TCP SYN or connection-initiation packets.
- Communication behavior: numerous short-lived, often incomplete connection attempts.
- Session behavior: many sessions terminate immediately after initial handshake or without full completion (in stealth scans).
- Protocol usage: predominantly TCP, occasionally UDP for service discovery.
- Timing: attempts can be rapid (aggressive scans) or deliberately spaced (stealth scans) to avoid threshold-based detection.
- Flow characteristics: minimal or absent backward data flow, since most probed ports do not respond meaningfully.

## Indicators of Compromise (IoCs)
- Network: sequential connection attempts across a wide port range from one source.
- Host: firewall logs showing rejected/reset connections across many ports.
- Behavioral: absence of legitimate application-layer data following connection attempts.
- Log-based: IDS alerts for scan signatures; repeated RST/ICMP unreachable responses.

## MITRE ATT&CK Mapping
- Tactic: Discovery — Technique: Network Service Discovery (T1046). Directly relevant as the technique describes probing for accessible network services, matching port scan behavior precisely.

## Detection Methods
IDS signature and threshold-based scan detection, firewall connection-attempt correlation, SIEM aggregation of failed connections per source, and ML models detecting abnormal port-access diversity per source IP.

## Explainable AI Feature Interpretation
`Min Packet Length` and `Max Packet Length` are often minimal and tightly clustered, reflecting near-empty probe packets. `Bwd Packet Length Mean`/`Std` tend to be low or near-zero due to the absence of substantive responses from closed or filtered ports. `act_data_pkt_fwd` is typically low since scans rarely carry application payload. `Flow Packets/s` may be elevated for aggressive scans, while `Bwd Header Length` reflects consistent minimal response structures (e.g., repeated RST packets).

## Severity Assessment
- Confidentiality Impact: Low (direct), but enables future high-impact attacks
- Integrity Impact: None (direct)
- Availability Impact: Low
- Overall Severity: Medium
- Business Impact: Precursor risk — successful scans often precede targeted exploitation attempts.

## Recommended Mitigation
Firewall rules limiting exposed ports, network segmentation, IDS/IPS scan detection rules, and honeypot deployment to detect and delay reconnaissance.

## Incident Response
Preparation (minimize exposed attack surface) → Detection (scan pattern alerts) → Containment (block source IP) → Eradication (not typically required beyond blocking) → Recovery (resume normal monitoring) → Lessons Learned (review unnecessarily exposed services).

## SOC Analyst Investigation Guide
Identify the scanning source, determine scan scope (single host vs. subnet-wide) and technique (full connect vs. stealth), and check whether any scanned port returned a substantive response indicating a viable target for further attack.

## Common False Positives
Legitimate vulnerability assessment tools or monitoring systems performing authorized scans can resemble malicious port scanning; verify against approved scanning schedules and source IPs.

## AI Incident Report Context
The flow pattern indicates systematic probing across multiple ports on the target host, consistent with reconnaissance activity aimed at identifying exposed services for potential exploitation.

## References
MITRE ATT&CK, NIST, SANS, Cisco.
