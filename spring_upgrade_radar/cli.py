from __future__ import annotations

import argparse
from pathlib import Path

from spring_upgrade_radar.report import (
    render_executive_summary, render_github_issues_markdown,
    render_html, render_jira_csv, render_markdown, render_tickets_json,
)
from spring_upgrade_radar.scanner import scan_project


def write_output(path: str, content: str) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="spring-upgrade-radar")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Scan a Spring Boot project")
    scan.add_argument("project", help="Path to the project root")
    scan.add_argument("--target", default="3.5", help="Target Spring Boot minor version")
    scan.add_argument("--output", help="Path to write Markdown report")
    scan.add_argument("--html-output", help="Path to write HTML report")
    scan.add_argument("--tickets-json", help="Path to write migration tickets JSON")
    scan.add_argument("--jira-csv", help="Path to write Jira-importable migration tickets CSV")
    scan.add_argument("--github-issues-md", help="Path to write copy/paste-ready GitHub Issues Markdown")
    scan.add_argument("--exec-summary-md", help="Path to write Executive Summary Markdown (leader-ready)")

    args = parser.parse_args(argv)
    if args.command == "scan":
        report = scan_project(args.project, target_boot=args.target)
        markdown = render_markdown(report)
        print(f"Risk score: {report.score}/100")
        print(f"Findings: {len(report.findings)}")
        if args.output:
            write_output(args.output, markdown)
            print(f"Markdown report: {args.output}")
        else:
            print(markdown)
        if args.html_output:
            write_output(args.html_output, render_html(report))
            print(f"HTML report: {args.html_output}")
        if args.tickets_json:
            write_output(args.tickets_json, render_tickets_json(report))
            print(f"Tickets JSON: {args.tickets_json}")
        if args.jira_csv:
            write_output(args.jira_csv, render_jira_csv(report))
            print(f"Jira CSV: {args.jira_csv}")
        if args.github_issues_md:
            write_output(args.github_issues_md, render_github_issues_markdown(report))
            print(f"GitHub issues Markdown: {args.github_issues_md}")
        if args.exec_summary_md:
            write_output(args.exec_summary_md, render_executive_summary(report))
            print(f"Executive Summary: {args.exec_summary_md}")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
