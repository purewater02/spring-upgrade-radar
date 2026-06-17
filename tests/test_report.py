import csv
import io
import tempfile
import unittest
import json
from pathlib import Path

from spring_upgrade_radar.scanner import scan_project, Finding
from spring_upgrade_radar.report import (
    render_markdown, render_html, render_tickets_markdown,
    render_tickets_json, render_jira_csv, render_github_issues_markdown,
    render_executive_summary, _readiness_grade, _suggested_backlog,
)


class ReportTests(unittest.TestCase):
    def test_renders_markdown_and_html_with_next_actions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pom.xml").write_text(
                """
<project>
  <parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.3.13</version>
  </parent>
  <properties>
    <java.version>17</java.version>
  </properties>
  <dependencies>
    <dependency>
      <groupId>org.springdoc</groupId>
      <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
      <version>2.5.0</version>
    </dependency>
  </dependencies>
</project>
""".strip()
            )

            scanned = scan_project(root, target_boot="3.5")
            markdown = render_markdown(scanned)
            html = render_html(scanned)

            self.assertIn("Spring Upgrade Radar", markdown)
            self.assertIn("3.3.13", markdown)
            self.assertIn("지원 종료", markdown)
            self.assertIn("Next actions", markdown)
            self.assertIn("<html", html)
            self.assertIn("Spring Upgrade Radar", html)
            self.assertIn("3.3.13", html)

    def test_converts_each_finding_into_actionable_migration_ticket(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "build.gradle").write_text(
                """
plugins {
    id 'org.springframework.boot' version '2.7.18'
}
sourceCompatibility = '11'
""".strip()
            )

            scanned = scan_project(root, target_boot="3.5")
            tickets = render_tickets_markdown(scanned)
            markdown = render_markdown(scanned)

            self.assertEqual(tickets.count("### Ticket"), len(scanned.findings))
            self.assertIn("## Migration tickets", tickets)
            self.assertIn("## Migration tickets", markdown)
            self.assertIn("Ticket 1: Spring Boot 2.x → 3.x 대형 마이그레이션", tickets)
            self.assertIn("- **Why**: 현재 2.7.18, 목표 3.5. Java 17 baseline과 Jakarta 전환이 필요합니다.", tickets)
            self.assertIn("- **Affected files/evidence**:", tickets)
            self.assertIn("`spring_boot_version=2.7.18`", tickets)
            self.assertIn("- **Suggested change**: Java 17+ 전환, javax→jakarta import 정리, Spring Security/Hibernate 변경점을 먼저 분리하세요.", tickets)
            self.assertIn("- **Validation command**: `./gradlew test`", tickets)
            self.assertIn("- **Rough effort**: L", tickets)

    def test_ticket_validation_command_points_to_single_nested_maven_module(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            module = root / "blog"
            module.mkdir()
            (module / "mvnw").write_text("#!/bin/sh\n")
            (module / "pom.xml").write_text(
                """
<project>
  <parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>2.6.2</version>
  </parent>
  <properties>
    <java.version>8</java.version>
  </properties>
</project>
""".strip()
            )

            scanned = scan_project(root, target_boot="3.5")
            tickets = render_tickets_markdown(scanned)

            self.assertIn("- **Validation command**: `cd blog && ./mvnw test`", tickets)

    def test_renders_tickets_json_for_jira_or_github_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "build.gradle").write_text(
                """
plugins {
    id 'org.springframework.boot' version '2.7.18'
}
sourceCompatibility = '11'
""".strip()
            )

            scanned = scan_project(root, target_boot="3.5")
            payload = json.loads(render_tickets_json(scanned))

            self.assertEqual(payload["project"], str(root))
            self.assertEqual(payload["target_boot"], "3.5")
            self.assertEqual(payload["risk_score"], scanned.score)
            self.assertEqual(len(payload["tickets"]), len(scanned.findings))
            first_ticket = payload["tickets"][0]
            self.assertEqual(first_ticket["id"], "SUR-001")
            self.assertEqual(first_ticket["rule_id"], "spring-boot-2-to-3")
            self.assertEqual(first_ticket["severity"], "high")
            self.assertEqual(first_ticket["rough_effort"], "L")
            self.assertEqual(first_ticket["validation_command"], "./gradlew test")
            self.assertIn("Spring Boot 2.x", first_ticket["title"])
            self.assertIn("spring_boot_version=2.7.18", first_ticket["evidence"])
    def test_renders_jira_csv_with_import_ready_ticket_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "build.gradle").write_text(
                """
plugins {
    id 'org.springframework.boot' version '2.7.18'
}
sourceCompatibility = '11'
""".strip()
            )

            scanned = scan_project(root, target_boot="3.5")
            rows = list(csv.DictReader(io.StringIO(render_jira_csv(scanned))))

            self.assertEqual(len(rows), len(scanned.findings))
            first_ticket = rows[0]
            self.assertEqual(first_ticket["Issue Type"], "Task")
            self.assertEqual(first_ticket["Summary"], "[SUR-001] Spring Boot 2.x → 3.x 대형 마이그레이션")
            self.assertEqual(first_ticket["Priority"], "Highest")
            self.assertEqual(first_ticket["Labels"], "spring-upgrade-radar,spring-boot-3,migration,high")
            self.assertIn("Rule: spring-boot-2-to-3", first_ticket["Description"])
            self.assertIn("Validation command: ./gradlew test", first_ticket["Description"])
            self.assertIn("spring_boot_version=2.7.18", first_ticket["Description"])
            self.assertEqual(first_ticket["Story Points"], "8")
    def test_renders_github_issues_markdown_with_copy_paste_ready_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "build.gradle").write_text(
                """
plugins {
    id 'org.springframework.boot' version '2.7.18'
}
sourceCompatibility = '11'
""".strip()
            )

            scanned = scan_project(root, target_boot="3.5")
            issues = render_github_issues_markdown(scanned)

            self.assertEqual(issues.count("## Issue SUR-"), len(scanned.findings))
            self.assertIn("# GitHub Issues - Spring Upgrade Radar", issues)
            self.assertIn("## Issue SUR-001", issues)
            self.assertIn("### Title", issues)
            self.assertIn("[SUR-001] Spring Boot 2.x → 3.x 대형 마이그레이션", issues)
            self.assertIn("### Labels", issues)
            self.assertIn("spring-upgrade-radar, spring-boot-3, migration, severity:high", issues)
            self.assertIn("### Body", issues)
            self.assertIn("#### Why", issues)
            self.assertIn("현재 2.7.18, 목표 3.5", issues)
            self.assertIn("#### Evidence", issues)
            self.assertIn("- `spring_boot_version=2.7.18`", issues)
            self.assertIn("#### Validation", issues)
            self.assertIn("```bash\n./gradlew test\n```", issues)
            self.assertIn("gh issue create --title", issues)

    def test_renders_executive_summary_with_grade_and_backlog(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "build.gradle").write_text(
                """
plugins {
    id 'org.springframework.boot' version '2.7.18'
}
sourceCompatibility = '11'
""".strip()
            )

            scanned = scan_project(root, target_boot="3.5")
            summary = render_executive_summary(scanned)

            self.assertIn("# Executive Summary", summary)
            self.assertIn("## 📊 개요", summary)
            self.assertIn("## 🎖️ Migration Readiness Grade", summary)
            self.assertIn("## ⚠️ Top 3 Risks", summary)
            self.assertIn("## 📋 Recommended Sprint Backlog", summary)
            # Risk score should appear
            self.assertIn(f"**{scanned.score}/100**", summary)
            # Grade should appear
            self.assertIn(_readiness_grade(scanned.score), summary)
            self.assertIn("| 70-100 | 🔴 **C (Critical)** |", summary)
            self.assertIn("| 30-69 | 🟡 **B (Ready)** |", summary)
            self.assertIn("| 0-29 | 🟢 **A (Excellent)** |", summary)
            # Sprint backlog items should appear
            self.assertIn("Sprint", summary)

    def test_executive_summary_top_risks_from_high_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            java_src = root / "src" / "main" / "java" / "com" / "example"
            java_src.mkdir(parents=True)
            (java_src / "App.java").write_text(
                "import javax.persistence.Entity;\nimport javax.servlet.http.HttpServletRequest;\n"
            )
            (root / "pom.xml").write_text(
                """
<project>
  <parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>2.7.18</version>
  </parent>
  <properties>
    <java.version>11</java.version>
  </properties>
</project>
""".strip()
            )

            scanned = scan_project(root, target_boot="3.5")
            summary = render_executive_summary(scanned)

            # Top 3 should include high severity findings
            high_count = sum(1 for f in scanned.findings if f.severity == "high")
            self.assertIn(f"### 1.", summary)
            if high_count > 0:
                self.assertIn("### 1.", summary)

    def test_executive_summary_empty_backlog_when_no_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pom.xml").write_text(
                """
<project>
  <parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.5.9</version>
  </parent>
  <properties>
    <java.version>21</java.version>
  </properties>
</project>
""".strip()
            )

            scanned = scan_project(root, target_boot="3.5")
            self.assertEqual(len(scanned.findings), 0)

            summary = render_executive_summary(scanned)
            self.assertIn("# Executive Summary", summary)
            self.assertIn("추가 작업 없음", summary)

    def test_readiness_grade_high_score(self):
        self.assertEqual(_readiness_grade(85), "C (Critical)")
        self.assertEqual(_readiness_grade(70), "C (Critical)")

    def test_readiness_grade_medium_score(self):
        self.assertEqual(_readiness_grade(50), "B (Ready)")
        self.assertEqual(_readiness_grade(30), "B (Ready)")

    def test_readiness_grade_low_score(self):
        self.assertEqual(_readiness_grade(10), "A (Excellent)")
        self.assertEqual(_readiness_grade(0), "A (Excellent)")

    def test_suggested_backlog_includes_java_migration(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "build.gradle").write_text(
                """
plugins {
    id 'org.springframework.boot' version '2.7.18'
}
sourceCompatibility = '11'
""".strip()
            )

            scanned = scan_project(root, target_boot="3.5")
            backlog = _suggested_backlog(scanned)
            backlog_titles = [item["title"] for item in backlog]
            # Should include Java migration sprint
            self.assertTrue(any("Java" in t for t in backlog_titles))

    def test_suggested_backlog_includes_jakarta_migration(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            java_src = root / "src" / "main" / "java" / "com" / "example"
            java_src.mkdir(parents=True)
            (java_src / "App.java").write_text("import javax.persistence.Entity;\n")
            (root / "pom.xml").write_text(
                """
<project>
  <parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>2.7.18</version>
  </parent>
</project>
""".strip()
            )

            scanned = scan_project(root, target_boot="3.5")
            backlog = _suggested_backlog(scanned)
            backlog_titles = [item["title"] for item in backlog]
            # Should include jakarta migration sprint
            self.assertTrue(any("jakarta" in t.lower() for t in backlog_titles))

    def test_render_markdown_embeds_executive_summary_with_all_sections(self):
        """Main report should include Executive Summary at the top:
        Overview, Migration Readiness Grade, Top 3 Risks, Estimated Roadmap,
        and Recommended Sprint Backlog."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            java_src = root / "src" / "main" / "java" / "com" / "example"
            java_src.mkdir(parents=True)
            (java_src / "App.java").write_text(
                "import javax.persistence.Entity;\n"
                "import javax.servlet.http.HttpServletRequest;\n"
            )
            (root / "build.gradle").write_text(
                """
plugins {
    id 'org.springframework.boot' version '2.7.18'
}
sourceCompatibility = '11'
""".strip()
            )

            scanned = scan_project(root, target_boot="3.5")
            md = render_markdown(scanned)

            # Executive Summary header should appear BEFORE findings
            self.assertIn("# Executive Summary", md)
            exec_pos = md.index("# Executive Summary")
            self.assertIn("## Findings", md)
            self.assertLess(exec_pos, md.index("## Findings"))

            # All required sections
            self.assertIn("## 📊 개요", md)
            self.assertIn("## 🎖️ Migration Readiness Grade", md)
            self.assertIn("## ⚠️ Top 3 Risks", md)
            self.assertIn("## 🗺️ Estimated Roadmap", md)
            self.assertIn("## 📋 Recommended Sprint Backlog", md)

            # Grade should appear
            self.assertIn(_readiness_grade(scanned.score), md)

            # Roadmap should have sprint estimates
            self.assertIn("Sprint", md)

    def test_render_markdown_roadmap_has_time_estimates(self):
        """Estimated Roadmap should show time estimates for each sprint."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            java_src = root / "src" / "main" / "java" / "com" / "example"
            java_src.mkdir(parents=True)
            (java_src / "App.java").write_text("import javax.persistence.Entity;\n")
            (root / "build.gradle").write_text(
                """
plugins {
    id 'org.springframework.boot' version '2.7.18'
}
sourceCompatibility = '11'
""".strip()
            )

            scanned = scan_project(root, target_boot="3.5")
            md = render_markdown(scanned)

            # Roadmap should contain time estimates like "2 weeks", "1 week"
            roadmap_section = md[md.index("## 🗺️ Estimated Roadmap"):]
            self.assertIn("2 주", roadmap_section)
            self.assertIn("1 주", roadmap_section)

    def test_render_markdown_empty_findings_has_safe_exec_summary(self):
        """When no findings, main report should still render a safe executive summary."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pom.xml").write_text(
                """
<project>
  <parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.5.9</version>
  </parent>
  <properties>
    <java.version>21</java.version>
  </properties>
</project>
""".strip()
            )

            scanned = scan_project(root, target_boot="3.5")
            self.assertEqual(len(scanned.findings), 0)

            md = render_markdown(scanned)
            self.assertIn("# Executive Summary", md)
            self.assertIn("지원 종료 또는 마이그레이션 위험 신호를 찾지 못했습니다", md)

    def test_render_markdown_includes_product_cta_footer(self):
        """Generated reports should include a lightweight CTA so samples can support lead generation."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "build.gradle").write_text(
                """
plugins {
    id 'org.springframework.boot' version '2.7.18'
}
sourceCompatibility = '11'
""".strip()
            )

            scanned = scan_project(root, target_boot="3.5")
            md = render_markdown(scanned)

            self.assertIn("## Need a full migration plan?", md)
            self.assertIn("Pro report", md)
            self.assertIn("Spring Boot 3 migration assessment", md)


if __name__ == "__main__":
    unittest.main()
