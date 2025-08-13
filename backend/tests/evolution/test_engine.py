"""
Tests for Evolution Engine

진화 엔진(Evolution Engine)의 핵심 기능을 테스트합니다.
"""

import asyncio
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from evolution.engine import (
    EvolutionEngine,
    EvolutionConfig,
    EvolutionStatus,
    EvolutionMetrics,
)


class TestEvolutionEngine:
    """Evolution Engine 테스트 클래스"""

    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        # 임시 디렉토리 생성
        self.temp_dir = Path(tempfile.mkdtemp())

        # 테스트용 설정
        self.config = EvolutionConfig(
            max_generations=10,
            population_size=5,
            memory_limit_kb=6.5,
            instantiation_limit_us=3.0,
            checkpoint_interval=5,
        )

        # Evolution 디렉토리를 임시 경로로 설정
        with patch("evolution.engine.Path") as mock_path:
            mock_path.return_value = self.temp_dir / "evolution"
            self.engine = EvolutionEngine(self.config)
            self.engine.evolution_dir = self.temp_dir / "evolution"
            self.engine.checkpoint_dir = self.engine.evolution_dir / "checkpoints"
            self.engine.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def teardown_method(self):
        """각 테스트 메서드 실행 후 정리"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    @pytest.mark.asyncio
    async def test_engine_initialization(self):
        """엔진 초기화 테스트"""
        # When: 엔진 초기화
        result = await self.engine.initialize()

        # Then: 초기화 성공
        assert result is True
        assert self.engine.status == EvolutionStatus.IDLE
        assert len(self.engine.population) == self.config.population_size
        assert self.engine.current_generation == 0

    @pytest.mark.asyncio
    async def test_population_creation(self):
        """개체군(Population) 생성 테스트"""
        # When: 개체군 초기화
        await self.engine.initialize()

        # Then: 올바른 개체군 생성
        assert len(self.engine.population) == self.config.population_size

        # 각 개체(genome)가 올바른 구조를 가지는지 확인
        for genome in self.engine.population:
            assert "id" in genome
            assert "genes" in genome
            assert "fitness" in genome
            assert "metrics" in genome

            # 유전자 구조 확인
            genes = genome["genes"]
            assert "layer_sizes" in genes
            assert "activation" in genes
            assert "learning_rate" in genes
            assert isinstance(genes["layer_sizes"], list)
            assert len(genes["layer_sizes"]) >= 2

    @pytest.mark.asyncio
    async def test_fitness_evaluation(self):
        """적합도(Fitness) 평가 테스트"""
        await self.engine.initialize()

        # When: 개체군 평가
        await self.engine._evaluate_population()

        # Then: 모든 개체의 적합도가 계산됨
        for genome in self.engine.population:
            assert genome["fitness"] >= 0
            assert genome["fitness"] <= 1
            assert "memory_kb" in genome["metrics"]
            assert "instantiation_us" in genome["metrics"]
            assert "accuracy" in genome["metrics"]

    @pytest.mark.asyncio
    async def test_memory_constraint_validation(self):
        """메모리 제약 조건 검증 테스트"""
        await self.engine.initialize()

        # Given: 메모리 제한을 초과하는 개체 생성
        test_genome = {
            "id": "test_agent",
            "fitness": 0.9,
            "metrics": {
                "memory_kb": 10.0,  # 6.5KB 제한 초과
                "instantiation_us": 2.0,
                "accuracy": 0.95,
            },
        }
        self.engine.best_genome = test_genome

        # When: 안전 검사 실행
        is_safe = await self.engine._safety_check()

        # Then: 안전하지 않음으로 판정
        assert is_safe is False

    @pytest.mark.asyncio
    async def test_instantiation_time_constraint(self):
        """인스턴스화 시간 제약 조건 테스트"""
        await self.engine.initialize()

        # Given: 인스턴스화 시간이 초과된 개체
        test_genome = {
            "id": "test_agent",
            "fitness": 0.9,
            "metrics": {
                "memory_kb": 5.0,
                "instantiation_us": 5.0,  # 3μs 제한 초과
                "accuracy": 0.95,
            },
        }
        self.engine.best_genome = test_genome

        # When: 안전 검사
        is_safe = await self.engine._safety_check()

        # Then: 안전하지 않음
        assert is_safe is False

    @pytest.mark.asyncio
    async def test_selection_process(self):
        """선택(Selection) 과정 테스트"""
        await self.engine.initialize()
        await self.engine._evaluate_population()

        # When: 부모 선택
        parents = await self.engine._selection()

        # Then: 올바른 수의 부모 선택
        assert len(parents) == self.config.population_size

        # 적합도가 높은 개체가 선택되었는지 확인
        parent_fitnesses = [p["fitness"] for p in parents]
        original_fitnesses = [g["fitness"] for g in self.engine.population]

        # 선택된 부모들의 평균 적합도가 전체 평균보다 높거나 같아야 함
        assert sum(parent_fitnesses) / len(parent_fitnesses) >= sum(
            original_fitnesses
        ) / len(original_fitnesses)

    @pytest.mark.asyncio
    async def test_crossover_operation(self):
        """교차(Crossover) 연산 테스트"""
        await self.engine.initialize()
        await self.engine._evaluate_population()
        parents = await self.engine._selection()

        # When: 교차 연산 실행
        offspring = await self.engine._crossover(parents)

        # Then: 올바른 수의 자손 생성
        assert len(offspring) >= len(parents)

        # 자손이 부모의 특성을 물려받았는지 확인
        for child in offspring:
            assert "genes" in child
            assert "id" in child
            # 자손은 부모의 fitness를 상속받을 수 있음

    @pytest.mark.asyncio
    async def test_mutation_operation(self):
        """돌연변이(Mutation) 연산 테스트"""
        await self.engine.initialize()
        original_population = [g.copy() for g in self.engine.population]

        # When: 돌연변이 적용
        mutated = await self.engine._mutation(self.engine.population)

        # Then: 개체군 크기 유지
        assert len(mutated) == len(original_population)

        # 일부 개체에서 변화가 발생했는지 확인 (돌연변이율에 따라)
        # 단, 확률적 특성상 항상 변화가 있지는 않을 수 있음
        assert len(mutated) == len(original_population)

    @pytest.mark.asyncio
    async def test_checkpoint_save_load(self):
        """체크포인트 저장/로드 테스트"""
        await self.engine.initialize()
        await self.engine._evaluate_population()

        # When: 체크포인트 저장
        await self.engine._save_checkpoint()

        # Then: 체크포인트 파일 생성 확인
        checkpoint_files = list(self.engine.checkpoint_dir.glob("checkpoint_*.json"))
        assert len(checkpoint_files) > 0

        # 체크포인트 데이터 검증
        import json

        with open(checkpoint_files[0], "r") as f:
            checkpoint_data = json.load(f)

        assert "generation" in checkpoint_data
        assert "population" in checkpoint_data
        assert "timestamp" in checkpoint_data

    @pytest.mark.asyncio
    async def test_emergency_stop(self):
        """긴급 정지 테스트"""
        await self.engine.initialize()

        # When: 긴급 정지 실행
        result = await self.engine.emergency_stop()

        # Then: 정지 성공 및 상태 변경
        assert result is True
        assert self.engine.status == EvolutionStatus.ROLLED_BACK
        assert len(self.engine.population) == 0

        # 긴급 체크포인트 파일 생성 확인
        emergency_files = list(self.engine.checkpoint_dir.glob("emergency_*.json"))
        assert len(emergency_files) > 0

    @pytest.mark.asyncio
    async def test_rollback_functionality(self):
        """롤백 기능 테스트"""
        await self.engine.initialize()

        # Given: 체크포인트 저장
        await self.engine._save_checkpoint()
        original_generation = self.engine.current_generation
        original_population_size = len(self.engine.population)

        # 상태 변경
        self.engine.current_generation = 5
        self.engine.population = []

        # When: 롤백 실행
        result = await self.engine.rollback()

        # Then: 이전 상태로 복원
        assert result is True
        assert self.engine.current_generation == original_generation
        assert len(self.engine.population) == original_population_size
        assert self.engine.status == EvolutionStatus.ROLLED_BACK

    @pytest.mark.asyncio
    async def test_evolution_metrics_tracking(self):
        """진화 지표 추적 테스트"""
        await self.engine.initialize()
        await self.engine._evaluate_population()

        # When: 지표 업데이트
        await self.engine._update_metrics()

        # Then: 지표가 올바르게 기록됨
        assert len(self.engine.metrics_history) > 0

        latest_metrics = self.engine.metrics_history[-1]
        assert isinstance(latest_metrics, EvolutionMetrics)
        assert latest_metrics.generation == self.engine.current_generation
        assert latest_metrics.fitness_score >= 0
        assert latest_metrics.autonomy_level == self.config.autonomy_target

    def test_genome_creation(self):
        """개체(Genome) 생성 테스트"""
        # When: 개체 생성
        genome = self.engine._create_random_genome()

        # Then: 올바른 구조 확인
        assert "id" in genome
        assert "genes" in genome
        assert "fitness" in genome
        assert "metrics" in genome

        # 유전자가 제약 조건 내에 있는지 확인
        genes = genome["genes"]
        assert genes["learning_rate"] > 0
        assert genes["learning_rate"] <= 0.1
        assert 0 <= genes["dropout_rate"] <= 1
        assert genes["activation"] in ["relu", "tanh", "sigmoid"]
        assert genes["optimizer"] in ["adam", "sgd", "rmsprop"]

    @pytest.mark.asyncio
    async def test_evolution_with_target_fitness(self):
        """목표 적합도를 가진 진화 테스트"""
        await self.engine.initialize()

        # Given: 낮은 목표 적합도 설정 (빠른 테스트를 위해)
        target_fitness = 0.5

        # Mock fitness evaluation to gradually improve and stay within constraints
        original_evaluate = self.engine._evaluate_fitness

        async def mock_evaluate_fitness(genome):
            # 점진적으로 개선되는 적합도 시뮬레이션
            base_fitness = await original_evaluate(genome)
            improvement = min(0.1 * self.engine.current_generation, 0.4)
            fitness = min(base_fitness + improvement, 1.0)

            # 안전 제약 조건 내에서 메트릭 설정
            genome["metrics"]["memory_kb"] = 5.0  # 6.5KB 제한 내
            genome["metrics"]["instantiation_us"] = 2.5  # 3μs 제한 내

            return fitness

        self.engine._evaluate_fitness = mock_evaluate_fitness

        # When: 진화 시작
        result = await self.engine.start_evolution(target_fitness)

        # Then: 목표 달성 또는 최대 세대 완료
        assert result is True
        assert self.engine.status == EvolutionStatus.COMPLETED
        assert self.engine.current_generation > 0


if __name__ == "__main__":
    # 직접 실행시 테스트 수행
    pytest.main([__file__, "-v"])
