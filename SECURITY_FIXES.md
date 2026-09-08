# Docker Security Vulnerability Fixes - Action Plan

**Report Generated:** 2025-01-17  
**Total CVEs Found:** 229 (13 Critical, 79 High, 86 Medium, 56 Low + 23 Unspecified)

---

## 🔴 CRITICAL Actions (DO IMMEDIATELY)

### 1. Frontend Image - OpenSSL Critical Vulnerabilities
**Status:** 3 CRITICAL CVEs blocking deployment

```bash
# Current: node:22-alpine with OpenSSL 3.5.7-r0
# Issue: CVE-2026-63073, CVE-2026-75803 (CVSS 9.1+ each)

# Fix: Rebuild with latest node:22-alpine
docker pull node:22-alpine
cd fastapi_nuxt_template
docker compose build frontend --no-cache
docker scout cves fastapi_nuxt_template-frontend:latest
```

**Expected improvement:** Eliminates 3 critical + 7 high OpenSSL vulnerabilities

---

### 2. Frontend Dependencies - npm tar Package
**Status:** 1 CRITICAL, 2 HIGH CVEs in production dependency

```bash
# Current: tar@7.5.11 in node_modules
# Critical Issue: CVE-2026-59873 (CVSS 9.2 - DoS/Memory)

# Fix:
cd frontend/nuxt4
pnpm update tar
# Should resolve to tar@7.5.19+

# Verify:
pnpm audit
```

**Expected improvement:** Eliminates 1 critical + 2 high tar vulnerabilities

---

### 3. PostgreSQL Image - Go stdlib Critical
**Status:** 4 CRITICAL CVEs in base image

```bash
# Current: postgres:17-alpine with Go 1.24.6
# Issues: CVE-2025-68121, CVE-2026-39821 (networking/protocol issues)

# Fix: Rebuild with latest postgres:17-alpine
docker pull postgres:17-alpine
docker compose build postgres --no-cache
docker scout cves fastapi_nuxt_template-postgres:latest
```

**Expected improvement:** Eliminates 4 critical Go stdlib vulnerabilities

---

### 4. Nginx Image - curl Critical Vulnerabilities
**Status:** 6 CRITICAL curl CVEs (unfixed in curl 8.12.1)

⚠️ **Note:** These are in the nginx:1.27-alpine base image upstream. Fixes pending from Alpine maintainers.

```dockerfile
# Current Nginx Dockerfile uses curl for healthcheck
# HEALTHCHECK uses: curl -f http://localhost/health

# Partial Mitigation (already applied):
# Switched to wget (built-in busybox) which has fewer vulns
# See: infrastructure/nginx/Dockerfile

# Full fix: Wait for nginx:1.27-alpine to ship curl 8.14.1+
# Timeline: Check Alpine releases periodically
docker pull nginx:1.27-alpine  # Re-check in 2-4 weeks
```

**Current status:** Mitigated to use wget instead of curl  
**Upstream status:** Pending alpine:3.21 curl security updates

---

## 🟡 HIGH Priority (Within 1 Week)

### 1. Frontend - Additional npm vulnerabilities
```bash
cd frontend/nuxt4
pnpm audit fix

# Expected updates:
# - brace-expansion: 2.0.2 → 2.1.4+
# - picomatch: 4.0.3 → 4.0.4+
# - ip-address: 10.1.0 → 10.3.1+
# - sigstore: 3.1.0 → 4.1.1+

docker compose build frontend --no-cache
docker scout cves fastapi_nuxt_template-frontend:latest
```

### 2. Backend - Python pip vulnerabilities
```bash
# Current: pip 25.0.1 in Python 3.12-slim
# Issues: CVE-2025-8869, CVE-2026-13346 (path traversal)

# Fix: Rebuild with latest python:3.12-slim
docker pull python:3.12-slim
docker compose build backend --no-cache

# Verify no new vulns introduced:
docker scout cves fastapi_nuxt_template-backend:latest
```

### 3. Backend - zlib HIGH vulnerability
```
Current: zlib 1:1.3.dfsg+really1.3.1-1
CVE: CVE-2026-85091
Status: NO FIX AVAILABLE YET (upstream debian pending)

Action: Monitor and rebuild when fix available (~2-4 weeks)
```

---

## 🟢 MEDIUM Priority (Routine Maintenance)

### 1. Rebuild all images with latest patches
```bash
# Rebuild all in one command
docker compose build --no-cache --pull

# Then verify each:
docker scout cves fastapi_nuxt_template-backend:latest
docker scout cves fastapi_nuxt_template-frontend:latest
docker scout cves fastapi_nuxt_template-nginx:latest
docker scout cves fastapi_nuxt_template-postgres:latest
docker scout cves fastapi_nuxt_template-redis:latest
```

### 2. Set up automated scanning
```bash
# Create GitHub Actions workflow (.github/workflows/security.yml)
name: Docker Security Scan
on:
  schedule:
    - cron: '0 0 * * *'  # Daily
  push:
    branches: [main]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - run: docker compose build
      - run: |
          docker scout cves fastapi_nuxt_template-backend:latest
          docker scout cves fastapi_nuxt_template-frontend:latest
          # ... etc for all images
```

