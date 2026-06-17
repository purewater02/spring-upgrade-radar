# Spring Upgrade Radar Landing Page Copy

## Hero

### Spring Boot 3 migration estimates in minutes, not meetings.

Scan your Spring Boot 2.x project locally and generate an executive summary, risk score, estimated roadmap, and migration tickets before committing to the upgrade.

**Primary CTA:** Generate a free migration report  
**Secondary CTA:** View sample report

Trust line:

> Local-first by default. Your source code does not need to leave your machine.

---

## Problem

### Spring Boot 3 upgrades hide multiple migrations in one release.

Upgrading from Spring Boot 2.x to 3.x is rarely just a version bump. Teams often need to handle:

- Java 17+ baseline requirements
- `javax.*` → `jakarta.*` namespace migration
- Spring Security 5 → 6 configuration changes
- Hibernate 5 → 6 compatibility issues
- dependency coordinate changes
- CI/runtime surprises
- unclear sprint estimates

The hard question is not “can we upgrade?”  
It is:

> **What will break, how risky is it, and how much time should we reserve?**

---

## Product

### From source scan to sprint plan.

Spring Upgrade Radar scans a Spring Boot project and generates a migration planning package your team can act on.

#### 1. Detect upgrade risks

Find risky patterns such as Java baseline gaps, `javax.persistence` imports, legacy Spring Security configuration, JSP/JSTL risks, and dependency coordinate issues.

#### 2. Score readiness

Get a risk score and readiness grade that makes migration complexity easy to explain to tech leads, EMs, CTOs, and PMs.

#### 3. Estimate the roadmap

Turn findings into an estimated sprint-by-sprint migration roadmap.

#### 4. Export tickets

Generate Markdown, HTML, JSON, Jira CSV, and GitHub Issues Markdown outputs.

---

## Sample report section

### Example Executive Summary

```md
# Executive Summary

- Spring Boot: 2.6.2 → 3.5
- Java: 8
- Risk score: 100/100 | Grade: C (Critical)

## Top 3 Risks
1. Spring Boot 2.x → 3.x major migration
2. Java 17 baseline gap
3. JPA javax.persistence imports

## Estimated Roadmap
- Sprint 1: Java 17+ build/runtime baseline — 2 weeks
- Sprint 2: javax → jakarta namespace migration — 2 weeks
- Sprint 3: dependency major upgrades — 2 weeks
- Sprint 4: Spring Boot 3.x validation — 1 week
```

CTA:

> View the full sample report.

---

## Security / privacy

### Built for teams that cannot upload source code.

Spring Upgrade Radar is local-first. Run it in your own repository, CI, or private runner. The default workflow generates reports without uploading source code to a hosted service.

---

## Use cases

### For backend teams

Estimate migration risk before assigning a sprint.

### For tech leads and EMs

Explain upgrade scope with a leader-ready executive summary.

### For consultants

Generate repeatable migration assessments for client projects.

### For platform teams

Scan multiple services and prioritize the riskiest upgrades first.

---

## Pricing copy

### Free CLI

For individual developers and early migration checks.

- Local scan
- Markdown/HTML report
- Risk score
- Core findings
- Migration tickets

### Pro Report — proposed $29/report

For teams that need a more complete planning artifact.

- PDF report
- dependency matrix
- richer sprint roadmap
- OpenRewrite recommendations
- PR/Jira-ready planning package

### Team / Enterprise

For organizations with multiple Spring Boot services.

- GitHub Action integration
- scan history
- multi-repo dashboard
- private runner
- custom rules

---

## Final CTA

### Know your Spring Boot 3 migration risk before the upgrade starts.

Run Spring Upgrade Radar and generate your first migration report.

**CTA:** Generate a free migration report
