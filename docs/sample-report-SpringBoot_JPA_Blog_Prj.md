# Executive Summary

- **Project**: `/home/puredev/Documents/GitHub/SpringBoot_JPA_Blog_Prj`
- **Spring Boot**: 2.6.2 → **3.5**
- **Java**: 8
- **Risk score**: **100/100**
- **Migration Readiness Grade**: **C (Critical)**

## 📊 개요

이 프로젝트는 현재 Spring Boot **2.6.2**에서 **3.5**로 마이그레이션해야 합니다.
전체 위험도는 **100/100**이며, 위험 수준은 **높음**입니다. 대규모 마이그레이션이 필요합니다.

## 🎖️ Migration Readiness Grade

| Score Range | Grade | Description |
|---|---|---|
| 70-100 | 🔴 **C (Critical)** | 대규모 마이그레이션 필요 — Java 17+, Jakarta 전환, 테스트 재작성이 동시 필요 |
| 30-69 | 🟡 **C (Critical)** | 표준 마이그레이션 — javax→jakarta 전환과 주요 API 변경점 확인 필요 |
| 0-29 | 🟢 **C (Critical)** | 준비됨 — 작은 조정만 필요하거나 이미 근접 버전 |

## ⚠️ Top 3 Risks

### 1. Spring Boot 2.x → 3.x 대형 마이그레이션

- **Severity**: high
- **Detail**: 현재 2.6.2, 목표 3.5. Java 17 baseline과 Jakarta 전환이 필요합니다.

### 2. Java 17 baseline 미달

- **Severity**: high
- **Detail**: 현재 Java 8. Spring Boot 3.x는 Java 17 이상이 필요합니다.

### 3. JPA javax.persistence import 발견

- **Severity**: high
- **Detail**: 10개 이상의 JPA import가 Jakarta Persistence 전환 대상입니다.

## 🗺️ Estimated Roadmap

### Sprint 1: Java 17+ 빌드 환경 전환

- **Goal**: JDK 17/21로 빌드하고 런타임 호환성 확보
- **Tasks**: sourceCompatibility/targetCompatibility 변경, JDK toolchain 설정, 빌드 테스트 실행
- **Estimated Time**: 2 주

### Sprint 2: javax → jakarta namespace 전환

- **Goal**: 모든 javax.* import를 jakarta.*로 전환
- **Tasks**: 약 10개 파일 전환, Servlet/Validation/Persistence별 검증 테스트 실행
- **Estimated Time**: 2 주

### Sprint 3: Spring Security 6 스타일로 재작성

- **Goal**: WebSecurityConfigurerAdapter → SecurityFilterChain 전환
- **Tasks**: SecurityFilterChain @Bean 추가, antMatchers→requestMatchers 변경, authorizeRequests→authorizeHttpRequests
- **Estimated Time**: 1 주

### Sprint 4: JSP/JSTL Jakarta 호환성 전환

- **Goal**: Tomcat 10 jakarta.servlet 환경에서 JSP 렌더링 검증
- **Tasks**: jakarta.servlet.jsp.jstl 의존성 전환, taglib URI 확인, 뷰 회귀 테스트
- **Estimated Time**: 1 주

### Sprint 5: 종속성 major upgrade

- **Goal**: Hibernate 6, springdoc-openapi, QueryDSL jakarta 등 주요 의존성 전환
- **Tasks**: 의존성 좌표 변경, native query/dialect 검증, 테스트 실행
- **Estimated Time**: 2 주

### Sprint 6: Spring Boot 2.x → 3.x 마이그레이션

- **Goal**: Spring Boot 3.x로 버전 업그레이드 및 breaking change 대응
- **Tasks**: parent/plugin 버전 변경, auto-configuration 변경점 확인, 테스트 재실행
- **Estimated Time**: 1 주

**Total Estimated Duration**: 6 sprints (약 2 주 ... 1 주)

## 📋 Recommended Sprint Backlog

### Sprint 1: Java 17+ 빌드 환경 전환

- **Goal**: JDK 17/21로 빌드하고 런타임 호환성 확보
- **Tasks**: sourceCompatibility/targetCompatibility 변경, JDK toolchain 설정, 빌드 테스트 실행

### Sprint 2: javax → jakarta namespace 전환

- **Goal**: 모든 javax.* import를 jakarta.*로 전환
- **Tasks**: 약 10개 파일 전환, Servlet/Validation/Persistence별 검증 테스트 실행

### Sprint 3: Spring Security 6 스타일로 재작성

- **Goal**: WebSecurityConfigurerAdapter → SecurityFilterChain 전환
- **Tasks**: SecurityFilterChain @Bean 추가, antMatchers→requestMatchers 변경, authorizeRequests→authorizeHttpRequests

