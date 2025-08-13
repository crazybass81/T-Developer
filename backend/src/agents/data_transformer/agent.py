"""
Data Transformer Agent
데이터 형식 불일치를 자동으로 감지하고 변환하는 스마트 에이전트
"""

import json
import asyncio
from typing import Any, Dict, Optional, Union, List
from dataclasses import dataclass, asdict, is_dataclass
import inspect
from datetime import datetime


@dataclass
class TransformationResult:
    """변환 결과"""

    success: bool
    transformed_data: Any
    original_format: str
    target_format: str
    transformation_log: List[str]
    error: Optional[str] = None


class DataTransformerAgent:
    """
    데이터 형식을 자동으로 감지하고 변환하는 에이전트
    에이전트 간 데이터 전달 시 형식 불일치를 해결
    """

    def __init__(self):
        self.name = "DataTransformer"
        self.version = "1.0.0"
        self.transformation_count = 0
        self.success_rate = 1.0
        self.format_signatures = self._init_format_signatures()

    def _init_format_signatures(self) -> Dict[str, Dict]:
        """각 에이전트가 기대하는 데이터 형식 정의"""
        return {
            "nl_input": {
                "expected_fields": ["user_input", "project_config"],
                "format": "dict",
                "nested": False,
            },
            "parser": {
                "expected_fields": ["query", "context", "features"],
                "format": "dict_or_object",
                "nested": True,
            },
            "component_decision": {
                "expected_fields": ["parsed_data", "requirements", "framework"],
                "format": "object",
                "attributes": ["name", "description", "components"],
            },
            "generation": {
                "expected_fields": ["name", "description", "framework", "features"],
                "format": "dict",
                "nested": False,
            },
            "assembly": {
                "expected_fields": ["generated_files", "project_structure"],
                "format": "dict",
                "nested": True,
            },
        }

    async def detect_format(self, data: Any) -> str:
        """데이터 형식 자동 감지"""
        if data is None:
            return "none"
        elif isinstance(data, dict):
            if "data" in data and "context" in data:
                return "wrapped_dict"
            elif "query" in data or "user_input" in data:
                return "query_dict"
            else:
                return "plain_dict"
        elif isinstance(data, str):
            try:
                json.loads(data)
                return "json_string"
            except:
                return "plain_string"
        elif hasattr(data, "__dict__"):
            return "object"
        elif is_dataclass(data):
            return "dataclass"
        elif isinstance(data, list):
            return "list"
        else:
            return "unknown"

    async def transform_for_agent(
        self, data: Any, target_agent: str, source_agent: Optional[str] = None
    ) -> TransformationResult:
        """
        특정 에이전트를 위한 데이터 변환

        Args:
            data: 변환할 데이터
            target_agent: 대상 에이전트 이름
            source_agent: 소스 에이전트 이름 (선택)

        Returns:
            TransformationResult: 변환 결과
        """
        log = []

        try:
            # 1. 현재 형식 감지
            current_format = await self.detect_format(data)
            log.append(f"Detected format: {current_format}")

            # 2. 대상 에이전트의 기대 형식 확인
            target_spec = self.format_signatures.get(target_agent, {})
            expected_format = target_spec.get("format", "dict")
            log.append(f"Target agent '{target_agent}' expects: {expected_format}")

            # 3. 변환 수행
            transformed = await self._perform_transformation(
                data, current_format, expected_format, target_spec
            )

            # 4. 검증
            if await self._validate_transformation(transformed, target_spec):
                log.append("✅ Transformation successful")
                self.transformation_count += 1

                return TransformationResult(
                    success=True,
                    transformed_data=transformed,
                    original_format=current_format,
                    target_format=expected_format,
                    transformation_log=log,
                )
            else:
                raise ValueError("Transformation validation failed")

        except Exception as e:
            log.append(f"❌ Transformation failed: {str(e)}")
            self.success_rate *= 0.99

            # 폴백: 최선의 추측으로 변환
            fallback = await self._fallback_transform(data, target_agent)

            return TransformationResult(
                success=False,
                transformed_data=fallback,
                original_format=current_format
                if "current_format" in locals()
                else "unknown",
                target_format=expected_format
                if "expected_format" in locals()
                else "unknown",
                transformation_log=log,
                error=str(e),
            )

    async def _perform_transformation(
        self, data: Any, from_format: str, to_format: str, target_spec: Dict
    ) -> Any:
        """실제 변환 수행"""

        # wrapped_dict → dict
        if from_format == "wrapped_dict" and to_format == "dict":
            return data.get("data", data)

        # dict → object
        elif (
            from_format in ["dict", "plain_dict", "wrapped_dict"]
            and to_format == "object"
        ):
            return self._dict_to_object(data, target_spec)

        # dict_or_object (둘 다 허용)
        elif to_format == "dict_or_object":
            # 이미 dict면 그대로, 아니면 dict로 변환
            if from_format in ["dict", "plain_dict", "wrapped_dict", "query_dict"]:
                return data.get("data", data) if "data" in data else data
            else:
                return self._object_to_dict(data) if from_format == "object" else data

        # object → dict
        elif from_format == "object" and to_format == "dict":
            return self._object_to_dict(data)

        # dataclass → dict
        elif from_format == "dataclass" and to_format == "dict":
            return asdict(data)

        # json_string → dict
        elif from_format == "json_string":
            parsed = json.loads(data)
            if to_format == "dict":
                return parsed
            else:
                return await self._perform_transformation(
                    parsed, "dict", to_format, target_spec
                )

        # 같은 형식이면 그대로 반환
        elif from_format == to_format:
            return data

        # 기본: 최선의 추측
        else:
            return await self._smart_transform(data, target_spec)

    def _dict_to_object(self, data: Dict, spec: Dict) -> Any:
        """dict를 객체로 변환"""

        class DynamicObject:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)

        # wrapped dict 처리
        if isinstance(data, dict) and "data" in data:
            actual_data = data["data"]
        else:
            actual_data = data

        # 필수 속성 추가
        obj = DynamicObject()
        for attr in spec.get("attributes", []):
            if isinstance(actual_data, dict):
                setattr(obj, attr, actual_data.get(attr))
            else:
                setattr(obj, attr, None)

        # 나머지 속성 추가
        if isinstance(actual_data, dict):
            for key, value in actual_data.items():
                if not hasattr(obj, key):
                    setattr(obj, key, value)

        # context 추가 (있으면)
        if isinstance(data, dict) and "context" in data:
            obj.context = data["context"]

        return obj

    def _object_to_dict(self, obj: Any) -> Dict:
        """객체를 dict로 변환"""
        if hasattr(obj, "__dict__"):
            return obj.__dict__.copy()
        else:
            # 속성들을 수동으로 추출
            result = {}
            for attr in dir(obj):
                if not attr.startswith("_"):
                    try:
                        value = getattr(obj, attr)
                        if not callable(value):
                            result[attr] = value
                    except:
                        pass
            return result

    async def _smart_transform(self, data: Any, spec: Dict) -> Any:
        """스마트 변환 (AI 기반 추후 확장 가능)"""

        # 필수 필드 추출
        required_fields = spec.get("expected_fields", [])
        result = {}

        # 다양한 소스에서 필드 추출 시도
        for field in required_fields:
            value = None

            # dict에서 추출
            if isinstance(data, dict):
                value = data.get(field)
                if value is None and "data" in data:
                    value = data["data"].get(field)

            # 객체에서 추출
            elif hasattr(data, field):
                value = getattr(data, field)

            # 중첩된 구조에서 추출
            elif isinstance(data, dict):
                for key in data:
                    if isinstance(data[key], dict) and field in data[key]:
                        value = data[key][field]
                        break

            if value is not None:
                result[field] = value

        return result

    async def _validate_transformation(self, data: Any, spec: Dict) -> bool:
        """변환 결과 검증"""
        required_fields = spec.get("expected_fields", [])

        if not required_fields:
            return True

        # dict 검증
        if isinstance(data, dict):
            return any(field in data for field in required_fields)

        # 객체 검증
        elif hasattr(data, "__dict__"):
            return any(hasattr(data, field) for field in required_fields)

        return False

    async def _fallback_transform(self, data: Any, target_agent: str) -> Dict:
        """폴백 변환 (최후의 수단)"""

        # 기본 구조 생성
        result = {
            "name": "Unknown",
            "description": "Fallback transformation",
            "framework": "react",
            "features": [],
            "timestamp": datetime.now().isoformat(),
        }

        # 가능한 데이터 추출
        if isinstance(data, dict):
            result.update(data)
        elif hasattr(data, "__dict__"):
            result.update(self._object_to_dict(data))
        elif isinstance(data, str):
            result["raw_input"] = data

        return result

    async def auto_fix(
        self, error: Exception, data: Any, agent_name: str
    ) -> Optional[Any]:
        """
        에러 발생 시 자동 수정 시도

        예: "'dict' object has no attribute 'name'" 에러 시
        """
        error_msg = str(error)

        # 속성 접근 에러 감지
        if "has no attribute" in error_msg:
            # 에러에서 속성명 추출
            import re

            match = re.search(r"has no attribute '(\w+)'", error_msg)
            if match:
                attr_name = match.group(1)

                # dict를 객체로 변환
                if isinstance(data, dict):

                    class QuickFix:
                        def __init__(self, data):
                            self.__dict__.update(data)
                            # 누락된 속성 추가
                            if not hasattr(self, attr_name):
                                setattr(self, attr_name, data.get(attr_name, ""))

                    return QuickFix(data)

        # 타입 에러 감지
        elif "TypeError" in error_msg or "expected" in error_msg:
            # 형식 변환 시도
            result = await self.transform_for_agent(data, agent_name)
            if result.success:
                return result.transformed_data

        return None

    def get_statistics(self) -> Dict:
        """변환 통계"""
        return {
            "total_transformations": self.transformation_count,
            "success_rate": self.success_rate,
            "supported_formats": list(self.format_signatures.keys()),
        }


