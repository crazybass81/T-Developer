import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';
import '../styles/ProjectCreationPage.css';

function ProjectCreationPage() {
  const navigate = useNavigate();
  const [projectData, setProjectData] = useState({
    name: '',
    description: '',
    githubRepo: '',
    slackChannel: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState({
    github: false,
    slack: false
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setProjectData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // 연결 상태 초기화 (값이 변경되면)
    if (name === 'githubRepo' && connectionStatus.github) {
      setConnectionStatus(prev => ({ ...prev, github: false }));
    } else if (name === 'slackChannel' && connectionStatus.slack) {
      setConnectionStatus(prev => ({ ...prev, slack: false }));
    }
  };
  
  const handleConnect = (type) => {
    if (type === 'github') {
      if (!projectData.githubRepo.trim()) {
        alert('GitHub 저장소 URL을 입력해주세요.');
        return;
      }
      
      // GitHub 저장소 형식 검증 (간단한 검증)
      const githubRegex = /^(https?:\/\/)?(www\.)?github\.com\/[\w.-]+\/[\w.-]+$/;
      if (!githubRegex.test(projectData.githubRepo)) {
        alert('유효한 GitHub 저장소 URL을 입력해주세요. (예: github.com/username/repo)');
        return;
      }
      
      setConnectionStatus(prev => ({ ...prev, github: true }));
      alert(`GitHub 저장소 "${projectData.githubRepo}"가 연결되었습니다.`);
    } else if (type === 'slack') {
      if (!projectData.slackChannel.trim()) {
        alert('Slack 채널을 입력해주세요.');
        return;
      }
      
      // Slack 채널 형식 검증 (간단한 검증)
      const slackRegex = /^#[\w-]+$/;
      if (!slackRegex.test(projectData.slackChannel)) {
        alert('유효한 Slack 채널 이름을 입력해주세요. (예: #channel-name)');
        return;
      }
      
      setConnectionStatus(prev => ({ ...prev, slack: true }));
      alert(`Slack 채널 "${projectData.slackChannel}"이 연결되었습니다.`);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // GitHub와 Slack 연결 상태 확인
      if (!connectionStatus.github) {
        alert('GitHub 저장소를 연결해주세요.');
        setLoading(false);
        return;
      }
      
      if (!connectionStatus.slack) {
        alert('Slack 채널을 연결해주세요.');
        setLoading(false);
        return;
      }
      
      console.log('Submitting to API:', api.defaults.baseURL + '/api/projects');
      
      // 임시 처리: API 호출 없이 다음 페이지로 이동
      // 실제 API가 준비되면 아래 주석을 해제하세요
      /*
      const response = await api.post('/api/projects', {
        name: projectData.name,
        description: projectData.description,
        github_repo: projectData.githubRepo,
        slack_channel: projectData.slackChannel
      });
      
      console.log('Project created:', response.data);
      */
      
      // 프로젝트 생성 후 작업 생성 페이지로 이동
      navigate('/tasks/new');
    } catch (err) {
      console.error('Error creating project:', err);
      setError('프로젝트 생성 중 오류가 발생했습니다. 다시 시도해주세요.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="project-creation-container">
      <h2>새 프로젝트 생성</h2>
      
      {error && <div className="error-message">{error}</div>}
      
      <form onSubmit={handleSubmit} className="project-form">
        <div className="form-group">
          <label htmlFor="name">프로젝트 이름</label>
          <input
            type="text"
            id="name"
            name="name"
            value={projectData.name}
            onChange={handleChange}
            required
            placeholder="예: GovChat"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="description">프로젝트 설명</label>
          <textarea
            id="description"
            name="description"
            value={projectData.description}
            onChange={handleChange}
            required
            placeholder="예: 정부지원사업 매칭 챗봇 프로젝트"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="githubRepo">GitHub 저장소</label>
          <div className="input-with-button">
            <input
              type="text"
              id="githubRepo"
              name="githubRepo"
              value={projectData.githubRepo}
              onChange={handleChange}
              required
              placeholder="예: github.com/사용자/govchat"
            />
            <button 
              type="button" 
              className={`connect-button ${connectionStatus.github ? 'connected' : ''}`}
              onClick={() => handleConnect('github')}
              title="GitHub 저장소 연결 확인"
            >
              {connectionStatus.github ? '✓ 연결됨' : '연결'}
            </button>
          </div>
          {connectionStatus.github && <div className="connection-info">GitHub 저장소가 연결되었습니다.</div>}
        </div>
        
        <div className="form-group">
          <label htmlFor="slackChannel">Slack 채널</label>
          <div className="input-with-button">
            <input
              type="text"
              id="slackChannel"
              name="slackChannel"
              value={projectData.slackChannel}
              onChange={handleChange}
              required
              placeholder="예: #govchat-dev"
            />
            <button 
              type="button" 
              className={`connect-button ${connectionStatus.slack ? 'connected' : ''}`}
              onClick={() => handleConnect('slack')}
              title="Slack 채널 연결 확인"
            >
              {connectionStatus.slack ? '✓ 연결됨' : '연결'}
            </button>
          </div>
          {connectionStatus.slack && <div className="connection-info">Slack 채널이 연결되었습니다.</div>}
        </div>
        
        <button 
          type="submit" 
          className="submit-button"
          disabled={loading || !connectionStatus.github || !connectionStatus.slack}
        >
          {loading ? '생성 중...' : '프로젝트 생성'}
        </button>
      </form>
    </div>
  );
}

export default ProjectCreationPage;