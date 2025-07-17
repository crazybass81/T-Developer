import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/TaskCreationPage.css';

function TaskCreationPage() {
  const navigate = useNavigate();
  const [request, setRequest] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // API 호출
      const response = await axios.post('/api/tasks', {
        request,
        user_id: 'web-user' // 실제 구현에서는 인증된 사용자 ID 사용
      });
      
      // 작업 ID를 받아 모니터링 페이지로 이동
      const taskId = response.data.task_id;
      navigate(`/tasks/${taskId}/monitor`);
    } catch (err) {
      console.error('Error creating task:', err);
      setError('작업 생성 중 오류가 발생했습니다. 다시 시도해주세요.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="task-creation-container">
      <h2>새 기능 요청</h2>
      
      {error && <div className="error-message">{error}</div>}
      
      <form onSubmit={handleSubmit} className="task-form">
        <div className="form-group">
          <label htmlFor="request">기능 요청 내용</label>
          <textarea
            id="request"
            value={request}
            onChange={(e) => setRequest(e.target.value)}
            required
            placeholder="사용자가 질문을 입력하면 관련된 정부 지원사업을 검색하여 추천하는 기능을 추가해줘."
            rows={5}
          />
        </div>
        
        <button 
          type="submit" 
          className="submit-button"
          disabled={loading}
        >
          {loading ? '요청 처리 중...' : '요청 보내기'}
        </button>
      </form>
    </div>
  );
}

export default TaskCreationPage;