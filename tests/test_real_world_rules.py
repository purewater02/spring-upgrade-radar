import tempfile
import unittest
from pathlib import Path

from spring_upgrade_radar.scanner import scan_project


class RealWorldRuleTests(unittest.TestCase):
    def test_scans_single_module_repo_from_parent_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            module = root / "blog"
            module.mkdir()
            (module / "pom.xml").write_text(
                """
<project>
  <parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>2.6.2</version>
  </parent>
  <properties><java.version>1.8</java.version></properties>
</project>
""".strip()
            )

            report = scan_project(root, target_boot="3.5")

            self.assertEqual(report.build_tool, "maven")
            self.assertEqual(report.spring_boot_version, "2.6.2")
            self.assertEqual(report.java_version, "8")

    def test_detects_legacy_spring_security_jsp_jstl_and_mysql_connector(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pom.xml").write_text(
                """
<project>
  <parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>2.6.2</version>
  </parent>
  <properties><java.version>1.8</java.version></properties>
  <dependencies>
    <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-security</artifactId></dependency>
    <dependency><groupId>org.apache.tomcat.embed</groupId><artifactId>tomcat-embed-jasper</artifactId></dependency>
    <dependency><groupId>javax.servlet</groupId><artifactId>jstl</artifactId></dependency>
    <dependency><groupId>mysql</groupId><artifactId>mysql-connector-java</artifactId></dependency>
  </dependencies>
</project>
""".strip()
            )
            security = root / "src/main/java/com/example/SecurityConfig.java"
            security.parent.mkdir(parents=True)
            security.write_text(
                """
import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;
import org.springframework.security.config.annotation.method.configuration.EnableGlobalMethodSecurity;

class SecurityConfig extends WebSecurityConfigurerAdapter {
  void configure(org.springframework.security.config.annotation.web.builders.HttpSecurity http) throws Exception {
    http.authorizeRequests().antMatchers("/**").permitAll();
  }
}
""".strip()
            )

            report = scan_project(root, target_boot="3.5")
            rule_ids = {finding.rule_id for finding in report.findings}

            self.assertIn("spring-security-legacy-config", rule_ids)
            self.assertIn("jsp-jstl-jakarta", rule_ids)
            self.assertIn("mysql-connector-coordinates", rule_ids)

    def test_splits_javax_imports_into_persistence_validation_and_servlet_tickets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pom.xml").write_text(
                """
<project>
  <parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>2.7.18</version>
  </parent>
  <properties><java.version>11</java.version></properties>
</project>
""".strip()
            )
            controller = root / "src/main/java/com/example/UserController.java"
            controller.parent.mkdir(parents=True)
            controller.write_text(
                """
import javax.persistence.Entity;
import javax.validation.Valid;
import javax.servlet.http.HttpServletRequest;

class UserController {
}
""".strip()
            )

            report = scan_project(root, target_boot="3.5")
            findings = {finding.rule_id: finding for finding in report.findings}

            self.assertIn("jakarta-persistence-imports", findings)
            self.assertIn("jakarta-validation-imports", findings)
            self.assertIn("jakarta-servlet-imports", findings)
            self.assertNotIn("jakarta-imports", findings)
            self.assertIn("javax.persistence.Entity", findings["jakarta-persistence-imports"].evidence[0])
            self.assertIn("Bean Validation", findings["jakarta-validation-imports"].recommendation)
            self.assertIn("Servlet API", findings["jakarta-servlet-imports"].recommendation)

    def test_detects_jsp_view_stack_from_jsp_files_and_application_properties(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pom.xml").write_text(
                """
<project>
  <parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>2.7.18</version>
  </parent>
  <properties><java.version>11</java.version></properties>
</project>
""".strip()
            )
            jsp = root / "src/main/webapp/WEB-INF/views/index.jsp"
            jsp.parent.mkdir(parents=True)
            jsp.write_text("<%@ taglib prefix=\"c\" uri=\"http://java.sun.com/jsp/jstl/core\" %>")
            app = root / "src/main/resources/application.yml"
            app.parent.mkdir(parents=True)
            app.write_text("spring:\n  mvc:\n    view:\n      prefix: /WEB-INF/views/\n      suffix: .jsp\n")

            report = scan_project(root, target_boot="3.5")
            jsp_finding = next(f for f in report.findings if f.rule_id == "jsp-jstl-jakarta")

            self.assertTrue(any("index.jsp" in item for item in jsp_finding.evidence))
            self.assertTrue(any("application.yml" in item for item in jsp_finding.evidence))

    def test_merges_duplicate_rule_findings_into_one_ticket(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pom.xml").write_text(
                """
<project>
  <parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>2.7.18</version>
  </parent>
  <properties><java.version>11</java.version></properties>
  <dependencies>
    <dependency><groupId>org.apache.tomcat.embed</groupId><artifactId>tomcat-embed-jasper</artifactId></dependency>
    <dependency><groupId>javax.servlet</groupId><artifactId>jstl</artifactId></dependency>
  </dependencies>
</project>
""".strip()
            )
            jsp = root / "src/main/webapp/WEB-INF/views/index.jsp"
            jsp.parent.mkdir(parents=True)
            jsp.write_text("<%@ taglib prefix=\"c\" uri=\"http://java.sun.com/jsp/jstl/core\" %>")

            report = scan_project(root, target_boot="3.5")
            jsp_findings = [finding for finding in report.findings if finding.rule_id == "jsp-jstl-jakarta"]

            self.assertEqual(len(jsp_findings), 1)
            self.assertTrue(any("index.jsp" in item for item in jsp_findings[0].evidence))
            self.assertTrue(any("tomcat-embed-jasper/jstl" in item for item in jsp_findings[0].evidence))

    def test_detects_non_executable_maven_wrapper(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pom.xml").write_text(
                """
<project>
  <parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>2.7.18</version>
  </parent>
  <properties><java.version>17</java.version></properties>
</project>
""".strip()
            )
            mvnw = root / "mvnw"
            mvnw.write_text("#!/bin/sh\n")
            mvnw.chmod(0o644)

            report = scan_project(root, target_boot="3.5")
            wrapper_finding = next(f for f in report.findings if f.rule_id == "maven-wrapper-executable")

            self.assertEqual(wrapper_finding.severity, "low")
            self.assertIn("mvnw is not executable", wrapper_finding.evidence)
            self.assertIn("chmod +x mvnw", wrapper_finding.recommendation)


if __name__ == "__main__":
    unittest.main()