### Sprint 4: JSP/JSTL Jakarta 호환성 전환

- **Goal**: Tomcat 10 jakarta.servlet 환경에서 JSP 렌더링 검증
- **Tasks**: jakarta.servlet.jsp.jstl 의존성 전환, taglib URI 확인, 뷰 회귀 테스트

### Sprint 5: 종속성 major upgrade

- **Goal**: Hibernate 6, springdoc-openapi, QueryDSL jakarta 등 주요 의존성 전환
- **Tasks**: 의존성 좌표 변경, native query/dialect 검증, 테스트 실행

### Sprint 6: Spring Boot 2.x → 3.x 마이그레이션

- **Goal**: Spring Boot 3.x로 버전 업그레이드 및 breaking change 대응
- **Tasks**: parent/plugin 버전 변경, auto-configuration 변경점 확인, 테스트 재실행

# Spring Upgrade Radar

- **Project**: `/home/puredev/Documents/GitHub/SpringBoot_JPA_Blog_Prj`
- **Build tool**: maven
- **Spring Boot**: 2.6.2
- **Java**: 8
- **Target Spring Boot**: 3.5
- **Risk score**: 100/100

## Findings

### [HIGH] Spring Boot 2.x → 3.x 대형 마이그레이션

- **Rule**: `spring-boot-2-to-3`
- **Detail**: 현재 2.6.2, 목표 3.5. Java 17 baseline과 Jakarta 전환이 필요합니다.
- **Recommendation**: Java 17+ 전환, javax→jakarta import 정리, Spring Security/Hibernate 변경점을 먼저 분리하세요.
- **Evidence**:
  - `spring_boot_version=2.6.2`

### [HIGH] Java 17 baseline 미달

- **Rule**: `java-baseline`
- **Detail**: 현재 Java 8. Spring Boot 3.x는 Java 17 이상이 필요합니다.
- **Recommendation**: 먼저 JDK 17/21 빌드와 런타임 호환성을 확보하세요.
- **Evidence**:
  - `java_version=8`

### [HIGH] JPA javax.persistence import 발견

- **Rule**: `jakarta-persistence-imports`
- **Detail**: 10개 이상의 JPA import가 Jakarta Persistence 전환 대상입니다.
- **Recommendation**: javax.persistence.*를 jakarta.persistence.*로 전환하고 Hibernate 6/JPA 3 호환성을 엔티티/레포지토리 테스트로 검증하세요.
- **Evidence**:
  - `blog/src/main/java/com/pure/blog/model/User.java:5: import javax.persistence.Column;`
  - `blog/src/main/java/com/pure/blog/model/User.java:6: import javax.persistence.Entity;`
  - `blog/src/main/java/com/pure/blog/model/User.java:7: import javax.persistence.EnumType;`
  - `blog/src/main/java/com/pure/blog/model/User.java:8: import javax.persistence.Enumerated;`
  - `blog/src/main/java/com/pure/blog/model/User.java:9: import javax.persistence.GeneratedValue;`
  - `blog/src/main/java/com/pure/blog/model/User.java:10: import javax.persistence.GenerationType;`
  - `blog/src/main/java/com/pure/blog/model/User.java:11: import javax.persistence.Id;`
  - `blog/src/main/java/com/pure/blog/model/Reply.java:5: import javax.persistence.Column;`
  - `blog/src/main/java/com/pure/blog/model/Reply.java:6: import javax.persistence.Entity;`
  - `blog/src/main/java/com/pure/blog/model/Reply.java:7: import javax.persistence.GeneratedValue;`

### [HIGH] Spring Security 5 스타일 설정 발견

- **Rule**: `spring-security-legacy-config`
- **Detail**: WebSecurityConfigurerAdapter/authorizeRequests/antMatchers/EnableGlobalMethodSecurity는 Spring Security 6 전환 시 SecurityFilterChain/requestMatchers/EnableMethodSecurity 패턴으로 재작성해야 합니다.
- **Recommendation**: SecurityFilterChain @Bean 기반으로 재작성하고 antMatchers→requestMatchers, authorizeRequests→authorizeHttpRequests로 분리 마이그레이션하세요.
- **Evidence**:
  - `blog/src/main/java/com/pure/blog/config/SecurityConfig.java: WebSecurityConfigurerAdapter`
  - `blog/src/main/java/com/pure/blog/config/SecurityConfig.java: authorizeRequests()`
  - `blog/src/main/java/com/pure/blog/config/SecurityConfig.java: antMatchers(`
  - `blog/src/main/java/com/pure/blog/config/SecurityConfig.java: @EnableGlobalMethodSecurity`

### [MEDIUM] JSP view stack 발견

