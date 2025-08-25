"""SharedDocumentContext - 루프 내 모든 문서를 공유하는 컨텍스트

이 모듈은 Evolution Loop 내에서 생성되는 모든 문서를 중앙에서 관리하고,
모든 에이전트가 실시간으로 참조할 수 있도록 합니다.

주요 기능:
1. 현재 루프의 모든 문서 저장 및 공유
2. 루프별 문서 히스토리 관리
3. 에이전트 간 문서 참조 체계 제공
4. AI 프롬프트용 문서 컨텍스트 생성

이를 통해 AI 드리븐 동적 오케스트레이터가 모든 정보를 바탕으로
최적의 의사결정을 할 수 있습니다.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class SharedDocumentContext:
    """루프 내 모든 문서를 공유하는 컨텍스트

    Evolution Loop의 각 반복에서 생성되는 모든 문서를 중앙에서 관리하며,
    모든 에이전트가 필요한 정보를 즉시 참조할 수 있도록 합니다.
    """

    def __init__(self):
        """SharedDocumentContext 초기화"""
        self.current_loop_documents: dict[str, dict[str, Any]] = {}
        self.all_documents_history: list[dict[str, dict[str, Any]]] = []
        self.current_loop_number: int = 0
        self.metadata: dict[str, Any] = {
            "created_at": datetime.now().isoformat(),
            "total_documents": 0,
            "total_loops": 0,
        }

    def add_document(
        self, agent_name: str, document: dict[str, Any], document_type: str = "analysis"
    ) -> None:
        """문서 추가 - 모든 에이전트가 즉시 참조 가능

        Args:
            agent_name: 문서를 생성한 에이전트 이름
            document: 문서 내용
            document_type: 문서 타입 (analysis, design, plan, code 등)
        """
        doc_with_metadata = {
            "content": document,
            "type": document_type,
            "created_at": datetime.now().isoformat(),
            "loop_number": self.current_loop_number,
            "agent": agent_name,
        }

        self.current_loop_documents[agent_name] = doc_with_metadata
        self.metadata["total_documents"] += 1

        logger.info(
            f"Document added by {agent_name} (type: {document_type}) to loop {self.current_loop_number}"
        )

    def get_document(self, agent_name: str) -> Optional[dict[str, Any]]:
        """특정 에이전트의 문서 조회

        Args:
            agent_name: 조회할 에이전트 이름

        Returns:
            해당 에이전트의 문서 또는 None
        """
        return self.current_loop_documents.get(agent_name)

    def get_all_documents(self) -> dict[str, dict[str, Any]]:
        """현재 루프의 모든 문서 반환

        Returns:
            현재 루프에서 생성된 모든 문서
        """
        return self.current_loop_documents.copy()

    def get_documents_by_type(self, document_type: str) -> dict[str, dict[str, Any]]:
        """특정 타입의 문서만 필터링하여 반환

        Args:
            document_type: 필터링할 문서 타입

        Returns:
            해당 타입의 문서들
        """
        filtered = {}
        for agent_name, doc in self.current_loop_documents.items():
            if doc.get("type") == document_type:
                filtered[agent_name] = doc
        return filtered

    def start_new_loop(self) -> None:
        """새 루프 시작 - 이전 문서는 히스토리로 이동"""
        if self.current_loop_documents:
            # 현재 문서를 히스토리에 저장
            self.all_documents_history.append(self.current_loop_documents.copy())
            logger.info(f"Loop {self.current_loop_number} documents archived to history")

        # 새 루프 초기화
        self.current_loop_documents = {}
        self.current_loop_number += 1
        self.metadata["total_loops"] = self.current_loop_number

        logger.info(f"Started new loop {self.current_loop_number}")

    def get_history(self, loop_number: Optional[int] = None) -> Any:
        """히스토리 조회

        Args:
            loop_number: 조회할 루프 번호 (None이면 전체 히스토리)

        Returns:
            요청된 히스토리 문서
        """
        if loop_number is not None:
            if 0 <= loop_number < len(self.all_documents_history):
                return self.all_documents_history[loop_number]
            return None
        return self.all_documents_history

    def get_context_for_ai(self, include_history: bool = False, max_history_loops: int = 2) -> str:
        """AI 프롬프트용 컨텍스트 생성

        Args:
            include_history: 히스토리 포함 여부
            max_history_loops: 포함할 최대 히스토리 루프 수

        Returns:
            AI가 참조할 수 있는 형식의 문서 컨텍스트
        """
        context: Dict[str, Any] = {
            "current_loop": self.current_loop_number,
            "current_documents": {},
        }

        # 현재 루프 문서 추가
        for agent_name, doc in self.current_loop_documents.items():
            context["current_documents"][agent_name] = {
                "type": doc.get("type"),
                "created_at": doc.get("created_at"),
                "content": doc.get("content"),
            }

        # 히스토리 추가 (선택적)
        if include_history and self.all_documents_history:
            context["previous_loops"] = []
            start_idx = max(0, len(self.all_documents_history) - max_history_loops)
            for idx in range(start_idx, len(self.all_documents_history)):
                loop_data: Dict[str, Any] = {"loop_number": idx, "documents": {}}
                for agent_name, doc in self.all_documents_history[idx].items():
                    loop_data["documents"][agent_name] = {
                        "type": doc.get("type"),
                        "content_summary": self._summarize_content(doc.get("content")),
                    }
                context["previous_loops"].append(loop_data)

        return json.dumps(context, indent=2, ensure_ascii=False)

    def _summarize_content(self, content: Any, max_length: int = 500) -> str:
        """컨텐츠 요약 (긴 문서를 위해)

        Args:
            content: 요약할 내용
            max_length: 최대 길이

        Returns:
            요약된 문자열
        """
        if isinstance(content, str):
            return content[:max_length] + "..." if len(content) > max_length else content
        elif isinstance(content, dict):
            # 주요 키만 추출
            summary = dict(list(content.items())[:5])
            return str(summary)
        else:
            return str(content)[:max_length]

    def get_analysis_summary(self) -> dict[str, Any]:
        """현재까지의 분석 요약

        Returns:
            전체 분석 상황 요약
        """
        summary = {
            "total_loops": self.current_loop_number,
            "total_documents": self.metadata["total_documents"],
            "current_loop_progress": {
                "documents_created": len(self.current_loop_documents),
                "agents_executed": list(self.current_loop_documents.keys()),
            },
            "document_types": {},
        }

        # 문서 타입별 카운트
        for doc in self.current_loop_documents.values():
            doc_type = doc.get("type", "unknown")
            summary["document_types"][doc_type] = summary["document_types"].get(doc_type, 0) + 1

        return summary

    def clear(self) -> None:
        """모든 문서 및 히스토리 초기화"""
        self.current_loop_documents = {}
        self.all_documents_history = []
        self.current_loop_number = 0
        self.metadata = {
            "created_at": datetime.now().isoformat(),
            "total_documents": 0,
            "total_loops": 0,
        }
        logger.info("SharedDocumentContext cleared")

    def export_all(self) -> dict[str, Any]:
        """모든 데이터 내보내기 (백업/저장용)

        Returns:
            전체 컨텍스트 데이터
        """
        return {
            "metadata": self.metadata,
            "current_loop_number": self.current_loop_number,
            "current_loop_documents": self.current_loop_documents,
            "all_documents_history": self.all_documents_history,
        }

    def import_data(self, data: dict[str, Any]) -> None:
        """데이터 가져오기 (복원용)

        Args:
            data: 가져올 데이터
        """
        self.metadata = data.get("metadata", self.metadata)
        self.current_loop_number = data.get("current_loop_number", 0)
        self.current_loop_documents = data.get("current_loop_documents", {})
        self.all_documents_history = data.get("all_documents_history", [])
        logger.info("SharedDocumentContext data imported")