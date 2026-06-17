import tempfile
import unittest
from pathlib import Path

from spring_upgrade_radar.scanner import scan_project


class ScannerTests(unittest.TestCase):
    def test_scans_gradle_spring_boot_2_project_and_reports_jakarta_and_eol_risks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "build.gradle").write_text(
                """
plugins {
    id 'java'
    id 'org.springframework.boot' version '2.7.18'
}

java {
    sourceCompatibility = JavaVersion.VERSION_11
}

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'io.springfox:springfox-boot-starter:3.0.0'
    implementation 'com.querydsl:querydsl-jpa:5.0.0'
}
""".strip()
            )
            (root / "src/main/java/com/example/UserController.java").parent.mkdir(parents=True)
            (root / "src/main/java/com/example/UserController.java").write_text(
                """
package com.example;

import javax.persistence.Entity;
import javax.validation.Valid;

@Entity
class UserController {
}
""".strip()
            )

            report = scan_project(root, target_boot="3.5")

            self.assertEqual(report.project_path, root)
            self.assertEqual(report.build_tool, "gradle")
            self.assertEqual(report.spring_boot_version, "2.7.18")
            self.assertEqual(report.java_version, "11")
            self.assertGreaterEqual(report.score, 70)
            rule_ids = {finding.rule_id for finding in report.findings}
            self.assertIn("spring-boot-2-to-3", rule_ids)
            self.assertIn("java-baseline", rule_ids)
            self.assertIn("jakarta-persistence-imports", rule_ids)
            self.assertIn("jakarta-validation-imports", rule_ids)
            self.assertIn("springfox", rule_ids)
            self.assertIn("querydsl-jakarta", rule_ids)


if __name__ == "__main__":
    unittest.main()