- **Rule**: `jsp-jstl-jakarta`
- **Detail**: JSP view stack은 Spring Boot 3/Tomcat 10의 jakarta.servlet 환경에서 taglib와 렌더링 호환성 점검이 필요합니다.
- **Recommendation**: JSP/JSTL 의존성을 Jakarta 호환 좌표로 전환하고 주요 view 렌더링 회귀 테스트를 추가하세요.
- **Evidence**:
  - `blog/src/main/webapp/WEB-INF/views/index.jsp`
  - `blog/src/main/webapp/WEB-INF/views/user/updateForm.jsp`
  - `blog/src/main/webapp/WEB-INF/views/user/loginForm.jsp`
  - `blog/src/main/webapp/WEB-INF/views/user/joinForm.jsp`
  - `blog/src/main/webapp/WEB-INF/views/board/updateForm.jsp`
  - `blog/src/main/webapp/WEB-INF/views/board/detail.jsp`
  - `blog/src/main/webapp/WEB-INF/views/board/writeForm.jsp`
  - `blog/src/main/webapp/WEB-INF/views/layout/footer.jsp`
  - `blog/src/main/webapp/WEB-INF/views/layout/header.jsp`
  - `blog/src/main/resources/application.yml: spring.mvc.view JSP configuration`

### [LOW] MySQL Connector/J 좌표 변경 점검

- **Rule**: `mysql-connector-coordinates`
- **Detail**: 구형 mysql:mysql-connector-java 좌표를 사용 중입니다. 최신 Connector/J는 com.mysql:mysql-connector-j 좌표를 사용합니다.
- **Recommendation**: com.mysql:mysql-connector-j로 전환하고 드라이버 클래스 자동 감지를 확인하세요.
- **Evidence**:
  - `mysql:mysql-connector-java`

### [LOW] Maven Wrapper 실행 권한 누락

- **Rule**: `maven-wrapper-executable`
- **Detail**: CI나 로컬 검증에서 ./mvnw test가 권한 문제로 실패할 수 있습니다.
- **Recommendation**: chmod +x blog/mvnw를 실행하고 wrapper 기반 검증 명령을 CI에 사용하세요.
- **Evidence**:
  - `blog/mvnw is not executable`

## Migration tickets

### Ticket 1: Spring Boot 2.x → 3.x 대형 마이그레이션

- **Rule**: `spring-boot-2-to-3`
- **Why**: 현재 2.6.2, 목표 3.5. Java 17 baseline과 Jakarta 전환이 필요합니다.
- **Affected files/evidence**:
  - `spring_boot_version=2.6.2`
- **Suggested change**: Java 17+ 전환, javax→jakarta import 정리, Spring Security/Hibernate 변경점을 먼저 분리하세요.
- **Validation command**: `cd blog && ./mvnw test`
- **Rough effort**: L

### Ticket 2: Java 17 baseline 미달

- **Rule**: `java-baseline`
- **Why**: 현재 Java 8. Spring Boot 3.x는 Java 17 이상이 필요합니다.
- **Affected files/evidence**:
  - `java_version=8`
- **Suggested change**: 먼저 JDK 17/21 빌드와 런타임 호환성을 확보하세요.
- **Validation command**: `cd blog && ./mvnw test`
- **Rough effort**: L

### Ticket 3: JPA javax.persistence import 발견

- **Rule**: `jakarta-persistence-imports`
- **Why**: 10개 이상의 JPA import가 Jakarta Persistence 전환 대상입니다.
- **Affected files/evidence**:
  - `blog/src/main/java/com/pure/blog/model/User.java:5: import javax.persistence.Column;`
  - `blog/src/main/java/com/pure/blog/model/User.java:6: import javax.persistence.Entity;`
  - `blog/src/main/java/com/pure/blog/model/User.java:7: import javax.persistence.EnumType;`
  - `blog/src/main/java/com/pure/blog/model/User.java:8: import javax.persistence.Enumerated;`
  - `blog/src/main/java/com/pure/blog/model/User.java:9: import javax.persistence.GeneratedValue;`
  - `blog/src/main/java/com/pure/blog/model/User.java:10: import javax.persistence.GenerationType;`
  - `blog/src/main/java/com/pure/blog/model/User.java:11: import javax.persistence.Id;`
  - `blog/src/main/java/com/pure/blog/model/Reply.java:5: import javax.persistence.Column;`
  - `blog/src/main/java/com/pure/blog/model/Reply.java:6: import javax.persistence.Entity;`
  - `blog/src/main/java/com/pure/blog/model/Reply.java:7: import javax.persistence.GeneratedValue;`
