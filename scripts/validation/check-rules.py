#!/usr/bin/env python3
"""
CLAUDE.md 규칙 자동 체크 스크립트
모든 명령 실행 후 자동으로 규칙 준수 여부를 확인합니다.
"""

import os
import sys
import subprocess
import re
from pathlib import Path
from typing import List, Dict, Tuple

class RuleChecker:
    def __init__(self):
        self.project_root = Path("/home/ec2-user/T-DeveloperMVP")
        self.violations = []
        self.warnings = []
        self.successes = []
        
    def check_no_mock_implementations(self) -> None:
        """Mock 구현이 없는지 확인"""
        mock_patterns = [
            (r"mock[A-Z]\w*", "Mock 변수/함수"),
            (r"return\s+.*mockData", "Mock 데이터 반환"),
            (r"// TODO: implement", "미구현 TODO"),
            (r"console\.log\(['\"]Not implemented", "미구현 로그"),
            (r"placeholder", "Placeholder 코드"),
        ]
        
        extensions = ['.ts', '.tsx', '.js', '.jsx', '.py']
        
        for pattern, description in mock_patterns:
            files = self._search_pattern(pattern, extensions)
            if files:
                self.violations.append(f"❌ {description} 발견: {len(files)}개 파일")
                for f in files[:3]:  # 처음 3개만 표시
                    self.violations.append(f"   - {f}")
                    
    def check_production_ready(self) -> None:
        """프로덕션 준비 상태 확인"""
        # Error handling 체크
        try_catch_count = self._count_pattern(r"try\s*{", ['.ts', '.tsx', '.js'])
        error_handling_count = self._count_pattern(r"catch\s*\(", ['.ts', '.tsx', '.js'])
        
        if try_catch_count < 10:
            self.warnings.append("⚠️  Error handling 부족 (try-catch 블록이 10개 미만)")
            
        # Logging 체크
        logger_count = self._count_pattern(r"logger\.", ['.py', '.ts', '.tsx'])
        if logger_count < 5:
            self.warnings.append("⚠️  로깅 부족 (logger 사용이 5회 미만)")
            
        # Validation 체크
        validation_count = self._count_pattern(r"(validate|Validator|validation)", ['.py', '.ts', '.tsx'])
        if validation_count > 0:
            self.successes.append("✅ Input validation 구현됨")
            
    def check_git_commit_rules(self) -> None:
        """Git 커밋 규칙 확인"""
        try:
            # 최근 커밋 확인
            result = subprocess.run(
                ["git", "log", "-1", "--pretty=format:%s"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            last_commit = result.stdout.strip()
            
            # Conventional Commits 형식 체크
            if re.match(r"^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+", last_commit):
                self.successes.append(f"✅ 올바른 커밋 메시지 형식: {last_commit[:50]}")
            else:
                self.warnings.append(f"⚠️  커밋 메시지 형식 확인 필요: {last_commit[:50]}")
                
            # Uncommitted changes 체크
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                uncommitted_count = len(result.stdout.strip().split('\n'))
                self.warnings.append(f"⚠️  커밋되지 않은 변경사항: {uncommitted_count}개 파일")
                self.warnings.append("💡 규칙: 단위 작업 완료 시 즉시 커밋 & 푸시")
                
        except Exception as e:
            pass
            
    def check_language_rules(self) -> None:
        """언어 사용 규칙 확인"""
        # Python 우선 규칙 체크
        py_agents = len(list(Path(self.project_root / "backend/src/agents/implementations").glob("*.py")))
        ts_agents = len(list(Path(self.project_root / "backend/src/agents").glob("*.ts")))
        
        if py_agents > 0:
            self.successes.append(f"✅ Python Agent 구현: {py_agents}개")
        if ts_agents > py_agents:
            self.warnings.append(f"⚠️  TypeScript Agent가 Python보다 많음 (TS: {ts_agents}, PY: {py_agents})")
            
    def check_forbidden_practices(self) -> None:
        """금지된 관행 체크"""
        forbidden = [
            (r"return\s+mockData", "mockData 반환"),
            (r"// TODO: implement later", "나중에 구현 TODO"),
            (r'console\.log\("Not implemented"\)', "미구현 로그"),
            (r"<any>", "TypeScript any 타입"),
            (r"catch\s*\(\s*\)\s*{\s*}", "빈 catch 블록"),
        ]
        
        for pattern, description in forbidden:
            files = self._search_pattern(pattern, ['.ts', '.tsx', '.js', '.jsx'])
            if files:
                self.violations.append(f"❌ 금지된 관행: {description} ({len(files)}개 파일)")
                
    def _search_pattern(self, pattern: str, extensions: List[str]) -> List[str]:
        """패턴 검색"""
        files = []
        for ext in extensions:
            for file_path in self.project_root.rglob(f"*{ext}"):
                if 'node_modules' in str(file_path) or '.git' in str(file_path):
                    continue
                    
                # 테스트 파일에서 jest.mock 사용은 허용
                if ('test' in str(file_path) or 'spec' in str(file_path)) and 'mock' in pattern.lower():
                    if ext in ['.ts', '.tsx', '.js', '.jsx']:
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                # jest.mock, mockClient 등 테스트 도구는 허용
                                if 'jest.mock' in content or 'mockClient' in content:
                                    continue
                        except:
                            pass
                            
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if re.search(pattern, content, re.IGNORECASE):
                            files.append(str(file_path.relative_to(self.project_root)))
                except:
                    pass
        return files
        
    def _count_pattern(self, pattern: str, extensions: List[str]) -> int:
        """패턴 카운트"""
        count = 0
        for ext in extensions:
            for file_path in self.project_root.rglob(f"*{ext}"):
                if 'node_modules' in str(file_path) or '.git' in str(file_path):
                    continue
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        count += len(re.findall(pattern, content, re.IGNORECASE))
                except:
                    pass
        return count
        
    def run_all_checks(self) -> None:
        """모든 체크 실행"""
        print("\n" + "="*60)
        print("🔍 CLAUDE.md 규칙 자동 체크")
        print("="*60)
        
        self.check_no_mock_implementations()
        self.check_production_ready()
        self.check_git_commit_rules()
        self.check_language_rules()
        self.check_forbidden_practices()
        
        # 결과 출력
        if self.violations:
            print("\n❌ 규칙 위반:")
            for v in self.violations:
                print(f"  {v}")
                
        if self.warnings:
            print("\n⚠️  경고:")
            for w in self.warnings:
                print(f"  {w}")
                
        if self.successes:
            print("\n✅ 준수 사항:")
            for s in self.successes:
                print(f"  {s}")
                
        if not self.violations and not self.warnings:
            print("\n🎉 모든 규칙을 준수하고 있습니다!")
            
        print("\n" + "="*60)
        
        # 위반 사항이 있으면 exit code 1
        if self.violations:
            sys.exit(1)

if __name__ == "__main__":
    checker = RuleChecker()
    checker.run_all_checks()