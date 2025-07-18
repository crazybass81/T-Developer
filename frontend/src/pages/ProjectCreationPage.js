import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
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

  const handleChange = (e) => {
    const { name, value } = e.target;
    setProjectData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // API 호출 - 프로젝트 생성 API 호출
      const response = await axios.post('/api/projects', {
        name: projectData.name,
        description: projectData.description,
        github_repo: projectData.githubRepo,
        slack_channel: projectData.slackChannel
      });
      
      console.log('Project created:', response.data);
      
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
            <button type="button" className="connect-button">연결</button>
          </div>
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
            <button type="button" className="connect-button">연결</button>
          </div>
        </div>
        
        <button 
          type="submit" 
          className="submit-button"
          disabled={loading}
        >
          {loading ? '생성 중...' : '프로젝트 생성'}
        </button>
      </form>
    </div>
  );
}

export default ProjectCreationPage;