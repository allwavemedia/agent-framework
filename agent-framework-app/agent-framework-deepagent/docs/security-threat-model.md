# Security Threat Model (Initial)

| ID | Threat | Vector | Impact | Likelihood | Mitigation | Status |
|----|--------|--------|--------|------------|------------|--------|
| T1 | Sandbox Escape | Malicious Python code | Host compromise | Medium | Docker isolation + read-only FS + resource limits | Planned |
| T2 | Prompt Injection | User-crafted prompt manipulates code gen | Rogue code generation | High | Input sanitization + allow‐list for generation templates | Planned |
| T3 | Secret Exposure | Misconfigured env or logs | Credential leakage | Medium | Redact secrets in logs, env var scanning in CI | Planned |
| T4 | Brute Force Auth (Epic2) | Repeated login attempts | Account takeover | Medium | Rate limiting (future), uniform error messages | Planned |
| T5 | Workflow Poisoning | Persisted malicious workflow reused | Subsequent compromise | Low | Validation on load + code static checks | Planned |
| T6 | Denial via Large Graph | Oversized workflow graph | Resource exhaustion | Medium | Enforce node/edge limits + request size caps | Planned |
| T7 | Insecure Checkpoint Data | Tampering with persisted state | Execution integrity loss | Low | Signed / hashed checkpoint metadata | Future |

## Notes
- Will expand with STRIDE categorization later.
- Each mitigation should map to tests (security or integration) when implemented.
