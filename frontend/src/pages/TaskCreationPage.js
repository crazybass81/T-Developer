import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import taskService from '../api/taskService';
import '../styles/TaskCreationPage.css';

function TaskCreationPage() {
  const navigate = useNavigate();
  const [request, setRequest] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState('');

  // 프로젝트 목록 가져오기
  useEffect(() => {
    const fetchProjects = async () => {
      try {
        // 실제 API 호출
        const response = await taskService.getProjects();
        setProjects(response.data);
        if (response.data.length > 0) {
          setSelectedProject(response.data[0].project_id);
        }
      } catch (err) {
        console.error('Error fetching projects:', err);
        setError('프로젝트 목록을 가져오는 중 오류가 발생했습니다.');
        
        // API 오류 시 더미 데이터 사용 (테스트용)
        const dummyProjects = [
          { project_id: 'PROJ-DEFAULT', name: 'GovChat' },
          { project_id: 'proj-2', name: '테스트 프로젝트' }
        ];
        setProjects(dummyProjects);
        setSelectedProject('PROJ-DEFAULT');
      }
    };
    
    fetchProjects();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // 실제 API 호출
      const response = await taskService.createTask({
        request,
        user_id: 'web-user', // 실제 구현에서는 인증된 사용자 ID 사용
        project_id: selectedProject
      });
      
      // 작업 ID를 받아 모니터링 페이지로 이동
      const taskId = response.data.task_id;
      console.log('Task created:', { task_id: taskId, request, project_id: selectedProject });
      
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
          <label htmlFor="project">프로젝트 선택</label>
          <select
            id="project"
            value={selectedProject}
            onChange={(e) => setSelectedProject(e.target.value)}
            required
          >
            {projects.length === 0 ? (
              <option value="">프로젝트가 없습니다</option>
            ) : (
              projects.map(project => (
                <option key={project.project_id} value={project.project_id}>
                  {project.name}
                </option>
              ))
            )}
          </select>
          {projects.length === 0 && (
            <div className="form-hint">
              <a href="/">프로젝트를 먼저 생성해주세요</a>
            </div>
          )}
        </div>
        
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