import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import taskService from '../api/taskService';
import axios from '../api/axios';
import '../styles/TaskReviewPage.css';

function TaskReviewPage() {
  const { taskId } = useParams();
  const [task, setTask] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState('');

  // 작업 정보 가져오기
  useEffect(() => {
    const fetchTask = async () => {
      try {
        const response = await taskService.getTask(taskId);
        setTask(response.data);
        
        // 첫 번째 파일 선택 (있는 경우)
        if (response.data.modified_files && response.data.modified_files.length > 0) {
          setSelectedFile(response.data.modified_files[0]);
        } else if (response.data.created_files && response.data.created_files.length > 0) {
          setSelectedFile(response.data.created_files[0]);
        }
      } catch (err) {
        console.error('Error fetching task:', err);
        setError('작업 정보를 가져오는 중 오류가 발생했습니다.');
      } finally {
        setLoading(false);
      }
    };

    fetchTask();
  }, [taskId]);

  // 선택된 파일 내용 가져오기
  useEffect(() => {
    if (!selectedFile || !task) return;
    
    const fetchFileDiff = async () => {
      try {
        setFileContent('파일 내용을 불러오는 중...');
        
        // 파일 경로를 URL 인코딩하여 API 호출
        const encodedPath = encodeURIComponent(selectedFile);
        const response = await axios.get(`/api/tasks/${taskId}/diff/${encodedPath}`);
        setFileContent(response.data.diff);
      } catch (err) {
        console.error('Error fetching file diff:', err);
        setFileContent(`// ${selectedFile} 파일의 diff를 가져오는 중 오류가 발생했습니다.\n// ${err.message}`);
      }
    };
    
    fetchFileDiff();
  }, [selectedFile, taskId, task]);

  if (loading) {
    return <div className="loading">작업 정보를 불러오는 중...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  if (!task) {
    return <div className="error-message">작업을 찾을 수 없습니다.</div>;
  }

  // diff 텍스트에 하이라이트 적용
  const formatDiff = (diffText) => {
    if (!diffText) return '';
    
    // 줄 단위로 분할
    const lines = diffText.split('\n');
    
    // 각 줄에 하이라이트 적용
    return lines.map((line, index) => {
      if (line.startsWith('+') && !line.startsWith('+++')) {
        return <div key={index} className="diff-added">{line}</div>;
      } else if (line.startsWith('-') && !line.startsWith('---')) {
        return <div key={index} className="diff-removed">{line}</div>;
      } else if (line.startsWith('@@ ')) {
        return <div key={index} className="diff-chunk">{line}</div>;
      } else if (line.startsWith('diff ') || line.startsWith('index ') || 
                line.startsWith('--- ') || line.startsWith('+++ ')) {
        return <div key={index} className="diff-header">{line}</div>;
      } else {
        return <div key={index}>{line}</div>;
      }
    });
  };

  return (
    <div className="task-review-container">
      <h2>작업 결과 확인</h2>
      
      <div className="task-header">
        <div className="task-id">작업 ID: {taskId}</div>
        <div className="task-status">상태: {task.status}</div>
      </div>
      
      <div className="task-request">
        <h3>요청 내용:</h3>
        <p>{task.request}</p>
      </div>
      
      <div className="plan-summary">
        <h3>계획 요약:</h3>
        <p>{task.plan_summary || '계획 정보가 없습니다.'}</p>
        {task.plan_s3_key && (
          <button 
            className="view-details-button"
            onClick={async () => {
              try {
                const response = await axios.get(`/api/tasks/${taskId}/plan`);
                alert(JSON.stringify(response.data, null, 2));
              } catch (err) {
                console.error('Error fetching plan details:', err);
                alert('계획 상세 정보를 가져오는 중 오류가 발생했습니다.');
              }
            }}
          >
            계획 상세 보기
          </button>
        )}
      </div>
      
      <div className="code-review-section">
        <h3>코드 변경사항:</h3>
        
        <div className="code-review-container">
          <div className="file-list">
            {task.modified_files && task.modified_files.length > 0 && (
              <div className="file-group">
                <h4>수정된 파일:</h4>
                <ul>
                  {task.modified_files.map(file => (
                    <li 
                      key={file} 
                      className={selectedFile === file ? 'selected' : ''}
                      onClick={() => setSelectedFile(file)}
                    >
                      {file}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {task.created_files && task.created_files.length > 0 && (
              <div className="file-group">
                <h4>생성된 파일:</h4>
                <ul>
                  {task.created_files.map(file => (
                    <li 
                      key={file} 
                      className={selectedFile === file ? 'selected' : ''}
                      onClick={() => setSelectedFile(file)}
                    >
                      {file}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
          
          <div className="file-content">
            {selectedFile ? (
              <>
                <h4>{selectedFile}</h4>
                <div className="code-block">
                  {formatDiff(fileContent)}
                </div>
              </>
            ) : (
              <div className="no-file-selected">파일을 선택하세요</div>
            )}
          </div>
        </div>
      </div>
      
      <div className="test-results">
        <h3>테스트 결과:</h3>
        {task.test_success ? (
          <div className="test-success">
            ✅ 모든 테스트 통과
          </div>
        ) : (
          <div className="test-failure">
            ❌ 테스트 실패
            <p>{task.error || '자세한 오류 정보가 없습니다.'}</p>
          </div>
        )}
        {task.test_log_s3_key && (
          <button 
            className="view-details-button"
            onClick={async () => {
              try {
                const response = await axios.get(`/api/tasks/${taskId}/test-log`);
                alert(response.data.log);
              } catch (err) {
                console.error('Error fetching test log:', err);
                alert('테스트 로그를 가져오는 중 오류가 발생했습니다.');
              }
            }}
          >
            테스트 로그 보기
          </button>
        )}
      </div>
      
      {task.pr_url && (
        <div className="deployment-info">
          <h3>배포 정보:</h3>
          <div className="deployment-details">
            <p>
              <strong>Pull Request:</strong>{' '}
              <a href={task.pr_url} target="_blank" rel="noopener noreferrer">
                {task.pr_url}
              </a>
            </p>
            {task.deployed_version && (
              <p><strong>버전:</strong> {task.deployed_version}</p>
            )}
            {task.deployed_url && (
              <p>
                <strong>배포 URL:</strong>{' '}
                <a href={task.deployed_url} target="_blank" rel="noopener noreferrer">
                  {task.deployed_url}
                </a>
              </p>
            )}
          </div>
        </div>
      )}
      
      <div className="action-buttons">
        <button 
          onClick={() => window.location.href = '/tasks/new'}
          className="new-task-button"
        >
          새 작업 요청하기
        </button>
      </div>
    </div>
  );
}

export default TaskReviewPage;