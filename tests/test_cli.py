import csv
import subprocess
import sys
import tempfile
import unittest
import json
from pathlib import Path


class CliTests(unittest.TestCase):
    def test_cli_writes_markdown_and_html_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "app"
            root.mkdir()
            (root / "build.gradle").write_text(
                """
plugins {
    id 'org.springframework.boot' version '2.7.18'
}
sourceCompatibility = '11'
""".strip()
            )
            markdown = Path(tmp) / "report.md"
            html = Path(tmp) / "report.html"
            tickets_json = Path(tmp) / "tickets.json"
            jira_csv = Path(tmp) / "jira.csv"
            github_issues = Path(tmp) / "github-issues.md"
            exec_summary = Path(tmp) / "exec-summary.md"

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "spring_upgrade_radar.cli",
                    "scan",
                    str(root),
                    "--target",
                    "3.5",
                    "--output",
                    str(markdown),
                    "--html-output",
                    str(html),
                    "--tickets-json",
                    str(tickets_json),
                    "--jira-csv",
                    str(jira_csv),
                    "--github-issues-md",
                    str(github_issues),
                    "--exec-summary-md",
                    str(exec_summary),
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Risk score", result.stdout)
            self.assertTrue(markdown.exists())
            self.assertTrue(html.exists())
            self.assertTrue(tickets_json.exists())
            self.assertTrue(jira_csv.exists())
            self.assertTrue(github_issues.exists())
            self.assertIn("Executive Summary", result.stdout)
            self.assertTrue(exec_summary.exists())
            self.assertIn("## 📊 개요", exec_summary.read_text())
            self.assertIn("## 📋 Recommended Sprint Backlog", exec_summary.read_text())
            self.assertIn("Spring Boot 2.x", markdown.read_text())
            self.assertIn("<html", html.read_text())
            tickets = json.loads(tickets_json.read_text())
            with jira_csv.open() as jira_file:
                jira_rows = list(csv.DictReader(jira_file))
            self.assertIn("Tickets JSON", result.stdout)
            self.assertIn("Jira CSV", result.stdout)
            self.assertIn("GitHub issues Markdown", result.stdout)
            self.assertEqual(tickets["tickets"][0]["id"], "SUR-001")
            self.assertEqual(tickets["tickets"][0]["rule_id"], "spring-boot-2-to-3")
            self.assertEqual(jira_rows[0]["Summary"], "[SUR-001] Spring Boot 2.x → 3.x 대형 마이그레이션")
            self.assertIn("## Issue SUR-001", github_issues.read_text())


if __name__ == "__main__":
    unittest.main()
