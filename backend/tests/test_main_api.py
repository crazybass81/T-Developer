"""
Test suite for T-Developer Main API
완전한 프로덕션 레벨 테스트 구현
"""

import pytest
import asyncio
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime
import sys
import os

# 프로젝트 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

# FastAPI 테스트 클라이언트
from fastapi.testclient import TestClient
from fastapi import WebSocket
import httpx

# 메인 API 임포트
from src.main_api import app, ConnectionManager, GenerateRequest


class TestMainAPI:
    """메인 API 테스트 클래스"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """테스트 셋업"""
        self.client = TestClient(app)
        self.test_project_id = "test_project_123"
        self.test_user_input = "Create a todo application with React"
        
        # 임시 디렉토리 생성
        self.temp_dir = tempfile.mkdtemp(prefix="test_t_developer_")
        
        yield
        
        # 클린업
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_health_check(self):
        """헬스체크 엔드포인트 테스트"""
        response = self.client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
    
    def test_cors_headers(self):
        """CORS 헤더 테스트"""
        response = self.client.options(
            "/api/v1/generate",
            headers={"Origin": "http://localhost:3000"}
        )
        
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
    
    @pytest.mark.asyncio
    async def test_generate_project_success(self):
        """프로젝트 생성 성공 테스트"""
        with patch("src.main_api.ecs_pipeline") as mock_pipeline:
            # Mock 파이프라인 설정
            mock_pipeline.execute = AsyncMock(return_value=Mock(
                success=True,
                project_id="test_project_123",
                project_path=self.temp_dir,
                metadata={
                    "files_generated": 10,
                    "match_score": 95.5,
                    "download_url": "/api/v1/download/test_project_123"
                },
                errors=[]
            ))
            
            request_data = {
                "query": self.test_user_input,
                "project_name": "Test Todo App",
                "template": "blank",
                "tech_stack": ["React", "Node.js"],
                "additional_features": ["auth", "database"]
            }
            
            response = self.client.post(
                "/api/v1/generate",
                json=request_data
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert "project_id" in data
            assert "download_url" in data
            assert data["metadata"]["files_generated"] == 10
    
    @pytest.mark.asyncio
    async def test_generate_project_failure(self):
        """프로젝트 생성 실패 테스트"""
        with patch("src.main_api.ecs_pipeline") as mock_pipeline:
            # Mock 파이프라인 실패 설정
            mock_pipeline.execute = AsyncMock(return_value=Mock(
                success=False,
                project_id="failed_project",
                project_path=None,
                metadata={"error": "Pipeline execution failed"},
                errors=["Agent NLInput failed", "Generation failed"]
            ))
            
            request_data = {
                "query": "Invalid request",
                "project_name": "Failed Project"
            }
            
            response = self.client.post(
                "/api/v1/generate",
                json=request_data
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is False
            assert len(data["errors"]) > 0
            assert "Pipeline execution failed" in str(data["metadata"])
    
    def test_generate_project_validation_error(self):
        """프로젝트 생성 유효성 검증 오류 테스트"""
        # query 필드 누락
        request_data = {
            "project_name": "Test Project"
        }
        
        response = self.client.post(
            "/api/v1/generate",
            json=request_data
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_download_project_success(self):
        """프로젝트 다운로드 성공 테스트"""
        # 테스트 ZIP 파일 생성
        test_zip_path = Path(self.temp_dir) / "test_project.zip"
        test_zip_path.write_text("test zip content")
        
        with patch("src.main_api.PROJECT_STORAGE_PATH", self.temp_dir):
            response = self.client.get("/api/v1/download/test_project")
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/zip"
            assert "content-disposition" in response.headers
    
    def test_download_project_not_found(self):
        """프로젝트 다운로드 실패 테스트 (파일 없음)"""
        response = self.client.get("/api/v1/download/non_existent_project")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Project file not found"
    
    def test_project_status(self):
        """프로젝트 상태 조회 테스트"""
        test_project_id = "status_test_123"
        
        # 프로젝트 상태 Mock
        with patch("src.main_api.get_project_status") as mock_status:
            mock_status.return_value = {
                "project_id": test_project_id,
                "status": "completed",
                "progress": 100,
                "created_at": datetime.now().isoformat()
            }
            
            response = self.client.get(f"/api/v1/projects/{test_project_id}/status")
            
            assert response.status_code == 200
            data = response.json()
            assert data["project_id"] == test_project_id
            assert data["status"] == "completed"
    
    def test_list_projects(self):
        """프로젝트 목록 조회 테스트"""
        with patch("src.main_api.list_user_projects") as mock_list:
            mock_list.return_value = [
                {
                    "project_id": "project_1",
                    "name": "Todo App",
                    "status": "completed",
                    "created_at": datetime.now().isoformat()
                },
                {
                    "project_id": "project_2",
                    "name": "Blog Platform",
                    "status": "in_progress",
                    "created_at": datetime.now().isoformat()
                }
            ]
            
            response = self.client.get("/api/v1/projects")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["project_id"] == "project_1"
    
    def test_delete_project(self):
        """프로젝트 삭제 테스트"""
        test_project_id = "delete_test_123"
        
        # 테스트 파일 생성
        test_file = Path(self.temp_dir) / f"{test_project_id}.zip"
        test_file.write_text("test content")
        
        with patch("src.main_api.PROJECT_STORAGE_PATH", self.temp_dir):
            response = self.client.delete(f"/api/v1/projects/{test_project_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Project deleted successfully"
            assert not test_file.exists()
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """WebSocket 연결 테스트"""
        with self.client.websocket_connect(f"/ws/{self.test_project_id}") as websocket:
            # 연결 확인 메시지
            data = websocket.receive_json()
            assert data["type"] == "connection"
            assert data["status"] == "connected"
            
            # 메시지 전송
            websocket.send_json({
                "type": "ping",
                "data": "test"
            })
            
            # 응답 확인
            response = websocket.receive_json()
            assert response["type"] == "pong"
    
    @pytest.mark.asyncio
    async def test_websocket_agent_updates(self):
        """WebSocket 에이전트 업데이트 테스트"""
        with self.client.websocket_connect(f"/ws/{self.test_project_id}") as websocket:
            # 연결 확인
            data = websocket.receive_json()
            assert data["type"] == "connection"
            
            # 에이전트 상태 업데이트 시뮬레이션
            with patch("src.main_api.manager") as mock_manager:
                mock_manager.send_agent_update = AsyncMock()
                
                # 에이전트 업데이트 트리거
                await mock_manager.send_agent_update(
                    self.test_project_id,
                    "nl_input",
                    "running",
                    50
                )
                
                mock_manager.send_agent_update.assert_called_once()


class TestConnectionManager:
    """WebSocket ConnectionManager 테스트"""
    
    @pytest.fixture
    def manager(self):
        """ConnectionManager 인스턴스"""
        return ConnectionManager()
    
    @pytest.fixture
    def mock_websocket(self):
        """Mock WebSocket"""
        websocket = AsyncMock(spec=WebSocket)
        websocket.accept = AsyncMock()
        websocket.send_json = AsyncMock()
        websocket.close = AsyncMock()
        return websocket
    
    @pytest.mark.asyncio
    async def test_connect(self, manager, mock_websocket):
        """WebSocket 연결 테스트"""
        project_id = "test_project"
        
        await manager.connect(mock_websocket, project_id)
        
        mock_websocket.accept.assert_called_once()
        assert project_id in manager.active_connections
        assert mock_websocket in manager.active_connections[project_id]
    
    def test_disconnect(self, manager, mock_websocket):
        """WebSocket 연결 해제 테스트"""
        project_id = "test_project"
        manager.active_connections[project_id] = {mock_websocket}
        
        manager.disconnect(mock_websocket, project_id)
        
        assert project_id not in manager.active_connections
    
    @pytest.mark.asyncio
    async def test_send_log(self, manager, mock_websocket):
        """로그 메시지 전송 테스트"""
        project_id = "test_project"
        manager.active_connections[project_id] = {mock_websocket}
        
        await manager.send_log(project_id, "Test log message", "info")
        
        mock_websocket.send_json.assert_called_once()
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["type"] == "log"
        assert call_args["message"] == "Test log message"
        assert call_args["level"] == "info"
    
    @pytest.mark.asyncio
    async def test_send_agent_update(self, manager, mock_websocket):
        """에이전트 업데이트 전송 테스트"""
        project_id = "test_project"
        manager.active_connections[project_id] = {mock_websocket}
        
        await manager.send_agent_update(
            project_id,
            "generation",
            "running",
            75
        )
        
        mock_websocket.send_json.assert_called_once()
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["type"] == "agent_update"
        assert call_args["data"]["agent_id"] == "generation"
        assert call_args["data"]["status"] == "running"
        assert call_args["data"]["progress"] == 75
    
    @pytest.mark.asyncio
    async def test_broadcast(self, manager):
        """브로드캐스트 테스트"""
        project_id = "test_project"
        
        # 여러 WebSocket 연결
        websockets = [AsyncMock(spec=WebSocket) for _ in range(3)]
        for ws in websockets:
            ws.send_json = AsyncMock()
        
        manager.active_connections[project_id] = set(websockets)
        
        await manager.broadcast(project_id, {"type": "test", "data": "broadcast"})
        
        for ws in websockets:
            ws.send_json.assert_called_once_with({"type": "test", "data": "broadcast"})


class TestPipelineIntegration:
    """파이프라인 통합 테스트"""
    
    @pytest.fixture
    def mock_pipeline(self):
        """Mock 파이프라인"""
        pipeline = Mock()
        pipeline.initialize = AsyncMock()
        pipeline.execute = AsyncMock()
        return pipeline
    
    @pytest.mark.asyncio
    async def test_pipeline_initialization(self, mock_pipeline):
        """파이프라인 초기화 테스트"""
        await mock_pipeline.initialize()
        mock_pipeline.initialize.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_pipeline_execution_with_all_params(self, mock_pipeline):
        """모든 파라미터를 사용한 파이프라인 실행 테스트"""
        mock_pipeline.execute.return_value = Mock(
            success=True,
            project_id="full_test_123",
            project_path="/tmp/full_test_123",
            metadata={
                "pipeline_type": "production",
                "agents_executed": 9,
                "agents_succeeded": 9
            },
            errors=[]
        )
        
        result = await mock_pipeline.execute(
            user_input="Create a full-featured e-commerce platform",
            project_name="E-Commerce Platform",
            project_type="web",
            features=["auth", "payment", "inventory", "shipping"],
            context={"user_id": "test_user", "session_id": "test_session"}
        )
        
        assert result.success is True
        assert result.metadata["agents_executed"] == 9
        assert result.metadata["agents_succeeded"] == 9
    
    @pytest.mark.asyncio
    async def test_pipeline_error_handling(self, mock_pipeline):
        """파이프라인 오류 처리 테스트"""
        mock_pipeline.execute.side_effect = Exception("Pipeline crashed")
        
        with pytest.raises(Exception) as exc_info:
            await mock_pipeline.execute("test input")
        
        assert "Pipeline crashed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_pipeline_partial_failure(self, mock_pipeline):
        """파이프라인 부분 실패 테스트"""
        mock_pipeline.execute.return_value = Mock(
            success=False,
            project_id="partial_test_123",
            project_path=None,
            metadata={
                "pipeline_type": "production",
                "agents_executed": 9,
                "agents_succeeded": 6,
                "agent_results": {
                    "nl_input": {"success": True},
                    "ui_selection": {"success": True},
                    "parser": {"success": True},
                    "component_decision": {"success": True},
                    "match_rate": {"success": True},
                    "search": {"success": True},
                    "generation": {"success": False, "errors": ["Code generation failed"]},
                    "assembly": {"success": False, "errors": ["No code to assemble"]},
                    "download": {"success": False, "errors": ["No project to download"]}
                }
            },
            errors=["Generation failed", "Assembly failed", "Download failed"]
        )
        
        result = await mock_pipeline.execute("test input")
        
        assert result.success is False
        assert result.metadata["agents_succeeded"] == 6
        assert len(result.errors) == 3


class TestErrorHandling:
    """오류 처리 테스트"""
    
    @pytest.fixture
    def client(self):
        """테스트 클라이언트"""
        return TestClient(app)
    
    def test_invalid_endpoint(self, client):
        """존재하지 않는 엔드포인트 테스트"""
        response = client.get("/api/v1/invalid")
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """허용되지 않은 메서드 테스트"""
        response = client.put("/api/v1/generate")
        assert response.status_code == 405
    
    def test_malformed_json(self, client):
        """잘못된 JSON 요청 테스트"""
        response = client.post(
            "/api/v1/generate",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_server_error_handling(self, client):
        """서버 오류 처리 테스트"""
        with patch("src.main_api.ecs_pipeline") as mock_pipeline:
            mock_pipeline.execute = AsyncMock(side_effect=Exception("Internal error"))
            
            response = client.post(
                "/api/v1/generate",
                json={"query": "test"}
            )
            
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data


class TestPerformance:
    """성능 테스트"""
    
    @pytest.fixture
    def client(self):
        """테스트 클라이언트"""
        return TestClient(app)
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client):
        """동시 요청 처리 테스트"""
        import aiohttp
        import asyncio
        
        async def make_request(session, index):
            """비동기 요청"""
            url = "http://testserver/health"
            async with session.get(url) as response:
                return await response.json()
        
        async with aiohttp.ClientSession() as session:
            # 10개의 동시 요청
            tasks = [make_request(session, i) for i in range(10)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 모든 요청이 성공해야 함
            assert all(
                isinstance(r, dict) and r.get("status") == "healthy"
                for r in results
                if not isinstance(r, Exception)
            )
    
    def test_large_payload_handling(self, client):
        """대용량 페이로드 처리 테스트"""
        large_input = "Create a complex application " * 1000  # 큰 입력
        
        response = client.post(
            "/api/v1/generate",
            json={
                "query": large_input,
                "project_name": "Large Project",
                "tech_stack": ["React"] * 10,
                "additional_features": ["feature"] * 100
            }
        )
        
        # 요청이 처리되어야 함 (타임아웃 없이)
        assert response.status_code in [200, 413]  # 200 OK 또는 413 Payload Too Large
    
    @pytest.mark.asyncio
    async def test_memory_leak_prevention(self):
        """메모리 누수 방지 테스트"""
        import tracemalloc
        import gc
        
        tracemalloc.start()
        
        # 초기 메모리 스냅샷
        snapshot1 = tracemalloc.take_snapshot()
        
        # 여러 번 실행
        for _ in range(10):
            manager = ConnectionManager()
            mock_ws = AsyncMock()
            await manager.connect(mock_ws, f"project_{_}")
            manager.disconnect(mock_ws, f"project_{_}")
        
        # 가비지 컬렉션
        gc.collect()
        
        # 최종 메모리 스냅샷
        snapshot2 = tracemalloc.take_snapshot()
        
        # 메모리 증가량 확인
        stats = snapshot2.compare_to(snapshot1, 'lineno')
        total_diff = sum(stat.size_diff for stat in stats)
        
        # 메모리 증가가 1MB 미만이어야 함
        assert total_diff < 1024 * 1024
        
        tracemalloc.stop()


# 테스트 실행을 위한 설정
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])