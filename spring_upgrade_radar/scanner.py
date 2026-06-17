from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    title: str
    detail: str
    evidence: list[str]
    recommendation: str


@dataclass(frozen=True)
class ScanReport:
    project_path: Path
    build_tool: str
    spring_boot_version: str | None
    java_version: str | None
    target_boot: str
    score: int
    findings: list[Finding]


def scan_project(project_path: str | Path, target_boot: str = "3.5") -> ScanReport:
    root = Path(project_path).resolve()
    build_tool, build_text = _load_build_file(root)
    spring_boot_version = _detect_spring_boot_version(build_tool, build_text)
    java_version = _detect_java_version(build_tool, build_text)

    findings: list[Finding] = []
    findings.extend(_spring_boot_support_findings(spring_boot_version, target_boot))
    findings.extend(_java_findings(java_version, target_boot))
    findings.extend(_source_findings(root))
    findings.extend(_dependency_findings(build_text, target_boot))
    findings.extend(_project_hygiene_findings(root, build_tool))
    findings = _merge_findings_by_rule(findings)

    score = min(100, sum(_severity_points(f.severity) for f in findings))
    return ScanReport(
        project_path=root,
        build_tool=build_tool,
        spring_boot_version=spring_boot_version,
        java_version=java_version,
        target_boot=target_boot,
        score=score,
        findings=findings,
    )


def _load_build_file(root: Path) -> tuple[str, str]:
    gradle_candidates = [root / "build.gradle", root / "build.gradle.kts"]
    for candidate in gradle_candidates:
        if candidate.exists():
            return "gradle", candidate.read_text(errors="ignore")
    pom = root / "pom.xml"
    if pom.exists():
        return "maven", pom.read_text(errors="ignore")

    nested_builds = [
        path
        for path in root.rglob("*")
        if path.name in {"pom.xml", "build.gradle", "build.gradle.kts"}
        and not any(part in {"build", "target", ".gradle", ".git"} for part in path.parts)
    ]
    if len(nested_builds) == 1:
        nested = nested_builds[0]
        return ("maven" if nested.name == "pom.xml" else "gradle"), nested.read_text(errors="ignore")
    raise FileNotFoundError(f"No build.gradle, build.gradle.kts, or pom.xml found under {root}")


def _detect_spring_boot_version(build_tool: str, text: str) -> str | None:
    if build_tool == "gradle":
        patterns = [
            r"org\.springframework\.boot['\"]\s+version\s+['\"]([^'\"]+)",
            r"id\(['\"]org\.springframework\.boot['\"]\)\s+version\s+['\"]([^'\"]+)",
            r"springBootVersion\s*=\s*['\"]([^'\"]+)",
        ]
        return _first_regex(patterns, text)

    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return _first_regex([r"<spring-boot.version>([^<]+)</spring-boot.version>", r"<version>(\d+\.\d+\.\d+)</version>"], text)

    ns = _xml_namespace(root)
    parent_artifact = root.findtext(f"{ns}parent/{ns}artifactId")
    if parent_artifact == "spring-boot-starter-parent":
        return root.findtext(f"{ns}parent/{ns}version")
    return root.findtext(f"{ns}properties/{ns}spring-boot.version")


def _detect_java_version(build_tool: str, text: str) -> str | None:
    if build_tool == "gradle":
        patterns = [
            r"sourceCompatibility\s*=\s*JavaVersion\.VERSION_(\d+)",
            r"sourceCompatibility\s*=\s*['\"]?(\d+)['\"]?",
            r"languageVersion\s*=\s*JavaLanguageVersion\.of\((\d+)\)",
        ]
        return _first_regex(patterns, text)

    match = re.search(r"<java.version>([^<]+)</java.version>", text)
    if match:
        return match.group(1).removeprefix("1.")
    return None


def _spring_boot_support_findings(version: str | None, target_boot: str) -> list[Finding]:
    if not version:
        return [Finding("spring-boot-version-missing", "medium", "Spring Boot 버전 미탐지", "빌드 파일에서 Spring Boot 버전을 찾지 못했습니다.", [], "Spring Boot plugin 또는 parent 버전을 명시하세요.")]

    major_minor = _major_minor(version)
    if major_minor.startswith("2."):
        return [Finding("spring-boot-2-to-3", "high", "Spring Boot 2.x → 3.x 대형 마이그레이션", f"현재 {version}, 목표 {target_boot}. Java 17 baseline과 Jakarta 전환이 필요합니다.", [f"spring_boot_version={version}"], "Java 17+ 전환, javax→jakarta import 정리, Spring Security/Hibernate 변경점을 먼저 분리하세요.")]
    if major_minor in {"3.0", "3.1", "3.2", "3.3", "3.4"}:
        return [Finding("spring-boot-support-window", "medium", "Spring Boot 3.x 지원 종료/EOL 점검 필요", f"현재 {version}. target {target_boot} 기준 최신 supported 라인으로 올리는 계획이 필요합니다.", [f"spring_boot_version={version}"], "3.5+ 또는 조직의 지원 정책상 LTS/상용 지원 라인으로 업그레이드하세요.")]
    return []


