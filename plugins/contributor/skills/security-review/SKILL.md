---
name: security-review
description: >-
  FTC security review checks. Activates when reviewing code for credential leaks,
  unsafe file operations, or code injection vulnerabilities in FTC robot code.
  Use when auditing skills for security issues, checking for hardcoded credentials,
  or reviewing scripts for safe file operations.
license: MIT
compatibility: Claude Code, Codex CLI, VS Code Copilot, Cursor
metadata:
  author: ncssm-robotics
  version: "1.0.0"
  category: tools
allowed-tools: Read, Glob, Grep
---

# FTC Security Review Checks

This skill defines security-focused checks for FTC marketplace skills. These checks help prevent credential leaks, unsafe file operations, and code injection vulnerabilities.

## FTC IP Address Whitelist

These IP addresses are ALLOWED and should NOT be flagged:

| IP Address | Purpose |
|------------|---------|
| `192.168.43.1` | Control Hub default IP |
| `192.168.49.1` | Robot Controller phone (WiFi Direct) |
| `localhost` | Local development |
| `127.0.0.1` | Local loopback |

Any other hardcoded IP addresses should be flagged for review.

## Credential Checks (Errors)

These must pass - credential leaks are serious security issues.

### API Keys and Tokens
- [ ] No hardcoded API keys (`api_key`, `apikey`, `api-key`)
- [ ] No hardcoded tokens (`token`, `auth_token`, `access_token`)
- [ ] No hardcoded secrets (`secret`, `secret_key`, `client_secret`)

### Passwords and Credentials
- [ ] No hardcoded passwords (`password`, `passwd`, `pwd`)
- [ ] No hardcoded PINs or codes
- [ ] No WiFi credentials (`ssid`, `wpa`, `psk`, `wifi_password`)

### Team-Specific Credentials
- [ ] No team-specific API keys or tokens
- [ ] No competition registration credentials
- [ ] No cloud service credentials

## Configuration Safety (Warnings)

### IP Address Usage
- [ ] Only whitelisted FTC IPs used (see whitelist above)
- [ ] Non-whitelisted IPs flagged for review
- [ ] IP addresses are configurable where possible

### Robot Configuration
- [ ] Robot config uses hardware map, not literals
- [ ] Motor/servo ports referenced by name, not number
- [ ] Team number configurable (not hardcoded)

## File Operation Safety (Warnings)

### Path Safety
- [ ] No absolute file paths in scripts (`/home/`, `/Users/`, `C:\`)
- [ ] No path traversal patterns (`../../../`)
- [ ] Scripts use relative paths from project root

### File Access
- [ ] File operations use safe path joining
- [ ] No arbitrary file read/write based on user input
- [ ] Temporary files use system temp directory

## Code Injection Prevention (Errors)

### Dynamic Code Execution
- [ ] No `eval()` of user input
- [ ] No `exec()` of dynamic content
- [ ] No `Runtime.exec()` with unsanitized input

### Shell Command Safety
- [ ] Shell commands don't include user input directly
- [ ] Command arguments are properly escaped
- [ ] No string concatenation for shell commands

### SQL Safety (if applicable)
- [ ] Parameterized queries used
- [ ] No string concatenation in SQL
- [ ] Input sanitized before database operations

## Network Safety (Info)

### External Communications
- [ ] No HTTP requests to non-FTC domains
- [ ] No websocket connections to external servers
- [ ] No data collection or telemetry to unknown endpoints

### Data Handling
- [ ] No exfiltration of local data
- [ ] No transmission of system information
- [ ] No automatic uploads without user consent

## Script-Specific Checks

### Python Scripts
- [ ] No `subprocess.call(shell=True)` with user input
- [ ] `pickle.load()` only on trusted data
- [ ] No `__import__()` with dynamic names

### Shell Scripts
- [ ] Variables quoted properly (`"$var"` not `$var`)
- [ ] No `eval` of user-provided data
- [ ] Input validation before use

## Common Vulnerabilities

| Vulnerability | Example | Fix |
|--------------|---------|-----|
| Hardcoded credential | `API_KEY = "abc123"` | Use environment variable |
| Command injection | `os.system(f"ls {user_input}")` | Use subprocess with list args |
| Path traversal | `open("../../../etc/passwd")` | Validate and sanitize paths |
| Arbitrary IP | `connect("192.168.1.100")` | Use configurable setting |

## FTC-Specific Considerations

### Safe Practices
- Robot Controller IP (192.168.43.1) is expected and safe
- Hardware map lookups are the correct pattern
- Configuration files in project directory are appropriate

### Review Carefully
- Scripts that download external content
- Code that accesses file system outside project
- Network connections to non-standard ports

## Running This Review

```bash
/contributor:review <skill-name> --type security
```

Or as part of full review:
```bash
/contributor:review <skill-name>
```