# 글로벌 인스턴스
data_transformer = DataTransformerAgent()


async def test_transformer():
    """테스트"""

    # 테스트 케이스 1: wrapped dict → object
    wrapped_data = {
        "data": {
            "name": "Todo App",
            "description": "Test app",
            "features": ["todo", "priority"],
        },
        "context": {"pipeline_id": "test_123"},
    }

    result = await data_transformer.transform_for_agent(
        wrapped_data, "component_decision"
    )

    print(f"Transformation 1: {result.success}")
    if result.success:
        print(f"  - Has 'name' attribute: {hasattr(result.transformed_data, 'name')}")
        print(
            f"  - Name value: {result.transformed_data.name if hasattr(result.transformed_data, 'name') else 'N/A'}"
        )

    # 테스트 케이스 2: object → dict
    class TestObject:
        def __init__(self):
            self.name = "Test"
            self.value = 123

    obj = TestObject()
    result2 = await data_transformer.transform_for_agent(obj, "generation")

    print(f"\nTransformation 2: {result2.success}")
    if result2.success:
        print(f"  - Is dict: {isinstance(result2.transformed_data, dict)}")
        print(f"  - Keys: {list(result2.transformed_data.keys())}")

    # 테스트 케이스 3: 자동 수정
    error = AttributeError("'dict' object has no attribute 'name'")
    fixed = await data_transformer.auto_fix(
        error, {"name": "Fixed"}, "component_decision"
    )

    print(f"\nAuto-fix: {fixed is not None}")
    if fixed:
        print(f"  - Has 'name': {hasattr(fixed, 'name')}")


if __name__ == "__main__":
    asyncio.run(test_transformer())
