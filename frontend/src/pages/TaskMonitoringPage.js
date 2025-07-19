import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import taskService from '../api/taskService';
import '../styles/TaskMonitoringPage.css';

function TaskMonitoringPage() {
  const { taskId } = useParams();
  const navigate = useNavigate();
  const [task, setTask] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [events, setEvents] = useState([]);

  // 작업 상태에 따른 아이콘 매핑
  const statusIcons = {
    received: '✅',
    planning: '🔄',
    planned: '📋',
    coding: '💻',
    coded: '💾',
    testing: '🧪',
    tested: '✅',
    deploying: '🚀',
    deployed: '🚀',
    completed: '🎉',
    error: '⚠️'
  };

  // 작업 정보 가져오기
  useEffect(() => {
    const fetchTask = async () => {
      try {
        // 임시 처리: API 호출 대신 더미 데이터 사용
        // 실제 API가 준비되면 아래 주석을 해제하세요
        /*
        const response = await taskService.getTask(taskId);
        setTask(response.data);
        */
        
        // 더미 데이터 - 시간에 따라 상태가 변하도록 설정
        const now = new Date();
        const startTime = new Date(parseInt(taskId.split('-')[1])); // TASK-timestamp 형식 가정
        const elapsedSeconds = Math.floor((now - startTime) / 1000);
        
        let status = 'received';
        if (elapsedSeconds > 3) status = 'planning';
        if (elapsedSeconds > 6) status = 'planned';
        if (elapsedSeconds > 9) status = 'coding';
        if (elapsedSeconds > 12) status = 'coded';
        if (elapsedSeconds > 15) status = 'testing';
        if (elapsedSeconds > 18) status = 'tested';
        if (elapsedSeconds > 21) status = 'deploying';
        if (elapsedSeconds > 24) status = 'deployed';
        if (elapsedSeconds > 27) status = 'completed';
        
        const dummyTask = {
          task_id: taskId,
          request: '사용자가 질문을 입력하면 관련된 정부 지원사업을 검색하여 추천하는 기능을 추가해줘.',
          status: status,
          created_at: startTime.toISOString(),
          updated_at: now.toISOString(),
          plan_summary: '정부 지원사업 검색 및 추천 기능 구현 계획',
          modified_files: ['src/services/searchService.js', 'src/controllers/chatController.js'],
          created_files: ['src/services/governmentSupportService.js'],
          branch_name: `feature/${taskId}`,
          commit_hash: 'abc123def456',
          test_success: true,
          pr_url: 'https://github.com/example/repo/pull/123',
          deployed_version: 'v1.0.0',
          deployed_url: 'https://example.com/app'
        };
        
        setTask(dummyTask);
        
        // 작업 상태에 따라 이벤트 생성
        generateEvents(dummyTask);
      } catch (err) {
        console.error('Error fetching task:', err);
        setError('작업 정보를 가져오는 중 오류가 발생했습니다.');
      } finally {
        setLoading(false);
      }
    };

    fetchTask();

    // 주기적으로 작업 상태 업데이트 (3초마다)
    const interval = setInterval(fetchTask, 3000);
    
    return () => clearInterval(interval);
  }, [taskId]);

  // 작업 상태에 따라 이벤트 생성
  const generateEvents = (taskData) => {
    if (!taskData) return;
    
    const newEvents = [];
    
    // 접수 이벤트
    newEvents.push({
      id: 1,
      time: new Date(taskData.created_at).toLocaleTimeString(),
      status: 'received',
      title: '작업 접수',
      description: `"${taskData.request}"`,
      icon: '✅'
    });
    
    // 계획 시작 이벤트 (상태가 planning 이상인 경우)
    if (['planning', 'planned', 'coding', 'coded', 'testing', 'tested', 'deploying', 'deployed', 'completed'].includes(taskData.status)) {
      newEvents.push({
        id: 2,
        time: new Date(taskData.updated_at || taskData.created_at).toLocaleTimeString(),
        status: 'planning',
        title: '계획 수립 중',
        description: 'Agno 에이전트가 기능 구현 계획 작성',
        icon: '🔄'
      });
    }
    
    // 계획 완료 이벤트 (상태가 planned 이상인 경우)
    if (['planned', 'coding', 'coded', 'testing', 'tested', 'deploying', 'deployed', 'completed'].includes(taskData.status)) {
      newEvents.push({
        id: 3,
        time: new Date(taskData.updated_at || taskData.created_at).toLocaleTimeString(),
        status: 'planned',
        title: '계획 완료',
        description: taskData.plan_summary || '계획 수립 완료',
        icon: '📋'
      });
    }
    
    // 코딩 시작 이벤트 (상태가 coding 이상인 경우)
    if (['coding', 'coded', 'testing', 'tested', 'deploying', 'deployed', 'completed'].includes(taskData.status)) {
      newEvents.push({
        id: 4,
        time: new Date(taskData.updated_at || taskData.created_at).toLocaleTimeString(),
        status: 'coding',
        title: '코드 구현 중',
        description: 'Q Developer 에이전트가 코드 작성 시작',
        icon: '💻'
      });
    }
    
    // 코딩 완료 이벤트 (상태가 coded 이상인 경우)
    if (['coded', 'testing', 'tested', 'deploying', 'deployed', 'completed'].includes(taskData.status)) {
      const modifiedCount = taskData.modified_files ? taskData.modified_files.length : 0;
      const createdCount = taskData.created_files ? taskData.created_files.length : 0;
      
      newEvents.push({
        id: 5,
        time: new Date(taskData.updated_at || taskData.created_at).toLocaleTimeString(),
        status: 'coded',
        title: '코드 구현 완료',
        description: `${modifiedCount}개의 파일 수정 / ${createdCount}개의 파일 생성`,
        icon: '💾',
        details: {
          branch: taskData.branch_name,
          commit: taskData.commit_hash
        }
      });
    }
    
    // 테스트 시작 이벤트 (상태가 testing 이상인 경우)
    if (['testing', 'tested', 'deploying', 'deployed', 'completed'].includes(taskData.status)) {
      newEvents.push({
        id: 6,
        time: new Date(taskData.updated_at || taskData.created_at).toLocaleTimeString(),
        status: 'testing',
        title: '테스트 실행 중',
        description: '단위 테스트 진행',
        icon: '🧪'
      });
    }
    
    // 테스트 완료 이벤트 (상태가 tested 이상인 경우)
    if (['tested', 'deploying', 'deployed', 'completed'].includes(taskData.status)) {
      newEvents.push({
        id: 7,
        time: new Date(taskData.updated_at || taskData.created_at).toLocaleTimeString(),
        status: 'tested',
        title: '모든 테스트 통과',
        description: taskData.test_success ? '모든 테스트 통과' : '테스트 실패',
        icon: taskData.test_success ? '✅' : '❌'
      });
    }
    
    // 배포 시작 이벤트 (상태가 deploying 이상인 경우)
    if (['deploying', 'deployed', 'completed'].includes(taskData.status)) {
      newEvents.push({
        id: 8,
        time: new Date(taskData.updated_at || taskData.created_at).toLocaleTimeString(),
        status: 'deploying',
        title: '배포 중',
        description: 'PR 생성 및 메인 브랜치에 병합 시도',
        icon: '🚀'
      });
    }
    
    // 배포 완료 이벤트 (상태가 deployed 이상인 경우)
    if (['deployed', 'completed'].includes(taskData.status)) {
      newEvents.push({
        id: 9,
        time: new Date(taskData.updated_at || taskData.created_at).toLocaleTimeString(),
        status: 'deployed',
        title: '배포 완료',
        description: `PR이 메인에 머지되어 배포되었습니다`,
        icon: '🎉',
        details: {
          pr_url: taskData.pr_url,
          version: taskData.deployed_version,
          url: taskData.deployed_url
        }
      });
    }
    
    // 작업 완료 이벤트 (상태가 completed인 경우)
    if (taskData.status === 'completed') {
      newEvents.push({
        id: 10,
        time: new Date(taskData.completed_at || taskData.updated_at || taskData.created_at).toLocaleTimeString(),
        status: 'completed',
        title: '작업 완료',
        description: `작업이 성공적으로 완료되었습니다`,
        icon: '🎉'
      });
    }
    
    // 오류 이벤트 (상태가 error인 경우)
    if (taskData.status === 'error') {
      newEvents.push({
        id: 11,
        time: new Date(taskData.updated_at || taskData.created_at).toLocaleTimeString(),
        status: 'error',
        title: '오류 발생',
        description: taskData.error || '작업 처리 중 오류가 발생했습니다',
        icon: '⚠️'
      });
    }
    
    setEvents(newEvents);
  };

  // 작업 완료 시 리뷰 페이지로 이동
  useEffect(() => {
    if (task && (task.status === 'completed' || task.status === 'deployed')) {
      // 3초 후 리뷰 페이지로 자동 이동
      const timer = setTimeout(() => {
        navigate(`/tasks/${taskId}/review`);
      }, 3000);
      
      return () => clearTimeout(timer);
    }
  }, [task, taskId, navigate]);

  if (loading) {
    return <div className="loading">작업 정보를 불러오는 중...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  if (!task) {
    return <div className="error-message">작업을 찾을 수 없습니다.</div>;
  }

  return (
    <div className="task-monitoring-container">
      <h2>작업 진행 상황</h2>
      
      <div className="task-header">
        <div className="task-id">작업 ID: {taskId}</div>
        <div className="task-status">
          <span className="status-icon">{statusIcons[task.status] || '🔄'}</span>
          <span className="status-text">{task.status}</span>
        </div>
      </div>
      
      <div className="task-request">
        <h3>요청 내용:</h3>
        <p>{task.request}</p>
      </div>
      
      <div className="timeline">
        {events.map(event => (
          <div key={event.id} className={`timeline-item ${event.status}`}>
            <div className="timeline-icon">{event.icon}</div>
            <div className="timeline-content">
              <div className="timeline-time">{event.time}</div>
              <h4>{event.title}</h4>
              <p>{event.description}</p>
              
              {event.details && (
                <div className="timeline-details">
                  {event.details.branch && (
                    <div>브랜치: {event.details.branch}</div>
                  )}
                  {event.details.commit && (
                    <div>커밋: {event.details.commit.substring(0, 8)}</div>
                  )}
                  {event.details.pr_url && (
                    <div>
                      <a href={event.details.pr_url} target="_blank" rel="noopener noreferrer">
                        PR 보기
                      </a>
                    </div>
                  )}
                  {event.details.url && (
                    <div>
                      <a href={event.details.url} target="_blank" rel="noopener noreferrer">
                        배포 URL
                      </a>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
      
      {(task.status === 'completed' || task.status === 'deployed') && (
        <div className="completion-message">
          <p>작업이 완료되었습니다. 잠시 후 결과 확인 페이지로 이동합니다.</p>
          <button 
            onClick={() => navigate(`/tasks/${taskId}/review`)}
            className="review-button"
          >
            지금 결과 확인하기
          </button>
        </div>
      )}
    </div>
  );
}

export default TaskMonitoringPage;