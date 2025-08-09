# T-Developer Makefile with CLAUDE.md rule checking

.PHONY: help check-rules dev build test deploy commit

help:
	@echo "사용 가능한 명령:"
	@echo "  make check-rules  - CLAUDE.md 규칙 체크"
	@echo "  make dev         - 개발 서버 시작 (규칙 체크 포함)"
	@echo "  make build       - 프로젝트 빌드 (규칙 체크 포함)"
	@echo "  make test        - 테스트 실행 (규칙 체크 포함)"
	@echo "  make commit      - Git 커밋 (규칙 체크 포함)"

check-rules:
	@echo "🔍 CLAUDE.md 규칙 체크 중..."
	@python3 check-rules.py

dev: check-rules
	@echo "🚀 개발 서버 시작..."
	cd backend && python3 -m uvicorn src.main_api:app --reload &
	cd frontend && npm run dev

build: check-rules
	@echo "🏗️  프로젝트 빌드 중..."
	cd frontend && npm run build
	cd backend && python3 -m compileall src/

test: check-rules
	@echo "🧪 테스트 실행 중..."
	cd backend && python3 -m pytest tests/ -v
	cd frontend && npm test

commit: check-rules
	@echo "📝 Git 커밋 중..."
	git add -A
	@read -p "커밋 메시지 (feat/fix/docs/...): " msg; \
	git commit -m "$$msg"
	git push

# 모든 명령 실행 시 자동으로 규칙 체크
%: check-rules
	@$(MAKE) $@