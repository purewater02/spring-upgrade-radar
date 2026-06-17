from __future__ import annotations

from html import escape
import csv
import io
import json

from spring_upgrade_radar.scanner import ScanReport


def render_markdown(report: ScanReport) -> str:
    # Executive Summary — always first
    lines = render_executive_summary(report).rstrip().splitlines()
    lines.append("")

    lines.extend(
        [
            "# Spring Upgrade Radar",
            "",
            f"- **Project**: `{report.project_path}`",
            f"- **Build tool**: {report.build_tool}",
            f"- **Spring Boot**: {report.spring_boot_version or 'unknown'}",
            f"- **Java**: {report.java_version or 'unknown'}",
            f"- **Target Spring Boot**: {report.target_boot}",
            f"- **Risk score**: {report.score}/100",
            "",
            "## Findings",
            "",
        ]
    )
    if not report.findings:
        lines.append("지원 종료 또는 마이그레이션 위험 신호를 찾지 못했습니다.")
    for finding in report.findings:
        lines.extend(
            [
                f"### [{finding.severity.upper()}] {finding.title}",
                "",
                f"- **Rule**: `{finding.rule_id}`",
                f"- **Detail**: {finding.detail}",
                f"- **Recommendation**: {finding.recommendation}",
            ]
        )
        if finding.evidence:
            lines.append("- **Evidence**:")
            for item in finding.evidence[:10]:
                lines.append(f"  - `{item}`")
        lines.append("")

    lines.extend(render_tickets_markdown(report).rstrip().splitlines())
    lines.extend(
        [
            "",
            "## Next actions",
            "",
            "1. High severity 항목부터 별도 브랜치/티켓으로 분리한다.",
            "2. Java 17/21 toolchain 빌드를 먼저 통과시킨다.",
            "3. javax→jakarta 전환과 dependency major upgrade를 한 PR에 섞지 않는다.",
            "4. 테스트 실패가 많은 모듈부터 OpenRewrite 또는 수동 migration spike를 수행한다.",
            "",
            "---",
            "",
            "## Need a full migration plan?",
            "",
            "This report is a first-pass migration radar. For team planning, turn it into a full Spring Boot 3 migration assessment:",
            "",
            "- **Pro report**: PDF, dependency matrix, and sprint-by-sprint plan",
            "- **Team workflow**: Jira/GitHub issue export and CI integration",
            "- **Spring Boot 3 migration assessment**: prioritized backlog and upgrade strategy",
        ]
    )
    return "\n".join(lines) + "\n"


def render_tickets_markdown(report: ScanReport) -> str:
    lines = ["## Migration tickets", ""]
    if not report.findings:
        lines.append("마이그레이션 티켓으로 변환할 findings가 없습니다.")
        return "\n".join(lines) + "\n"

    validation_command = _validation_command(report)
    for index, finding in enumerate(report.findings, start=1):
        lines.extend(
            [
                f"### Ticket {index}: {finding.title}",
                "",
                f"- **Rule**: `{finding.rule_id}`",
                f"- **Why**: {finding.detail}",
                "- **Affected files/evidence**:",
            ]
        )
        if finding.evidence:
            for item in finding.evidence[:10]:
                lines.append(f"  - `{item}`")
        else:
            lines.append("  - `No direct file evidence; build metadata or missing configuration finding.`")
        lines.extend(
            [
                f"- **Suggested change**: {finding.recommendation}",
                f"- **Validation command**: `{validation_command}`",
                f"- **Rough effort**: {_rough_effort(finding.severity)}",
                "",
            ]
        )
    return "\n".join(lines)


