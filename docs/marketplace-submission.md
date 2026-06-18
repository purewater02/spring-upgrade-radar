# GitHub Marketplace Submission Notes

Use this checklist when publishing Spring Upgrade Radar as a free GitHub Action in GitHub Marketplace.

## Listing positioning

- **Listing name**: Spring Upgrade Radar
- **Short description**: Free local-first Spring Boot 3 migration scanner for risk reports, roadmaps, and tickets.
- **Primary category**: Code quality
- **Secondary category**: Continuous integration or Utilities
- **Tags/topics**: spring-boot, java, migration, github-actions, jakarta-ee, spring-boot-3

## Pricing stance

The GitHub Action is free.

Optional paid services are external add-ons while demand is validated:

| Plan | Price | Notes |
|---|---:|---|
| Free CLI + GitHub Action | $0 | Local scan, Markdown/HTML reports, JSON/Jira/GitHub issue exports |
| Pro Report | $49/repo | Reviewed report, dependency risk notes, prioritized roadmap, async feedback |
| Team Assessment | From $299/project | Multi-module analysis and CI rollout guidance |

Do **not** present Pro Report / Team Assessment as paid GitHub Marketplace plans. Official GitHub Marketplace paid plans require a GitHub App/OAuth App listing, verified publisher setup, Marketplace API event handling, and financial onboarding.

## Release notes for v0.1.1

### Highlights

- Free composite GitHub Action for CI-based Spring Boot migration scanning.
- Local-first CLI: source code stays on the runner/machine.
- Generates Markdown and HTML reports with risk score, readiness grade, top risks, and estimated roadmap.
- Exports migration tickets as JSON, Jira CSV, and GitHub Issues Markdown.
- Hardened packaging so `pip install -e .` works in clean clones.
- CLI now auto-creates output directories such as `out/report.md`.
- Corrected Migration Readiness Grade table in generated reports and public samples.

### Validation

- Local unit tests: 27 passing.
- Clean temporary install verified with `pip install -e .`.
- Demo scan verified against `examples/demo-spring-boot-27`.
- GitHub Actions CI verified on Python 3.11 and 3.12.
- GitHub Pages public links verified.

### Quick start

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
      - uses: purewater02/spring-upgrade-radar@v0.1.1
        with:
          project-path: "."
          target-version: "3.5"
          output-dir: "spring-upgrade-radar-output"
      - uses: actions/upload-artifact@v4
        with:
          name: spring-upgrade-radar-report
          path: spring-upgrade-radar-output/
```

## UI publishing steps

1. Open `action.yml` on GitHub: https://github.com/purewater02/spring-upgrade-radar/blob/main/action.yml
2. If GitHub shows the Marketplace banner, click **Draft a release**.
3. Use tag `v0.1.1` and title `Spring Upgrade Radar v0.1.1`.
4. Check **Publish this Action to the GitHub Marketplace**.
5. Accept the GitHub Marketplace Developer Agreement if prompted.
6. Choose categories:
   - Primary: Code quality
   - Secondary: Continuous integration or Utilities
7. Paste the release notes above.
8. Publish the release.

If the release already exists as a draft, open the draft release, check **Publish this Action to the GitHub Marketplace**, then publish it.
