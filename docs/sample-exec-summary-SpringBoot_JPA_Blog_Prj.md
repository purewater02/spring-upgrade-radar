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
| 30-69 | 🟡 **B (Ready)** | 표준 마이그레이션 — javax→jakarta 전환과 주요 API 변경점 확인 필요 |
| 0-29 | 🟢 **A (Excellent)** | 준비됨 — 작은 조정만 필요하거나 이미 근접 버전 |

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