- **Suggested change**: javax.persistence.*를 jakarta.persistence.*로 전환하고 Hibernate 6/JPA 3 호환성을 엔티티/레포지토리 테스트로 검증하세요.
- **Validation command**: `cd blog && ./mvnw test`
- **Rough effort**: L

### Ticket 4: Spring Security 5 스타일 설정 발견

- **Rule**: `spring-security-legacy-config`
- **Why**: WebSecurityConfigurerAdapter/authorizeRequests/antMatchers/EnableGlobalMethodSecurity는 Spring Security 6 전환 시 SecurityFilterChain/requestMatchers/EnableMethodSecurity 패턴으로 재작성해야 합니다.
- **Affected files/evidence**:
  - `blog/src/main/java/com/pure/blog/config/SecurityConfig.java: WebSecurityConfigurerAdapter`
  - `blog/src/main/java/com/pure/blog/config/SecurityConfig.java: authorizeRequests()`
  - `blog/src/main/java/com/pure/blog/config/SecurityConfig.java: antMatchers(`
  - `blog/src/main/java/com/pure/blog/config/SecurityConfig.java: @EnableGlobalMethodSecurity`
- **Suggested change**: SecurityFilterChain @Bean 기반으로 재작성하고 antMatchers→requestMatchers, authorizeRequests→authorizeHttpRequests로 분리 마이그레이션하세요.
- **Validation command**: `cd blog && ./mvnw test`
- **Rough effort**: L

### Ticket 5: JSP view stack 발견

- **Rule**: `jsp-jstl-jakarta`
- **Why**: JSP view stack은 Spring Boot 3/Tomcat 10의 jakarta.servlet 환경에서 taglib와 렌더링 호환성 점검이 필요합니다.
- **Affected files/evidence**:
  - `blog/src/main/webapp/WEB-INF/views/index.jsp`
  - `blog/src/main/webapp/WEB-INF/views/user/updateForm.jsp`
  - `blog/src/main/webapp/WEB-INF/views/user/loginForm.jsp`
  - `blog/src/main/webapp/WEB-INF/views/user/joinForm.jsp`
  - `blog/src/main/webapp/WEB-INF/views/board/updateForm.jsp`
  - `blog/src/main/webapp/WEB-INF/views/board/detail.jsp`
  - `blog/src/main/webapp/WEB-INF/views/board/writeForm.jsp`
  - `blog/src/main/webapp/WEB-INF/views/layout/footer.jsp`
  - `blog/src/main/webapp/WEB-INF/views/layout/header.jsp`
  - `blog/src/main/resources/application.yml: spring.mvc.view JSP configuration`
- **Suggested change**: JSP/JSTL 의존성을 Jakarta 호환 좌표로 전환하고 주요 view 렌더링 회귀 테스트를 추가하세요.
- **Validation command**: `cd blog && ./mvnw test`
- **Rough effort**: M

### Ticket 6: MySQL Connector/J 좌표 변경 점검

- **Rule**: `mysql-connector-coordinates`
- **Why**: 구형 mysql:mysql-connector-java 좌표를 사용 중입니다. 최신 Connector/J는 com.mysql:mysql-connector-j 좌표를 사용합니다.
- **Affected files/evidence**:
  - `mysql:mysql-connector-java`
- **Suggested change**: com.mysql:mysql-connector-j로 전환하고 드라이버 클래스 자동 감지를 확인하세요.
- **Validation command**: `cd blog && ./mvnw test`
- **Rough effort**: S

### Ticket 7: Maven Wrapper 실행 권한 누락

- **Rule**: `maven-wrapper-executable`
- **Why**: CI나 로컬 검증에서 ./mvnw test가 권한 문제로 실패할 수 있습니다.
- **Affected files/evidence**:
  - `blog/mvnw is not executable`
- **Suggested change**: chmod +x blog/mvnw를 실행하고 wrapper 기반 검증 명령을 CI에 사용하세요.
- **Validation command**: `cd blog && ./mvnw test`
- **Rough effort**: S

## Next actions

1. High severity 항목부터 별도 브랜치/티켓으로 분리한다.
2. Java 17/21 toolchain 빌드를 먼저 통과시킨다.
3. javax→jakarta 전환과 dependency major upgrade를 한 PR에 섞지 않는다.
4. 테스트 실패가 많은 모듈부터 OpenRewrite 또는 수동 migration spike를 수행한다.

---

## Need a full migration plan?

This report is a first-pass migration radar. For team planning, turn it into a full Spring Boot 3 migration assessment:

- **Pro report**: PDF, dependency matrix, and sprint-by-sprint plan
- **Team workflow**: Jira/GitHub issue export and CI integration
- **Spring Boot 3 migration assessment**: prioritized backlog and upgrade strategy
