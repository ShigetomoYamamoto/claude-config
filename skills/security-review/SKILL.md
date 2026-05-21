---
name: security-review
description: Use this skill when adding authentication, handling user input, working with secrets, creating API endpoints, or implementing payment/sensitive features. Provides comprehensive security checklist and patterns.
---

# Security Review Skill

This skill ensures all code follows security best practices and identifies potential vulnerabilities.

## When to Activate

- Implementing authentication or authorization
- Handling user input or file uploads
- Creating new API endpoints
- Working with secrets or credentials
- Implementing payment features
- Storing or transmitting sensitive data
- Integrating third-party APIs

## Security Checklist

### 1. Secrets Management

#### ❌ NEVER
- Hardcode API keys, passwords, or tokens in source files
- Commit `.env` files with real secrets
- Store credentials in version-controlled configuration files

#### ✅ ALWAYS
- Load secrets from environment variables
- Fail fast with a clear error if a required secret is missing
- Add `.env` and credential files to `.gitignore`
- Store production secrets in the hosting platform's secret manager

#### Verification
- [ ] No hardcoded API keys, tokens, or passwords
- [ ] All secrets loaded from environment variables
- [ ] `.env` files in `.gitignore`
- [ ] No secrets in git history

### 2. Input Validation

#### Principles
- Validate all user input at system boundaries (API endpoints, form submissions)
- Use schema validation libraries available in the project's language
- Whitelist allowed values rather than blacklisting forbidden ones
- Error messages must not reveal internal structure

#### File Upload Validation
- Check file size (enforce a maximum)
- Check MIME type against an allowlist
- Check file extension against an allowlist
- Store uploads outside the web root or in object storage

#### Verification
- [ ] All user inputs validated with a schema or explicit checks
- [ ] File uploads restricted by size, type, and extension
- [ ] No user input passed directly to queries or shell commands
- [ ] Error messages do not leak sensitive information

### 3. Injection Prevention

#### SQL / NoSQL Injection
- ALWAYS use parameterized queries or the ORM's query builder
- NEVER concatenate user input into query strings

#### Command Injection
- NEVER pass user input directly to shell commands
- Use language-native libraries instead of spawning shell processes

#### Verification
- [ ] All database queries use parameterized queries or ORM
- [ ] No string concatenation in queries
- [ ] No shell command execution with user-controlled input

### 4. Authentication & Authorization

#### Token Handling
- Store session tokens in httpOnly, Secure, SameSite=Strict cookies (not in client-accessible storage)
- Validate tokens on every protected request
- Use short expiry times with refresh token rotation

#### Authorization
- Check permissions before every sensitive operation
- Verify the requesting user owns or has access to the requested resource
- Apply the principle of least privilege

#### Database-Level Access Control
- Enable row-level security if supported by the database
- Never expose database credentials to client-side code

#### Verification
- [ ] Tokens stored securely (httpOnly cookies or equivalent)
- [ ] Authorization checked before every sensitive operation
- [ ] Database access control policies enabled
- [ ] Role-based access control implemented

### 5. XSS Prevention

- Sanitize user-provided HTML before rendering (use a sanitization library)
- Prefer safe text rendering over raw HTML injection
- Set Content-Security-Policy headers
- Rely on framework-native escaping (most modern frameworks escape by default)

#### Verification
- [ ] User-provided HTML sanitized before rendering
- [ ] CSP headers configured
- [ ] Framework's built-in escaping used

### 6. CSRF Protection

- Use CSRF tokens on state-changing requests (POST, PUT, DELETE, PATCH)
- Set SameSite=Strict on session cookies
- Verify Origin/Referer headers on sensitive state-changing endpoints

#### Verification
- [ ] CSRF tokens on state-changing operations
- [ ] SameSite=Strict on session cookies

### 7. Rate Limiting

- Apply rate limiting on all API endpoints
- Apply stricter limits on sensitive operations (authentication, search, financial actions)
- Rate limit per IP and per authenticated user

#### Verification
- [ ] Rate limiting on all API endpoints
- [ ] Stricter limits on sensitive operations
- [ ] Per-user rate limiting for authenticated endpoints

### 8. Sensitive Data Exposure

#### Logging
- Never log passwords, tokens, API keys, or PII
- Redact or mask sensitive fields before logging
- Return generic error messages to users; log details server-side only

#### Error Handling
- Do not return stack traces or internal error details to clients

#### Verification
- [ ] No sensitive data in logs
- [ ] Generic error messages for users
- [ ] No stack traces exposed to clients

### 9. Dependency Security

- Run the language-appropriate dependency audit tool (npm audit, pip-audit, cargo audit, govulncheck, etc.)
- Fix high/critical vulnerabilities before merging
- Commit lock files and use them in CI for reproducible builds
- Enable automated dependency updates (Dependabot or equivalent)

#### Verification
- [ ] Dependency audit clean (no high/critical CVEs)
- [ ] Lock files committed
- [ ] Automated dependency updates enabled

## Security Testing

Write automated tests covering security properties:

```
# Authentication: unauthenticated request returns 401
# Authorization: insufficient role returns 403
# Validation: invalid input returns 400 with safe error message
# Rate limit: exceeding limit returns 429
```

## Pre-Deployment Checklist

- [ ] No hardcoded secrets
- [ ] All inputs validated
- [ ] Parameterized queries only
- [ ] XSS protection in place
- [ ] CSRF protection enabled
- [ ] Authentication verified on every protected route
- [ ] Authorization checks in place
- [ ] Rate limiting enabled
- [ ] HTTPS enforced
- [ ] Security headers configured (CSP, HSTS, X-Frame-Options)
- [ ] Error handling does not expose internals
- [ ] No sensitive data in logs
- [ ] Dependencies free of high/critical CVEs

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)

---

**Remember**: Security is not optional. Validate, sanitize, authenticate, authorize — at every boundary.
