import pytest
from unittest.mock import Mock, patch, AsyncMock
from backend.src.agents.implementations.nl_context_manager import ConversationContextManager

class TestConversationContextManager:
    """대화 컨텍스트 관리자 테스트"""

    @pytest.fixture
    def context_manager(self):
        with patch('boto3.resource'):
            return ConversationContextManager()

    @pytest.fixture
    def sample_user_history(self):
        return [
            {
                'session_id': 'session1',
                'messages': [{
                    'extracted_info': {
                        'tech_stack': ['react', 'node'],
                        'requirements': ['user authentication', 'data storage']
                    }
                }]
            },
            {
                'session_id': 'session2',
                'messages': [{
                    'extracted_info': {
                        'tech_stack': ['react', 'python'],
                        'requirements': ['user authentication', 'api integration']
                    }
                }]
            }
        ]

    @pytest.mark.asyncio
    async def test_get_conversation_context_new_session(self, context_manager):
        """새 세션 컨텍스트 조회 테스트"""
        with patch.object(context_manager.table, 'get_item', return_value={'Item': {}}):
            with patch.object(context_manager.table, 'query', return_value={'Items': []}):
                context = await context_manager.get_conversation_context('new_session', 'user123')
                
                assert context.session_id == 'new_session'
                assert context.user_id == 'user123'
                assert context.current_messages == []

    @pytest.mark.asyncio
    async def test_analyze_user_patterns(self, context_manager, sample_user_history):
        """사용자 패턴 분석 테스트"""
        patterns = await context_manager._analyze_user_patterns(sample_user_history)
        
        # 기술 스택 빈도 확인
        assert len(patterns['tech_stacks']) > 0
        assert ('react', 2) in patterns['tech_stacks']  # react가 2번 나타남
        
        # 공통 요구사항 확인
        assert 'user authentication' in patterns['common_requirements']

    @pytest.mark.asyncio
    async def test_update_context(self, context_manager):
        """컨텍스트 업데이트 테스트"""
        message = {
            'user_id': 'user123',
            'role': 'user',
            'content': 'Create a web app'
        }
        
        with patch.object(context_manager, 'get_conversation_context', new_callable=AsyncMock) as mock_get:
            mock_context = Mock()
            mock_context.current_messages = []
            mock_get.return_value = mock_context
            
            with patch.object(context_manager.table, 'put_item') as mock_put:
                await context_manager.update_context('session123', message)
                
                mock_put.assert_called_once()
                # TTL이 설정되었는지 확인
                call_args = mock_put.call_args[1]['Item']
                assert 'ttl' in call_args

    @pytest.mark.asyncio
    async def test_message_history_limit(self, context_manager):
        """메시지 히스토리 제한 테스트"""
        # 50개 이상의 메시지가 있는 컨텍스트 생성
        long_messages = [{'content': f'message {i}'} for i in range(55)]
        
        with patch.object(context_manager, 'get_conversation_context', new_callable=AsyncMock) as mock_get:
            mock_context = Mock()
            mock_context.current_messages = long_messages
            mock_get.return_value = mock_context
            
            with patch.object(context_manager, '_summarize_old_messages', new_callable=AsyncMock) as mock_summarize:
                mock_summarize.return_value = {'content': 'summary', 'is_summary': True}
                
                with patch.object(context_manager.table, 'put_item'):
                    message = {'user_id': 'user123', 'role': 'user', 'content': 'new message'}
                    await context_manager.update_context('session123', message)
                    
                    # 요약이 호출되었는지 확인
                    mock_summarize.assert_called_once()

    def test_normalize_requirement(self, context_manager):
        """요구사항 정규화 테스트"""
        req1 = "  User Authentication  "
        req2 = "USER AUTHENTICATION"
        
        normalized1 = context_manager._normalize_requirement(req1)
        normalized2 = context_manager._normalize_requirement(req2)
        
        assert normalized1 == normalized2
        assert normalized1 == "user authentication"