#!/usr/bin/env python3
"""
테스트 폴더 구조 최적화 스크립트
"""

import os
import shutil
from pathlib import Path
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestStructureOptimizer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backend_root = self.project_root / "backend"
        self.new_test_root = self.backend_root / "tests"
        
    def optimize_structure(self):
        """테스트 구조 최적화 실행"""
        logger.info("🚀 테스트 구조 최적화 시작")
        
        # 1. 새로운 테스트 구조 생성
        self._create_new_structure()
        
        # 2. 에이전트 테스트 파일 이동
        self._migrate_agent_tests()
        
        # 3. 중복 파일 정리
        self._cleanup_duplicates()
        
        # 4. 빈 폴더 제거
        self._remove_empty_dirs()
        
        logger.info("✅ 테스트 구조 최적화 완료")
    
    def _create_new_structure(self):
        """새로운 테스트 디렉토리 구조 생성"""
        logger.info("📁 새로운 테스트 구조 생성")
        
        # 기본 구조 생성
        test_dirs = [
            "unit/agents/nl_input",
            "unit/agents/parser", 
            "unit/agents/ui_selection",
            "unit/agents/component_decision",
            "unit/agents/match_rate",
            "unit/agents/search",
            "unit/agents/generation", 
            "unit/agents/assembly",
            "unit/agents/download",
            "unit/framework",
            "unit/utils",
            "integration/agents",
            "integration/api", 
            "integration/database",
            "e2e",
            "fixtures",
            "helpers",
            "config"
        ]
        
        for dir_path in test_dirs:
            full_path = self.new_test_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            
            # __init__.py 파일 생성
            init_file = full_path / "__init__.py"
            if not init_file.exists():
                init_file.write_text("")
    
    def _migrate_agent_tests(self):
        """에이전트 테스트 파일 마이그레이션"""
        logger.info("🔄 에이전트 테스트 파일 마이그레이션")
        
        agents = [
            "nl_input", "parser", "ui_selection", "component_decision",
            "match_rate", "search", "generation", "assembly", "download"
        ]
        
        for agent in agents:
            self._migrate_single_agent_tests(agent)
    
    def _migrate_single_agent_tests(self, agent_name: str):
        """단일 에이전트 테스트 마이그레이션"""
        logger.info(f"📦 {agent_name} 에이전트 테스트 마이그레이션")
        
        # 소스 경로들
        source_paths = [
            self.backend_root / f"src/agents/implementations/{agent_name}/tests",
            self.backend_root / f"src/agents/implementations/{agent_name}",
            self.backend_root / f"tests/agents/{agent_name}",
            self.backend_root / "tests/agents"
        ]
        
        # 대상 경로
        target_path = self.new_test_root / f"unit/agents/{agent_name}"
        
        # 테스트 파일 수집 및 이동
        test_files = []
        
        for source_path in source_paths:
            if source_path.exists():
                # test_*.py 파일 찾기
                for test_file in source_path.glob("test_*.py"):
                    if test_file.name not in [f.name for f in test_files]:
                        test_files.append(test_file)
                
                # tests 폴더 내 파일들
                if source_path.name == "tests":
                    for test_file in source_path.glob("*.py"):
                        if test_file.name not in [f.name for f in test_files]:
                            test_files.append(test_file)
        
        # 파일 이동
        for test_file in test_files:
            target_file = target_path / test_file.name
            if not target_file.exists():
                shutil.copy2(test_file, target_file)
                logger.info(f"  ✅ {test_file.name} -> {target_file}")
    
    def _cleanup_duplicates(self):
        """중복 파일 정리"""
        logger.info("🧹 중복 파일 정리")
        
        # 에이전트 구현 폴더 내 테스트 파일 제거
        impl_path = self.backend_root / "src/agents/implementations"
        
        for agent_dir in impl_path.iterdir():
            if agent_dir.is_dir() and agent_dir.name != "__pycache__":
                # test_*.py 파일 제거
                for test_file in agent_dir.glob("test_*.py"):
                    test_file.unlink()
                    logger.info(f"  🗑️  제거: {test_file}")
                
                # tests 폴더 제거
                tests_dir = agent_dir / "tests"
                if tests_dir.exists():
                    shutil.rmtree(tests_dir)
                    logger.info(f"  🗑️  제거: {tests_dir}")
        
        # 기존 backend/tests/agents 폴더 정리
        old_agents_tests = self.backend_root / "tests/agents"
        if old_agents_tests.exists():
            # 개별 테스트 파일들만 제거 (이미 마이그레이션됨)
            for test_file in old_agents_tests.glob("test_*.py"):
                test_file.unlink()
                logger.info(f"  🗑️  제거: {test_file}")
    
    def _remove_empty_dirs(self):
        """빈 디렉토리 제거"""
        logger.info("📂 빈 디렉토리 정리")
        
        def is_empty_dir(path: Path) -> bool:
            if not path.is_dir():
                return False
            
            try:
                # __pycache__ 제외하고 확인
                contents = [p for p in path.iterdir() if p.name != "__pycache__"]
                return len(contents) == 0
            except:
                return False
        
        # 에이전트 구현 폴더 내 빈 tests 폴더 제거
        impl_path = self.backend_root / "src/agents/implementations"
        
        for agent_dir in impl_path.iterdir():
            if agent_dir.is_dir():
                tests_dir = agent_dir / "tests"
                if tests_dir.exists() and is_empty_dir(tests_dir):
                    tests_dir.rmdir()
                    logger.info(f"  🗑️  빈 폴더 제거: {tests_dir}")

def main():
    """메인 실행 함수"""
    project_root = "/home/ec2-user/T-DeveloperMVP"
    
    optimizer = TestStructureOptimizer(project_root)
    optimizer.optimize_structure()
    
    print("\n" + "="*60)
    print("🎉 테스트 구조 최적화 완료!")
    print("="*60)
    print("\n새로운 테스트 구조:")
    print("backend/tests/")
    print("├── unit/agents/        # 에이전트 단위 테스트")
    print("├── integration/        # 통합 테스트") 
    print("├── e2e/               # E2E 테스트")
    print("├── fixtures/          # 테스트 데이터")
    print("├── helpers/           # 테스트 헬퍼")
    print("└── config/            # 테스트 설정")
    print("\n다음 단계:")
    print("1. 테스트 실행 확인: cd backend && python -m pytest tests/")
    print("2. 테스트 설정 업데이트 필요시 수정")

if __name__ == "__main__":
    main()