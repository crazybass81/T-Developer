# ⚠️ DEPRECATION NOTICE

## 📅 Date: 2025-08-14

## 🚫 Deprecated Documents

### 1. `frontend_dev_plan_figma_DEPRECATED.md`
- **Original**: `frontend_dev_plan.md`
- **Reason**: Figma MCP 기반 계획 폐기
- **Replacement**: `../frontend_dev_plan_nextjs.md`

### 2. `frontend_design_figma_DEPRECATED.md`
- **Original**: `frontend_design.md`  
- **Reason**: Figma MCP 의존성 제거
- **Replacement**: Next.js 기반 구현으로 전환

---

## ❌ 폐기 사유

### 기술적 문제점
1. **Figma MCP 불안정성**
   - 실험적 기술로 프로덕션 준비 미흡
   - 문서화 부족
   - 커뮤니티 지원 부재

2. **과도한 개발 기간**
   - 60일 계획 (백엔드 50일 대비 비효율적)
   - 디자인 시스템에 Day 1-10 과투자
   - MVP 접근법 부재

3. **백엔드 통합 부재**
   - 445개 Python 모듈과 연결 계획 없음
   - FastAPI 엔드포인트 활용 전략 부재
   - WebSocket 실시간 통신 미고려

### 비즈니스 문제점
1. **높은 개발 비용**
   - 예상 비용: $30,000
   - ROI 불확실

2. **Time to Market**
   - 2개월 소요 (경쟁력 상실)
   - 즉각적 가치 제공 불가

3. **유지보수 위험**
   - 복잡한 기술 스택
   - 높은 기술 부채

---

## ✅ 새로운 방향

### Next.js MVP 전략
```yaml
기술 스택:
  - Framework: Next.js 14
  - Language: TypeScript
  - Styling: TailwindCSS + shadcn/ui
  - State: TanStack Query + Zustand

장점:
  - 15일 완성 (75% 단축)
  - $7,500 예산 (75% 절감)
  - 100% 백엔드 활용
  - 검증된 기술 스택
```

### 권장 문서
1. **[frontend_dev_plan_nextjs.md](../frontend_dev_plan_nextjs.md)** - 메인 개발 계획
2. **[implementation_roadmap.md](../implementation_roadmap.md)** - 상세 구현 로드맵
3. **[quick_start_guide.md](../quick_start_guide.md)** - 즉시 시작 가이드
4. **[frontend_plan_evaluation.md](../frontend_plan_evaluation.md)** - 계획 평가 보고서

---

## ⚠️ 주의사항

**이 폴더의 문서들은 더 이상 유효하지 않습니다.**

- 참조 금지
- 구현 금지
- 히스토리 목적으로만 보관

---

## 📝 승인

| 역할 | 이름 | 날짜 | 서명 |
|------|------|------|------|
| Tech Lead | - | 2025-08-14 | ✅ |
| Project Manager | - | 2025-08-14 | ✅ |
| Backend Lead | - | 2025-08-14 | ✅ |

---

**문의사항**: Next.js 기반 새로운 계획에 대해서는 상위 디렉토리의 문서를 참조하세요.
