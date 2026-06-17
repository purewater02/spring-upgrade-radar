# Spring Boot 2.7 to 3.x Migration Checklist

Spring Boot 3 is not just another dependency bump. For many teams, the upgrade from Spring Boot 2.7 to 3.x combines several migrations at once: Java 17, Jakarta EE namespaces, Spring Security 6, Hibernate 6, dependency updates, and CI/runtime changes.

This checklist helps you estimate the migration before you start changing code.

---

## 1. Confirm your current baseline

Before planning the upgrade, capture the current project state:

- Spring Boot version
- Java version
- build tool: Maven or Gradle
- Spring Security version and configuration style
- Hibernate/JPA usage
- servlet/JSP/JSTL usage
- database driver versions
- CI JDK version
- test coverage and critical integration tests

Why this matters:

> Spring Boot 3 requires Java 17+. If your project is still on Java 8 or 11, the Java migration should be planned before the Spring Boot version bump.

---

## 2. Move to Java 17+ first

Spring Boot 3 requires Java 17 or newer. Treat this as a separate migration step.

Checklist:

- update local JDK to 17 or 21
- update CI runner JDK
- update Maven/Gradle toolchain settings
- verify compiler source/target compatibility
- run the full test suite before touching Spring Boot

Suggested validation:

```bash
./mvnw test
# or
./gradlew test
```

If Java 17 alone breaks the build, solve that before upgrading Spring Boot.

---

## 3. Scan for `javax.*` imports

Spring Boot 3 is based on Jakarta EE 10. Many Java EE APIs moved from `javax.*` to `jakarta.*`.

High-priority areas:

- `javax.persistence.*`
- `javax.validation.*`
- `javax.servlet.*`
- `javax.annotation.*`
- JSP/JSTL tag libraries

Example:

```java
import javax.persistence.Entity;
```

becomes:

```java
import jakarta.persistence.Entity;
```

This change can cascade into Hibernate, validation, servlet filters, generated sources, and third-party dependencies.

---

## 4. Check Spring Security 5 → 6 changes

Spring Security 6 removes or replaces many older configuration patterns.

Look for:

- `WebSecurityConfigurerAdapter`
- `authorizeRequests()`
- `antMatchers()`
- `@EnableGlobalMethodSecurity`

Modern Spring Security configurations usually use:

- `SecurityFilterChain` bean
- `authorizeHttpRequests()`
- `requestMatchers()`
- `@EnableMethodSecurity`

Do not mix this refactor into a broad dependency upgrade PR. It is easier to review and test as a separate step.

---

## 5. Review Hibernate 5 → 6 risks

If your app uses JPA heavily, Hibernate 6 can introduce behavior changes even after the code compiles.

Review:

- custom dialects
- native queries
- JPQL/HQL queries
- naming strategies
- enum mappings
- date/time mappings
- lazy loading assumptions
- repository integration tests

Recommended approach:

1. migrate imports first,
2. update dependencies,
3. run repository tests,
4. validate critical queries manually if needed.

---

## 6. Check dependency coordinates and compatibility

Some libraries changed coordinates or require major upgrades for Spring Boot 3 compatibility.

Common examples:

- MySQL Connector/J: `mysql:mysql-connector-java` → `com.mysql:mysql-connector-j`
- Springfox → springdoc-openapi
- QueryDSL Jakarta classifier or annotation processor changes
- old servlet/JSP/JSTL dependencies

Create a dependency matrix:

| Area | Current | Target | Risk |
| --- | --- | --- | --- |
| Java | 8/11 | 17/21 | High |
| Spring Boot | 2.7.x | 3.x | High |
| Security | 5.x | 6.x | Medium/High |
| Hibernate | 5.x | 6.x | Medium/High |
| OpenAPI | Springfox | springdoc | Medium |

---

## 7. Split the migration into reviewable phases

A safe upgrade plan usually looks like this:

### Sprint 1: Java 17+ baseline

- update JDK/toolchain
- fix Java compatibility issues
- make CI green

### Sprint 2: Jakarta namespace migration

- replace `javax.*` imports
- update affected dependencies
- run compile and unit tests

### Sprint 3: major framework dependencies

- Spring Security 6 changes
- Hibernate 6 validation
- OpenAPI/library migrations

### Sprint 4: Spring Boot 3 upgrade validation

- update Spring Boot parent/plugin
- run full test suite
- run smoke tests
- verify runtime configuration

---

## 8. Generate migration tickets

The migration becomes easier when each risk is converted into an actionable ticket.

A good migration ticket should include:

- title
- rule or risk category
- why it matters
- affected files/evidence
- suggested change
- validation command
- rough effort

Example:

```md
Title: Replace javax.persistence imports with jakarta.persistence
Why: Spring Boot 3 uses Jakarta Persistence APIs.
Evidence: src/main/java/.../User.java imports javax.persistence.Entity
Suggested change: replace imports and validate Hibernate 6/JPA 3 compatibility.
Validation: ./mvnw test
Effort: L
```

---

## 9. Estimate before committing the team

Before assigning the upgrade, answer these questions:

- Is the project already on Java 17?
- How many `javax.*` imports exist?
- Does it use legacy Spring Security configuration?
- Does it use Hibernate-specific behavior?
- Are critical repository/controller tests available?
- Can CI run the migration branch reliably?
- How many separate PRs will the migration need?

If you cannot answer these quickly, run a migration scan first.

---

## Generate a free migration report

Spring Upgrade Radar is a local-first CLI that scans a Spring Boot project and generates:

- executive summary
- risk score
- top risks
- estimated roadmap
- migration tickets
- Jira/GitHub export files

Quick start:

```bash
git clone https://github.com/purewater02/spring-upgrade-radar.git
cd spring-upgrade-radar
python3 -m venv .venv
. .venv/bin/activate
pip install -e .

spring-upgrade-radar scan /path/to/your/spring-project \
  --target 3.5 \
  --output out/report.md \
  --html-output out/report.html \
  --tickets-json out/tickets.json \
  --jira-csv out/jira.csv \
  --github-issues-md out/github-issues.md
```

CTA:

> Know your Spring Boot 3 migration risk before the upgrade starts. Generate a free migration report.