def _java_findings(version: str | None, target_boot: str) -> list[Finding]:
    if not version:
        return [Finding("java-version-missing", "low", "Java 버전 미탐지", "빌드 파일에서 Java 버전을 찾지 못했습니다.", [], "toolchain 또는 java.version을 명시하세요.")]
    try:
        java = int(version)
    except ValueError:
        return []
    if java < 17:
        return [Finding("java-baseline", "high", "Java 17 baseline 미달", f"현재 Java {version}. Spring Boot 3.x는 Java 17 이상이 필요합니다.", [f"java_version={version}"], "먼저 JDK 17/21 빌드와 런타임 호환성을 확보하세요.")]
    return []


def _source_findings(root: Path) -> list[Finding]:
    javax_hits_by_namespace: dict[str, list[str]] = {
        "persistence": [],
        "validation": [],
        "servlet": [],
        "other": [],
    }
    security_hits: list[str] = []
    jsp_hits: list[str] = []
    for path in root.rglob("*.java"):
        if any(part in {"build", "target", ".gradle", ".git"} for part in path.parts):
            continue
        text = path.read_text(errors="ignore")
        for line_no, line in enumerate(text.splitlines(), start=1):
            if "import javax." in line:
                bucket = _javax_namespace_bucket(line)
                hits = javax_hits_by_namespace[bucket]
                if len(hits) < 10:
                    hits.append(f"{path.relative_to(root)}:{line_no}: {line.strip()}")
        for token in ("WebSecurityConfigurerAdapter", "authorizeRequests()", "antMatchers(", "@EnableGlobalMethodSecurity"):
            if token in text:
                security_hits.append(f"{path.relative_to(root)}: {token}")

    for path in root.rglob("*.jsp"):
        if _is_ignored_path(path):
            continue
        jsp_hits.append(f"{path.relative_to(root)}")

    for path in root.rglob("application*.yml"):
        if _is_ignored_path(path):
            continue
        text = path.read_text(errors="ignore").lower()
        if "mvc" in text and "view" in text and ".jsp" in text:
            jsp_hits.append(f"{path.relative_to(root)}: spring.mvc.view JSP configuration")
    for path in root.rglob("application*.properties"):
        if _is_ignored_path(path):
            continue
        text = path.read_text(errors="ignore").lower()
        if "spring.mvc.view" in text and ".jsp" in text:
            jsp_hits.append(f"{path.relative_to(root)}: spring.mvc.view JSP configuration")

    findings: list[Finding] = []
    for bucket, hits in javax_hits_by_namespace.items():
        if hits:
            findings.append(_javax_finding(bucket, hits))
    if security_hits:
        findings.append(Finding("spring-security-legacy-config", "high", "Spring Security 5 스타일 설정 발견", "WebSecurityConfigurerAdapter/authorizeRequests/antMatchers/EnableGlobalMethodSecurity는 Spring Security 6 전환 시 SecurityFilterChain/requestMatchers/EnableMethodSecurity 패턴으로 재작성해야 합니다.", security_hits[:10], "SecurityFilterChain @Bean 기반으로 재작성하고 antMatchers→requestMatchers, authorizeRequests→authorizeHttpRequests로 분리 마이그레이션하세요."))
    if jsp_hits:
        findings.append(Finding("jsp-jstl-jakarta", "medium", "JSP view stack 발견", "JSP view stack은 Spring Boot 3/Tomcat 10의 jakarta.servlet 환경에서 taglib와 렌더링 호환성 점검이 필요합니다.", jsp_hits[:10], "JSP/JSTL 의존성을 Jakarta 호환 좌표로 전환하고 주요 view 렌더링 회귀 테스트를 추가하세요."))
    return findings


def _javax_namespace_bucket(line: str) -> str:
    if "javax.persistence." in line:
        return "persistence"
    if "javax.validation." in line:
        return "validation"
    if "javax.servlet." in line:
        return "servlet"
    return "other"


def _javax_finding(bucket: str, hits: list[str]) -> Finding:
    if bucket == "persistence":
        return Finding("jakarta-persistence-imports", "high", "JPA javax.persistence import 발견", f"{len(hits)}개 이상의 JPA import가 Jakarta Persistence 전환 대상입니다.", hits, "javax.persistence.*를 jakarta.persistence.*로 전환하고 Hibernate 6/JPA 3 호환성을 엔티티/레포지토리 테스트로 검증하세요.")
    if bucket == "validation":
        return Finding("jakarta-validation-imports", "medium", "Bean Validation javax.validation import 발견", f"{len(hits)}개 이상의 Bean Validation import가 Jakarta Validation 전환 대상입니다.", hits, "Bean Validation API의 javax.validation.*을 jakarta.validation.*로 전환하고 validation starter 및 DTO 검증 테스트를 확인하세요.")
    if bucket == "servlet":
        return Finding("jakarta-servlet-imports", "high", "Servlet javax.servlet import 발견", f"{len(hits)}개 이상의 Servlet API import가 Jakarta Servlet 전환 대상입니다.", hits, "Servlet API의 javax.servlet.*을 jakarta.servlet.*로 전환하고 filter/listener/interceptor 동작을 통합 테스트로 확인하세요.")
    return Finding("jakarta-other-imports", "medium", "기타 javax.* import 발견", f"{len(hits)}개 이상의 기타 Java EE import가 Jakarta 전환 대상일 수 있습니다.", hits, "해당 javax.* API의 Jakarta 대응 패키지와 의존성 좌표를 확인하세요.")