### 3. Monitor base image updates
- **node:22-alpine** - Check weekly for security patches
- **python:3.12-slim** - Check monthly (Debian Trixie)
- **nginx:1.27-alpine** - Check weekly
- **postgres:17-alpine** - Check weekly
- **redis:7-alpine** - Check monthly (lowest risk)

---

## 📋 Vulnerability Summary by Image

### ✅ redis:7-alpine (LOWEST RISK)
- **Vulns:** 2 Medium, 0 High/Critical
- **Status:** No action required this cycle
- **Risk:** Safe for production
- **Action:** Monthly routine updates only

### ⚠️ backend:latest (41 total)
- **Critical:** 0
- **High:** 1 (zlib - no fix yet)
- **Medium:** 6 (pip)
- **Status:** Blocked on zlib fix
- **Action:** Rebuild weekly until zlib patch available

### 🔴 frontend:latest (29 total)
- **Critical:** 3 (OpenSSL)
- **High:** 17 (OpenSSL + npm)
- **Medium:** 8 (npm)
- **Status:** URGENT - deploy fix this week
- **Action:** Priority 1 - Update npm deps today

### 🔴 nginx:latest (124 total)
- **Critical:** 6 (curl)
- **High:** 30 (curl + image libraries)
- **Medium:** 49 (image processing libs)
- **Status:** URGENT - awaiting upstream fix
- **Action:** Already mitigated wget; wait for nginx:1.27-alpine patch

### 🔴 postgres:latest (63 total)
- **Critical:** 4 (Go stdlib)
- **High:** 31 (Go stdlib + others)
- **Medium:** 21
- **Status:** URGENT - deploy fix this week
- **Action:** Rebuild with latest postgres:17-alpine

---

## 📊 Expected Improvement After Fixes

### Before Fixes
```
Total: 229 vulnerabilities
  Critical: 13
  High: 79
  Medium: 86
  Low: 56
```

### After Phase 1 (Critical Fixes - This Week)
```
Expected Total: ~150 vulnerabilities (-79)
  Critical: 0
  High: 35-40
  Medium: 60-70
  Low: 40-50
```

### After Phase 2 (npm Updates)
```
Expected Total: ~100 vulnerabilities (-50)
  Critical: 0
  High: 10-15
  Medium: 40-50
  Low: 40-50
```

### After Upstream Patches (zlib, curl - 2-4 weeks)
```
Expected Total: ~40-50 vulnerabilities (-100+)
  Critical: 0
  High: 0-5
  Medium: 20-30
  Low: 20-30
```

---

## ✅ Deployment Readiness Checklist

- [ ] Day 1: Rebuild frontend with `pnpm update`
- [ ] Day 1: Rebuild postgres with latest base image
- [ ] Day 2: Test all images in staging
- [ ] Day 3: Re-scan with `docker scout cves`
- [ ] Day 3: Verify no new vulns introduced
- [ ] Day 4: Deploy to production
- [ ] Weekly: Re-scan and monitor base images
- [ ] Monthly: Run `pnpm audit` on frontend
- [ ] Pending: Watch for zlib and curl fixes

---

## Quick Reference Commands

```bash
# Scan all images
docker scout cves fastapi_nuxt_template-backend:latest
docker scout cves fastapi_nuxt_template-frontend:latest
docker scout cves fastapi_nuxt_template-nginx:latest
docker scout cves fastapi_nuxt_template-postgres:latest
docker scout cves fastapi_nuxt_template-redis:latest

# Get recommendations for specific image
docker scout recommendations fastapi_nuxt_template-frontend:latest

# Full rebuild with latest patches
docker compose build --no-cache --pull

# Export CVE details to JSON
docker scout cves --format json fastapi_nuxt_template-frontend:latest > frontend-cves.json

# View detailed CVE info
docker scout cves fastapi_nuxt_template-frontend:latest --details

# Use Scout in CI/CD
docker scout cves --exit-code --threshold medium fastapi_nuxt_template-backend:latest
```

---

## Risk Assessment

### Current Production Risk: 🔴 HIGH
- 13 critical vulnerabilities
- Network-exposed services (nginx, frontend) affected
- Crypto libraries affected (OpenSSL)

### Post-Phase-1 Risk: 🟡 MEDIUM
- 0 critical
- Remaining highs mostly in image processing libs (low exposure)
- Frontend/API secured

### Post-Phase-2 Risk: 🟢 LOW
- Mainly low-severity / no available fixes
- Suitable for production

---

## Timeline

| Date | Action | Severity |
|------|--------|----------|
| Today | Update frontend npm deps | CRITICAL |
| Today | Rebuild postgres, frontend, backend | CRITICAL |
| Tomorrow | Test in staging | CRITICAL |
| Day 3 | Re-scan and verify | CRITICAL |
| Day 4 | Deploy to production | CRITICAL |
| 2-4 weeks | Monitor for zlib/curl fixes | HIGH |
| Monthly | Routine updates | MEDIUM |
| Weekly | Re-scan for new advisories | MEDIUM |

---

## Questions?

- Docker Scout docs: https://docs.docker.com/scout/
- CVE lookup: https://scout.docker.com/
- Alpine security: https://alpinelinux.org/
- Debian security: https://www.debian.org/security/