def render_tickets_json(report: ScanReport) -> str:
    validation_command = _validation_command(report)
    payload = {
        "project": str(report.project_path),
        "build_tool": report.build_tool,
        "spring_boot_version": report.spring_boot_version,
        "java_version": report.java_version,
        "target_boot": report.target_boot,
        "risk_score": report.score,
        "tickets": [
            {
                "id": f"SUR-{index:03d}",
                "title": finding.title,
                "rule_id": finding.rule_id,
                "severity": finding.severity,
                "why": finding.detail,
                "evidence": finding.evidence[:10],
                "suggested_change": finding.recommendation,
                "validation_command": validation_command,
                "rough_effort": _rough_effort(finding.severity),
            }
            for index, finding in enumerate(report.findings, start=1)
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def render_jira_csv(report: ScanReport) -> str:
    output = io.StringIO()
    fieldnames = ["Issue Type", "Summary", "Description", "Priority", "Labels", "Story Points"]
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()

    validation_command = _validation_command(report)
    for index, finding in enumerate(report.findings, start=1):
        ticket_id = f"SUR-{index:03d}"
        evidence = "\n".join(f"- {item}" for item in finding.evidence[:10]) or "- No direct file evidence; build metadata or missing configuration finding."
        writer.writerow(
            {
                "Issue Type": "Task",
                "Summary": f"[{ticket_id}] {finding.title}",
                "Description": "\n".join(
                    [
                        f"Rule: {finding.rule_id}",
                        f"Why: {finding.detail}",
                        "Evidence:",
                        evidence,
                        f"Suggested change: {finding.recommendation}",
                        f"Validation command: {validation_command}",
                        f"Rough effort: {_rough_effort(finding.severity)}",
                    ]
                ),
                "Priority": _jira_priority(finding.severity),
                "Labels": f"spring-upgrade-radar,spring-boot-3,migration,{finding.severity}",
                "Story Points": _story_points(finding.severity),
            }
        )
    return output.getvalue()


def render_github_issues_markdown(report: ScanReport) -> str:
    lines = [
        "# GitHub Issues - Spring Upgrade Radar",
        "",
        f"Project: `{report.project_path}`",
        f"Target Spring Boot: `{report.target_boot}`",
        f"Risk score: `{report.score}/100`",
        "",
        "Use each section as a copy/paste-ready GitHub issue, or turn the title/body/labels into `gh issue create` calls.",
        "",
    ]
    validation_command = _validation_command(report)
    for index, finding in enumerate(report.findings, start=1):
        ticket_id = f"SUR-{index:03d}"
        title = f"[{ticket_id}] {finding.title}"
        labels = f"spring-upgrade-radar, spring-boot-3, migration, severity:{finding.severity}"
        evidence = [f"- `{item}`" for item in finding.evidence[:10]] or ["- `No direct file evidence; build metadata or missing configuration finding.`"]
        body_lines = [
            "#### Why",
            finding.detail,
            "",
            "#### Evidence",
            *evidence,
            "",
            "#### Suggested change",
            finding.recommendation,
            "",
            "#### Validation",
            "```bash",
            validation_command,
            "```",
            "",
            "#### Planning",
            f"- Severity: `{finding.severity}`",
            f"- Rough effort: `{_rough_effort(finding.severity)}`",
            f"- Rule: `{finding.rule_id}`",
        ]
        body = "\n".join(body_lines)
        lines.extend(
            [
                f"## Issue {ticket_id}",
                "",
                "### Title",
                title,
                "",
                "### Labels",
                labels,
                "",
                "### Body",
                body,
                "",
                "### gh command",
                "```bash",
                f"gh issue create --title {json.dumps(title, ensure_ascii=False)} --label {json.dumps(labels, ensure_ascii=False)} --body-file <body-file>",
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def _validation_command(report: ScanReport) -> str:
    if report.build_tool == "gradle":
        nested_gradlew = _single_nested_wrapper(report.project_path, "gradlew")
        if nested_gradlew:
            return f"cd {nested_gradlew} && ./gradlew test"
        return "./gradlew test"
    if report.build_tool == "maven":
        nested_mvnw = _single_nested_wrapper(report.project_path, "mvnw")
        if nested_mvnw:
            return f"cd {nested_mvnw} && ./mvnw test"
        if not (report.project_path / "pom.xml").exists():
            nested_pom_dirs = sorted(
                {path.parent.relative_to(report.project_path).as_posix() for path in report.project_path.rglob("pom.xml") if _is_scannable_path(path)}
            )
            if len(nested_pom_dirs) == 1:
                return f"cd {nested_pom_dirs[0]} && mvn test"
        return "./mvnw test"
    return "run the project test suite"


def _single_nested_wrapper(project_path, wrapper_name: str) -> str | None:
    root_wrapper = project_path / wrapper_name
    if root_wrapper.exists():
        return None
    wrappers = sorted(
        path.parent.relative_to(project_path).as_posix()
        for path in project_path.rglob(wrapper_name)
        if _is_scannable_path(path)
    )
    return wrappers[0] if len(wrappers) == 1 else None


def _is_scannable_path(path) -> bool:
    return not any(part in {"build", "target", ".gradle", ".git"} for part in path.parts)


def _rough_effort(severity: str) -> str:
    return {"high": "L", "medium": "M", "low": "S"}.get(severity, "M")


def _jira_priority(severity: str) -> str:
    return {"high": "Highest", "medium": "Medium", "low": "Low"}.get(severity, "Medium")


def _story_points(severity: str) -> str:
    return {"high": "8", "medium": "3", "low": "1"}.get(severity, "3")


def render_executive_summary(report: ScanReport) -> str:
    """Executive Summary — 리더십/고객에게 바로 보여주는 1페이지 요약."""
    score = report.score
    grade = _readiness_grade(score)
    findings_by_severity: dict[str, list[Finding]] = {"high": [], "medium": [], "low": []}
    for f in report.findings:
        findings_by_severity[f.severity].append(f)
    
    findings_by_rule = {f.rule_id: f for f in report.findings}

    lines = [
        "# Executive Summary",
        "",
        f"- **Project**: `{report.project_path}`",
        f"- **Spring Boot**: {report.spring_boot_version or 'unknown'} → **{report.target_boot}**",
        f"- **Java**: {report.java_version or 'unknown'}",
        f"- **Risk score**: **{score}/100**",
        f"- **Migration Readiness Grade**: **{grade}**",
        "",
    ]

    # Overview paragraph
    if score >= 70:
        risk_level = "높음"
        desc = "대규모 마이그레이션이 필요합니다."
    elif score >= 30:
        risk_level = "중간"
        desc = "표준적인 전환 작업이 예상됩니다."
    else:
        risk_level = "낮음"
        desc = "현재 버전이 목표와 근접하거나 마이그레이션 위험이 적습니다."
    
    lines.extend([
        "## 📊 개요",
        "",
        f"이 프로젝트는 현재 Spring Boot **{report.spring_boot_version or 'unknown'}**에서 **{report.target_boot}**로 마이그레이션해야 합니다.",
        f"전체 위험도는 **{score}/100**이며, 위험 수준은 **{risk_level}**입니다. {desc}",
        "",
    ])

    # Migration Readiness Grade
    lines.extend([
        "## 🎖️ Migration Readiness Grade",
        "",
        f"| Score Range | Grade | Description |",
        f"|---|---|---|",
        "| 70-100 | 🔴 **C (Critical)** | 대규모 마이그레이션 필요 — Java 17+, Jakarta 전환, 테스트 재작성이 동시 필요 |",
        "| 30-69 | 🟡 **B (Ready)** | 표준 마이그레이션 — javax→jakarta 전환과 주요 API 변경점 확인 필요 |",
        "| 0-29 | 🟢 **A (Excellent)** | 준비됨 — 작은 조정만 필요하거나 이미 근접 버전 |",
        "",
    ])

    # Top 3 Risks
    high_findings = findings_by_severity.get("high", [])
    medium_findings = findings_by_severity.get("medium", [])
    top_risks = high_findings[:3] if high_findings else medium_findings[:3]
    
    lines.extend([
        "## ⚠️ Top 3 Risks",
        "",
    ])
    if top_risks:
        for i, r in enumerate(top_risks, 1):
            lines.extend([
                f"### {i}. {r.title}",
                "",
                f"- **Severity**: {r.severity}",
                f"- **Detail**: {r.detail}",
                "",
            ])
    else:
        lines.extend(["현재 발견된 주요 위험이 없습니다. 🎉", ""])

    # Estimated Roadmap
    backlog_items = _suggested_backlog(report)
    jakarta_rules = [k for k in findings_by_rule if k.startswith("jakarta-")]
    has_work = top_risks or jakarta_rules or "spring-security-legacy-config" in findings_by_rule
    
    lines.extend([
        "## 🗺️ Estimated Roadmap",
        "",
    ])
    if has_work:
        for i, item in enumerate(backlog_items, 1):
            lines.extend([
                f"### Sprint {i}: {item['title']}",
                "",
                f"- **Goal**: {item['goal']}",
                f"- **Tasks**: {item['tasks']}",
                f"- **Estimated Time**: {item.get('time_estimate', 'N/A')}",
                "",
            ])
        sprint_count = len(backlog_items)
        if sprint_count > 1:
            total = f"{backlog_items[0].get('time_estimate', 'N/A')} ... {backlog_items[-1].get('time_estimate', 'N/A')}"
        else:
            total = backlog_items[0].get('time_estimate', 'N/A')
        lines.extend([
            f"**Total Estimated Duration**: {sprint_count} sprints (약 {total})",
            "",
        ])
    else:
        lines.extend(["현재 발견된 주요 마이그레이션 작업이 없습니다. 🎉", ""])

    # Recommended Sprint Backlog
    lines.extend([
        "## 📋 Recommended Sprint Backlog",
        "",
    ])
    for i, item in enumerate(backlog_items, 1):
        lines.extend([
            f"### Sprint {i}: {item['title']}",
            "",
            f"- **Goal**: {item['goal']}",
            f"- **Tasks**: {item['tasks']}",
            "",
        ])

    return "\n".join(lines) + "\n"


def _readiness_grade(score: int) -> str:
    if score >= 70:
        return "C (Critical)"
    if score >= 30:
        return "B (Ready)"
    return "A (Excellent)"


def _suggested_backlog(report: ScanReport) -> list[dict[str, str]]:
    """Findings 기반 권장 sprint 백로그 생성."""
    findings_by_rule = {f.rule_id: f for f in report.findings}
    backlog: list[dict[str, str]] = []

    # Sprint 1: Java baseline
    if "java-baseline" in findings_by_rule:
        backlog.append({
            "title": "Java 17+ 빌드 환경 전환",
            "goal": "JDK 17/21로 빌드하고 런타임 호환성 확보",
            "tasks": "sourceCompatibility/targetCompatibility 변경, JDK toolchain 설정, 빌드 테스트 실행",
            "time_estimate": "2 주",
        })

    # Sprint 2: javax → jakarta
    jakarta_rules = [k for k in findings_by_rule if k.startswith("jakarta-")]
    if jakarta_rules:
        affected = [findings_by_rule[r] for r in jakarta_rules]
        total_files = sum(len(f.evidence) for f in affected)
        backlog.append({
            "title": "javax → jakarta namespace 전환",
            "goal": "모든 javax.* import를 jakarta.*로 전환",
            "tasks": f"약 {total_files}개 파일 전환, Servlet/Validation/Persistence별 검증 테스트 실행",
            "time_estimate": "2 주",
        })

    # Sprint 3: Security
    if "spring-security-legacy-config" in findings_by_rule:
        backlog.append({
            "title": "Spring Security 6 스타일로 재작성",
            "goal": "WebSecurityConfigurerAdapter → SecurityFilterChain 전환",
            "tasks": "SecurityFilterChain @Bean 추가, antMatchers→requestMatchers 변경, authorizeRequests→authorizeHttpRequests",
            "time_estimate": "1 주",
        })

    # Sprint 4: JSP
    if "jsp-jstl-jakarta" in findings_by_rule:
        backlog.append({
            "title": "JSP/JSTL Jakarta 호환성 전환",
            "goal": "Tomcat 10 jakarta.servlet 환경에서 JSP 렌더링 검증",
            "tasks": "jakarta.servlet.jsp.jstl 의존성 전환, taglib URI 확인, 뷰 회귀 테스트",
            "time_estimate": "1 주",
        })

    # Sprint 5: Dependency upgrades
    dep_rules = [k for k in findings_by_rule if k in {"springfox", "querydsl-jakarta", "hibernate-major", "mysql-connector-coordinates"}]
    if dep_rules:
        backlog.append({
            "title": "종속성 major upgrade",
            "goal": "Hibernate 6, springdoc-openapi, QueryDSL jakarta 등 주요 의존성 전환",
            "tasks": "의존성 좌표 변경, native query/dialect 검증, 테스트 실행",
            "time_estimate": "2 주",
        })

    # Sprint 6: Spring Boot version upgrade
    if "spring-boot-2-to-3" in findings_by_rule:
        backlog.append({
            "title": "Spring Boot 2.x → 3.x 마이그레이션",
            "goal": "Spring Boot 3.x로 버전 업그레이드 및 breaking change 대응",
            "tasks": "parent/plugin 버전 변경, auto-configuration 변경점 확인, 테스트 재실행",
            "time_estimate": "1 주",
        })

    if not backlog:
        backlog.append({
            "title": "추가 작업 없음",
            "goal": "현재 버전이 목표와 근접합니다.",
            "tasks": "정기적 Spring Boot 업데이트 모니터링",
            "time_estimate": "N/A",
        })

    return backlog


def render_html(report: ScanReport) -> str:
    body = render_markdown(report)
    escaped = escape(body)
    return f"""<!doctype html>
<html lang=\"ko\">
<head>
  <meta charset=\"utf-8\">
  <title>Spring Upgrade Radar</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 920px; margin: 40px auto; line-height: 1.55; padding: 0 20px; }}
    pre {{ white-space: pre-wrap; background: #0f172a; color: #e2e8f0; padding: 24px; border-radius: 12px; }}
  </style>
</head>
<body>
<pre>{escaped}</pre>
</body>
</html>
"""