def _project_hygiene_findings(root: Path, build_tool: str) -> list[Finding]:
    findings: list[Finding] = []
    if build_tool == "maven":
        for mvnw in root.rglob("mvnw"):
            if _is_ignored_path(mvnw):
                continue
            if not mvnw.stat().st_mode & 0o111:
                rel = mvnw.relative_to(root).as_posix()
                command = f"chmod +x {rel}"
                findings.append(Finding("maven-wrapper-executable", "low", "Maven Wrapper 실행 권한 누락", "CI나 로컬 검증에서 ./mvnw test가 권한 문제로 실패할 수 있습니다.", [f"{rel} is not executable"], f"{command}를 실행하고 wrapper 기반 검증 명령을 CI에 사용하세요."))
    return findings


def _dependency_findings(text: str, target_boot: str) -> list[Finding]:
    findings: list[Finding] = []
    if "springfox" in text.lower():
        findings.append(Finding("springfox", "medium", "Springfox 의존성 발견", "Springfox는 Spring Boot 3 전환 시 springdoc-openapi로 대체하는 경우가 많습니다.", ["springfox"], "springdoc-openapi 2.x starter로 대체하고 Swagger 설정을 정리하세요."))
    if "querydsl-jpa" in text.lower():
        findings.append(Finding("querydsl-jakarta", "medium", "QueryDSL JPA Jakarta classifier 점검", "Spring Boot 3/Jakarta 환경에서는 QueryDSL JPA jakarta classifier/annotation processor 설정이 필요할 수 있습니다.", ["querydsl-jpa"], "querydsl-jpa:jakarta 및 annotationProcessor 설정을 확인하세요."))
    if "hibernate-core" in text.lower():
        findings.append(Finding("hibernate-major", "medium", "Hibernate major upgrade 영향 점검", "Spring Boot 3는 Hibernate 6 계열로 이동합니다.", ["hibernate-core"], "native query, dialect, type mapping, QueryDSL 호환성을 별도 테스트하세요."))
    if "tomcat-embed-jasper" in text.lower() or "<artifactid>jstl</artifactid>" in text.lower() or "javax.servlet" in text.lower():
        findings.append(Finding("jsp-jstl-jakarta", "medium", "JSP/JSTL Jakarta 전환 점검", "JSP view와 javax.servlet:jstl 조합은 Boot 3/Tomcat 10의 jakarta.servlet 환경에서 의존성 좌표와 taglib 호환성을 점검해야 합니다.", ["tomcat-embed-jasper/jstl"], "JSTL은 jakarta.servlet.jsp.jstl 계열 의존성으로 전환하고 JSP taglib URI/뷰 렌더링 회귀 테스트를 준비하세요."))
    if "<groupid>mysql</groupid>" in text.lower() and "<artifactid>mysql-connector-java</artifactid>" in text.lower():
        findings.append(Finding("mysql-connector-coordinates", "low", "MySQL Connector/J 좌표 변경 점검", "구형 mysql:mysql-connector-java 좌표를 사용 중입니다. 최신 Connector/J는 com.mysql:mysql-connector-j 좌표를 사용합니다.", ["mysql:mysql-connector-java"], "com.mysql:mysql-connector-j로 전환하고 드라이버 클래스 자동 감지를 확인하세요."))
    return findings


def _severity_points(severity: str) -> int:
    return {"high": 30, "medium": 15, "low": 5}.get(severity, 0)


def _merge_findings_by_rule(findings: list[Finding]) -> list[Finding]:
    merged: dict[str, Finding] = {}
    for finding in findings:
        existing = merged.get(finding.rule_id)
        if existing is None:
            merged[finding.rule_id] = finding
            continue

        evidence = list(existing.evidence)
        for item in finding.evidence:
            if item not in evidence:
                evidence.append(item)
        merged[finding.rule_id] = Finding(
            rule_id=existing.rule_id,
            severity=_higher_severity(existing.severity, finding.severity),
            title=existing.title,
            detail=existing.detail,
            evidence=evidence,
            recommendation=existing.recommendation,
        )
    return list(merged.values())


def _higher_severity(left: str, right: str) -> str:
    order = {"low": 1, "medium": 2, "high": 3}
    return left if order.get(left, 0) >= order.get(right, 0) else right


def _is_ignored_path(path: Path) -> bool:
    return any(part in {"build", "target", ".gradle", ".git"} for part in path.parts)


def _first_regex(patterns: list[str], text: str) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            return match.group(1)
    return None


def _major_minor(version: str) -> str:
    parts = version.split(".")
    return ".".join(parts[:2]) if len(parts) >= 2 else version


def _xml_namespace(root: ET.Element) -> str:
    if root.tag.startswith("{"):
        return root.tag.split("}", 1)[0] + "}"
    return ""
