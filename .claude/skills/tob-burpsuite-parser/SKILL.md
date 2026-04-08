---
name: tob-burpsuite-parser
description: Trail of Bits: parse Burp Suite project files — extract findings, requests, responses
---

# Tob Burpsuite Parser — MAARS Security Reference

## Overview
Trail of Bits: parse Burp Suite project files — extract findings, requests, responses

## Core Approach
Trail of Bits methodology: systematic, thorough, adversarial mindset. Document everything.

## Key Questions
- What are the trust boundaries and attack surfaces?
- What assumptions does the code make about inputs?
- Where is user-controlled data used in security-sensitive operations?
- What are the worst-case failure modes?

## Best Practices
1. Understand the system before finding bugs
2. Look for classes of vulnerabilities, not just individual bugs
3. Test properties and invariants, not just happy paths
4. Document findings with reproduction steps and impact analysis
5. Prioritize by exploitability and impact

## Common Vulnerability Classes
- Access control failures
- Integer arithmetic errors (overflow, underflow, truncation)
- Reentrancy and state confusion
- Insecure randomness and timing attacks
- Input validation and injection flaws
- Cryptographic misuse

## Tools
- Semgrep: pattern-based static analysis
- Slither/Echidna: Solidity analysis and fuzzing
- Hypothesis: property-based testing in Python
- Burp Suite: web application security testing

## Models to Use
- Security analysis: claude-opus-4-6
- Rule writing: claude-sonnet-4-6
- Quick lookups: claude-haiku-4-5-20251001
