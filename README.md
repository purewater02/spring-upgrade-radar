# Spring Upgrade Radar

**Generate a Spring Boot 3 migration estimate before your upgrade breaks.**

Landing page: https://purewater02.github.io/spring-upgrade-radar/

Spring Upgrade Radar is a local-first scanner for Spring Boot projects. It inspects Maven/Gradle applications and generates a leader-ready migration report with risk score, top risks, estimated roadmap, and actionable tickets.

> Positioning: **Spring Boot 3 migration estimate generator** — not just a static analyzer.

## Why this exists

Spring Boot 2.x → 3.x upgrades are risky because several changes land at once:

- Java 17+ baseline
- `javax.*` → `jakarta.*` namespace migration
- Spring Security 5 → 6 API changes
- Hibernate 5 → 6 behavior changes
- dependency coordinate and plugin compatibility issues
- CI/runtime surprises that are hard to estimate upfront

This tool answers the question teams usually ask first:

> **“How risky is this migration, what will break, and how many sprints should we plan?”**

## What it generates

- **Executive Summary** — 1-page report for CTOs, EMs, tech leads, and PMs
- **Risk score and readiness grade** — quick estimate of migration complexity
- **Top 3 risks** — the issues most likely to block the upgrade
- **Estimated Roadmap** — sprint-by-sprint migration plan with rough time estimates
- **Recommended Sprint Backlog** — prioritized implementation sequence
- **Full Markdown/HTML report** — detailed findings with evidence and recommendations
- **Migration tickets** — actionable work items for engineering teams
- **Structured exports** — JSON, Jira CSV, and GitHub Issues Markdown

## Example output

See the sample report generated from a Spring Boot 2.x project:

- [`docs/sample-report-SpringBoot_JPA_Blog_Prj.md`](docs/sample-report-SpringBoot_JPA_Blog_Prj.md)
- [`docs/sample-exec-summary-SpringBoot_JPA_Blog_Prj.md`](docs/sample-exec-summary-SpringBoot_JPA_Blog_Prj.md)
- [`docs/sample-tickets-SpringBoot_JPA_Blog_Prj.json`](docs/sample-tickets-SpringBoot_JPA_Blog_Prj.json)
- [`docs/sample-jira-SpringBoot_JPA_Blog_Prj.csv`](docs/sample-jira-SpringBoot_JPA_Blog_Prj.csv)
- [`docs/sample-github-issues-SpringBoot_JPA_Blog_Prj.md`](docs/sample-github-issues-SpringBoot_JPA_Blog_Prj.md)

A typical executive summary includes:

```md
# Executive Summary

- Spring Boot: 2.6.2 → 3.5
- Java: 8
- Risk score: 100/100 | Grade: C (Critical)

## ⚠️ Top 3 Risks
1. Spring Boot 2.x → 3.x major migration
2. Java 17 baseline gap
3. JPA javax.persistence imports

## 🗺️ Estimated Roadmap
- Sprint 1: Java 17+ build/runtime baseline — Estimated Time: 2 weeks
- Sprint 2: javax → jakarta namespace migration — Estimated Time: 2 weeks
- Sprint 3: dependency major upgrades — Estimated Time: 2 weeks
- Sprint 4: Spring Boot 3.x migration validation — Estimated Time: 1 week
```

## Quick start

### Option 1: Run from source

```bash
git clone https://github.com/<your-org>/spring-upgrade-radar.git
cd spring-upgrade-radar
python3 -m venv .venv
. .venv/bin/activate
pip install -e .

spring-upgrade-radar scan examples/demo-spring-boot-27 \
  --target 3.5 \
  --output out/demo-report.md \
  --html-output out/demo-report.html \
  --tickets-json out/demo-tickets.json \
  --jira-csv out/demo-jira.csv \
  --github-issues-md out/demo-github-issues.md
```

### Option 2: Run as a module

```bash
python3 -m spring_upgrade_radar.cli scan <path-to-spring-project> \
  --target 3.5 \
  --output out/report.md \
  --html-output out/report.html \
  --tickets-json out/tickets.json \
  --jira-csv out/jira.csv \
  --github-issues-md out/github-issues.md
```

## GitHub Actions usage

After publishing this repository as a GitHub Action, teams can run it in CI:

```yaml
name: Spring Upgrade Radar

on:
  workflow_dispatch:
  pull_request:
    paths:
      - "**/pom.xml"
      - "**/build.gradle"
      - "**/*.java"

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Run Spring Upgrade Radar
        uses: <your-org>/spring-upgrade-radar@v0.1.0
        with:
          project-path: "."
          target-version: "3.5"
      - uses: actions/upload-artifact@v4
        with:
          name: spring-upgrade-radar-report
          path: spring-upgrade-radar-output/
```

See [`action.yml`](action.yml) for the local composite action definition.

## Current scan scope

This is intentionally a narrow first wedge:

- static analysis only
- no source upload required
- local-first by default
- focused on Spring Boot 2.7/3.x → 3.5 migration planning
- report-first, not auto-rewrite-first

Current checks include:

- Spring Boot 2.x → 3.x migration risk
- Java baseline compatibility
- Jakarta Persistence import migration
- Spring Security legacy configuration patterns
- JSP/JSTL Jakarta compatibility risks
- MySQL Connector/J coordinate migration
- wrapper/CI execution readiness checks

## Product direction

The product wedge is migration planning, not generic linting:

1. **Free local CLI** — basic report, Markdown/HTML output, sample-driven adoption
2. **Pro report** — richer roadmap, PDF/export, historical comparison, GitHub PR comments
3. **Team/Enterprise** — multi-repo dashboard, Jira export, private runner, custom rules
4. **Consulting lead generation** — “free migration assessment” funnel for Spring Boot 3 upgrades

See [`docs/productization-plan.md`](docs/productization-plan.md) for the proposed packaging, pricing, and marketing plan.

Marketing drafts:

- [`docs/landing-page-copy.md`](docs/landing-page-copy.md)
- [`docs/articles/spring-boot-27-to-3x-migration-checklist.md`](docs/articles/spring-boot-27-to-3x-migration-checklist.md)

## Development

Run tests:

```bash
python3 -m unittest discover -s tests -v
```

Run a demo scan:

```bash
python3 -m spring_upgrade_radar.cli scan examples/demo-spring-boot-27 \
  --target 3.5 \
  --output out/demo-report.md \
  --html-output out/demo-report.html \
  --tickets-json out/demo-tickets.json \
  --jira-csv out/demo-jira.csv \
  --github-issues-md out/demo-github-issues.md
```

## Roadmap

Next useful rules and features:

1. Spring Security 5 → 6 API usage details
2. Hibernate 5 → 6 native query/dialect risks
3. Gradle/Maven plugin compatibility matrix
4. OpenRewrite recipe recommendations
5. GitHub PR comments and CI annotations
6. SaaS-style hosted report viewer

## License

TBD.
