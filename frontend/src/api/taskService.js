import api from './axios';

// 작업 관련 API 서비스
const taskService = {
  // 작업 생성
  createTask: (data) => {
    return api.post('/api/tasks', data);
  },
  
  // 작업 조회
  getTask: (taskId) => {
    return api.get(`/api/tasks/${taskId}`);
  },
  
  // 프로젝트 목록 조회
  getProjects: () => {
    return api.get('/api/projects');
  },
  
  // 프로젝트 생성
  createProject: (data) => {
    return api.post('/api/projects', data);
  }
};

export default taskService;