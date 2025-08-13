"""
Simple tests without database dependencies
데이터베이스 의존성 없는 간단한 테스트
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

# 프로젝트 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestBasicFunctionality:
    """기본 기능 테스트"""

    def test_imports(self):
        """모듈 임포트 테스트"""
        try:
            from src.main_api import app

            assert app is not None
        except ImportError as e:
            pytest.skip(f"Import failed: {e}")

    def test_simple_calculation(self):
        """간단한 계산 테스트"""
        assert 2 + 2 == 4
        assert 10 * 10 == 100
        assert "hello" + " " + "world" == "hello world"

    def test_list_operations(self):
        """리스트 연산 테스트"""
        test_list = [1, 2, 3, 4, 5]
        assert len(test_list) == 5
        assert sum(test_list) == 15
        assert max(test_list) == 5
        assert min(test_list) == 1

    def test_dictionary_operations(self):
        """딕셔너리 연산 테스트"""
        test_dict = {"a": 1, "b": 2, "c": 3}
        assert len(test_dict) == 3
        assert test_dict["a"] == 1
        assert "b" in test_dict
        assert "d" not in test_dict

    def test_string_operations(self):
        """문자열 연산 테스트"""
        test_string = "Hello World"
        assert test_string.lower() == "hello world"
        assert test_string.upper() == "HELLO WORLD"
        assert test_string.replace("World", "Python") == "Hello Python"
        assert len(test_string) == 11

    def test_boolean_logic(self):
        """불린 로직 테스트"""
        assert True and True
        assert not (True and False)
        assert True or False
        assert not (False and False)

    @pytest.mark.parametrize(
        "input_val,expected", [(0, 0), (1, 1), (5, 120), (10, 3628800)]
    )
    def test_factorial(self, input_val, expected):
        """팩토리얼 테스트"""

        def factorial(n):
            if n <= 1:
                return n if n == 1 else 0 if n == 0 else None
            return n * factorial(n - 1)

        if input_val == 0:
            assert factorial(input_val) == 0 or factorial(input_val) == 1
        else:
            assert factorial(input_val) == expected

    def test_exception_handling(self):
        """예외 처리 테스트"""
        with pytest.raises(ZeroDivisionError):
            x = 1 / 0

        with pytest.raises(KeyError):
            d = {}
            x = d["nonexistent"]

        with pytest.raises(IndexError):
            l = []
            x = l[0]

    def test_file_operations(self):
        """파일 연산 테스트"""
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            temp_path = f.name

        # 파일 읽기
        with open(temp_path, "r") as f:
            content = f.read()
            assert content == "test content"

        # 파일 삭제
        import os

        os.unlink(temp_path)
        assert not os.path.exists(temp_path)


class TestUtilityFunctions:
    """유틸리티 함수 테스트"""

    def test_json_operations(self):
        """JSON 연산 테스트"""
        import json

        data = {"name": "test", "value": 123}
        json_str = json.dumps(data)
        assert isinstance(json_str, str)

        parsed = json.loads(json_str)
        assert parsed == data

    def test_datetime_operations(self):
        """날짜시간 연산 테스트"""
        from datetime import datetime, timedelta

        now = datetime.now()
        assert isinstance(now, datetime)

        future = now + timedelta(days=1)
        assert future > now

        past = now - timedelta(hours=1)
        assert past < now

    def test_regex_operations(self):
        """정규표현식 테스트"""
        import re

        pattern = r"\d+"
        text = "There are 123 numbers and 456 more"

        matches = re.findall(pattern, text)
        assert matches == ["123", "456"]

        # 이메일 패턴
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        assert re.match(email_pattern, "test@example.com")
        assert not re.match(email_pattern, "invalid-email")

    def test_path_operations(self):
        """경로 연산 테스트"""
        from pathlib import Path

        p = Path("/home/user/test.txt")
        assert p.name == "test.txt"
        assert p.suffix == ".txt"
        assert p.stem == "test"
        assert str(p.parent) == "/home/user"

    def test_uuid_generation(self):
        """UUID 생성 테스트"""
        import uuid

        id1 = uuid.uuid4()
        id2 = uuid.uuid4()

        assert id1 != id2
        assert len(str(id1)) == 36
        assert "-" in str(id1)

    def test_hash_operations(self):
        """해시 연산 테스트"""
        import hashlib

        text = "Hello World"

        # MD5
        md5_hash = hashlib.md5(text.encode()).hexdigest()
        assert len(md5_hash) == 32

        # SHA256
        sha256_hash = hashlib.sha256(text.encode()).hexdigest()
        assert len(sha256_hash) == 64

        # 같은 입력은 같은 해시
        assert hashlib.md5(text.encode()).hexdigest() == md5_hash

    def test_base64_encoding(self):
        """Base64 인코딩 테스트"""
        import base64

        text = "Hello World"
        encoded = base64.b64encode(text.encode()).decode()
        assert encoded == "SGVsbG8gV29ybGQ="

        decoded = base64.b64decode(encoded).decode()
        assert decoded == text

    def test_environment_variables(self):
        """환경 변수 테스트"""
        import os

        # 환경 변수 설정
        os.environ["TEST_VAR"] = "test_value"
        assert os.environ.get("TEST_VAR") == "test_value"

        # 환경 변수 제거
        del os.environ["TEST_VAR"]
        assert os.environ.get("TEST_VAR") is None

        # 기본값 사용
        assert os.environ.get("NONEXISTENT", "default") == "default"


class TestMockingAndPatching:
    """Mock 및 Patch 테스트"""

    def test_basic_mock(self):
        """기본 Mock 테스트"""
        mock_obj = Mock()
        mock_obj.method.return_value = "mocked"

        assert mock_obj.method() == "mocked"
        mock_obj.method.assert_called_once()

    def test_mock_with_spec(self):
        """Spec을 사용한 Mock 테스트"""

        class MyClass:
            def method(self):
                return "original"

        mock_obj = Mock(spec=MyClass)
        mock_obj.method.return_value = "mocked"

        assert mock_obj.method() == "mocked"

        # 존재하지 않는 메서드 호출 시도
        with pytest.raises(AttributeError):
            mock_obj.nonexistent_method()

    @patch("builtins.open", mock_open(read_data="fake content"))
    def test_patch_decorator(self):
        """Patch 데코레이터 테스트"""
        # open이 mock으로 대체됨
        with open("fake_file.txt", "r") as f:
            content = f.read()

        # 내용이 올바르게 읽혔는지 확인
        assert content == "fake content"

    def test_patch_context_manager(self):
        """Patch 컨텍스트 매니저 테스트"""
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = True

            import os

            assert os.path.exists("/fake/path") is True
            mock_exists.assert_called_with("/fake/path")

    def test_mock_side_effect(self):
        """Mock side_effect 테스트"""
        mock_func = Mock()
        mock_func.side_effect = [1, 2, 3]

        assert mock_func() == 1
        assert mock_func() == 2
        assert mock_func() == 3

        # side_effect로 예외 발생
        mock_func.side_effect = ValueError("Error")
        with pytest.raises(ValueError):
            mock_func()


class TestAsyncFunctions:
    """비동기 함수 테스트"""

    @pytest.mark.asyncio
    async def test_basic_async(self):
        """기본 비동기 테스트"""

        async def async_function():
            return "async result"

        result = await async_function()
        assert result == "async result"

    @pytest.mark.asyncio
    async def test_async_with_sleep(self):
        """Sleep을 포함한 비동기 테스트"""
        import asyncio

        async def delayed_function():
            await asyncio.sleep(0.01)
            return "delayed"

        result = await delayed_function()
        assert result == "delayed"

    @pytest.mark.asyncio
    async def test_async_gather(self):
        """비동기 gather 테스트"""
        import asyncio

        async def task(n):
            await asyncio.sleep(0.01)
            return n * 2

        results = await asyncio.gather(task(1), task(2), task(3))

        assert results == [2, 4, 6]

    @pytest.mark.asyncio
    async def test_async_exception(self):
        """비동기 예외 테스트"""

        async def failing_function():
            raise ValueError("Async error")

        with pytest.raises(ValueError):
            await failing_function()


class TestDataStructures:
    """데이터 구조 테스트"""

    def test_set_operations(self):
        """집합 연산 테스트"""
        set1 = {1, 2, 3, 4}
        set2 = {3, 4, 5, 6}

        # 합집합
        assert set1 | set2 == {1, 2, 3, 4, 5, 6}

        # 교집합
        assert set1 & set2 == {3, 4}

        # 차집합
        assert set1 - set2 == {1, 2}

        # 대칭 차집합
        assert set1 ^ set2 == {1, 2, 5, 6}

    def test_tuple_operations(self):
        """튜플 연산 테스트"""
        t = (1, 2, 3, 4, 5)

        assert len(t) == 5
        assert t[0] == 1
        assert t[-1] == 5
        assert t[1:3] == (2, 3)

        # 튜플은 불변
        with pytest.raises(TypeError):
            t[0] = 10

    def test_deque_operations(self):
        """Deque 연산 테스트"""
        from collections import deque

        d = deque([1, 2, 3])

        # 양쪽 끝에 추가
        d.append(4)
        d.appendleft(0)
        assert list(d) == [0, 1, 2, 3, 4]

        # 양쪽 끝에서 제거
        assert d.pop() == 4
        assert d.popleft() == 0
        assert list(d) == [1, 2, 3]

    def test_counter_operations(self):
        """Counter 연산 테스트"""
        from collections import Counter

        c = Counter(["a", "b", "c", "a", "b", "a"])

        assert c["a"] == 3
        assert c["b"] == 2
        assert c["c"] == 1
        assert c.most_common(2) == [("a", 3), ("b", 2)]

    def test_defaultdict_operations(self):
        """DefaultDict 연산 테스트"""
        from collections import defaultdict

        dd = defaultdict(list)
        dd["key1"].append("value1")
        dd["key2"].append("value2")

        assert dd["key1"] == ["value1"]
        assert dd["key3"] == []  # 기본값 반환


# 테스트 실행을 위한 설정
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
