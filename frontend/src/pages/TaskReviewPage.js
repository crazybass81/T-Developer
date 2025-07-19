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
        // 임시 처리: API 호출 대신 더미 데이터 사용
        // 실제 API가 준비되면 아래 주석을 해제하세요
        /*
        const response = await taskService.getTask(taskId);
        setTask(response.data);
        */
        
        // 더미 데이터
        const dummyTask = {
          task_id: taskId,
          request: '사용자가 질문을 입력하면 관련된 정부 지원사업을 검색하여 추천하는 기능을 추가해줘.',
          status: 'completed',
          created_at: new Date(Date.now() - 30000).toISOString(),
          updated_at: new Date().toISOString(),
          plan_summary: '정부 지원사업 검색 및 추천 기능 구현 계획',
          modified_files: ['src/services/searchService.js', 'src/controllers/chatController.js'],
          created_files: ['src/services/governmentSupportService.js'],
          branch_name: `feature/${taskId}`,
          commit_hash: 'abc123def456',
          test_success: true,
          pr_url: 'https://github.com/example/repo/pull/123',
          deployed_version: 'v1.0.0',
          deployed_url: 'https://example.com/app',
          plan_s3_key: 'plans/task-123-plan.json',
          test_log_s3_key: 'logs/task-123-test.log'
        };
        
        setTask(dummyTask);
        
        // 첫 번째 파일 선택 (있는 경우)
        if (dummyTask.modified_files && dummyTask.modified_files.length > 0) {
          setSelectedFile(dummyTask.modified_files[0]);
        } else if (dummyTask.created_files && dummyTask.created_files.length > 0) {
          setSelectedFile(dummyTask.created_files[0]);
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
        
        // 임시 처리: API 호출 대신 더미 데이터 사용
        // 실제 API가 준비되면 아래 주석을 해제하세요
        /*
        // 파일 경로를 URL 인코딩하여 API 호출
        const encodedPath = encodeURIComponent(selectedFile);
        const response = await axios.get(`/api/tasks/${taskId}/diff/${encodedPath}`);
        setFileContent(response.data.diff);
        */
        
        // 더미 diff 데이터
        let dummyDiff = '';
        
        if (selectedFile === 'src/services/searchService.js') {
          dummyDiff = `diff --git a/src/services/searchService.js b/src/services/searchService.js
index 1234567..abcdefg 100644
--- a/src/services/searchService.js
+++ b/src/services/searchService.js
@@ -10,6 +10,7 @@ class SearchService {
   constructor() {
     this.db = database.getConnection();
     this.logger = new Logger('SearchService');
+    this.govSupportService = new GovernmentSupportService();
   }

   /**
@@ -25,6 +26,25 @@ class SearchService {
     return results;
   }

+  /**
+   * 사용자 질문에 관련된 정부 지원사업을 검색합니다.
+   * @param {string} query - 사용자 질문
+   * @param {number} limit - 최대 결과 수 (기본값: 3)
+   * @returns {Array} 관련 지원사업 목록
+   */
+  async searchGovernmentSupport(query, limit = 3) {
+    this.logger.info(\`정부 지원사업 검색: \${query}\`);
+    
+    // 키워드 추출 및 정부 지원사업 검색
+    const keywords = await this.extractKeywords(query);
+    const supportPrograms = await this.govSupportService.findByKeywords(keywords, limit);
+    
+    this.logger.info(\`검색 결과: \${supportPrograms.length}개 지원사업 발견\`);
+    
+    return supportPrograms;
+  }
+
   /**
    * 검색 결과를 사용자 선호도에 따라 정렬합니다.
    * @param {Array} results - 검색 결과 배열`;
        } else if (selectedFile === 'src/controllers/chatController.js') {
          dummyDiff = `diff --git a/src/controllers/chatController.js b/src/controllers/chatController.js
index 9876543..fedcba0 100644
--- a/src/controllers/chatController.js
+++ b/src/controllers/chatController.js
@@ -2,6 +2,7 @@ const ChatService = require('../services/chatService');
 const UserService = require('../services/userService');
 const ResponseFormatter = require('../utils/responseFormatter');
 const SearchService = require('../services/searchService');
+const { SUPPORT_PROGRAM_INTENT } = require('../constants/intents');

 class ChatController {
   constructor() {
@@ -35,6 +36,21 @@ class ChatController {
     }
   }

+  /**
+   * 정부 지원사업 추천 처리
+   */
+  async handleSupportProgramRecommendation(req, res) {
+    try {
+      const { query } = req.body;
+      const searchService = new SearchService();
+      const programs = await searchService.searchGovernmentSupport(query);
+      
+      return res.json(ResponseFormatter.success(programs));
+    } catch (error) {
+      this.logger.error(\`지원사업 추천 오류: \${error.message}\`);
+      return res.status(500).json(ResponseFormatter.error('지원사업 검색 중 오류가 발생했습니다'));
+    }
+  }
+
   /**
    * 사용자 메시지 처리
    */
@@ -48,6 +64,11 @@ class ChatController {
       // 의도 분석
       const intent = await this.chatService.analyzeIntent(message);
       
+      // 정부 지원사업 검색 의도인 경우
+      if (intent === SUPPORT_PROGRAM_INTENT) {
+        return await this.handleSupportProgramRecommendation(req, res);
+      }
+      
       // 일반 대화 처리
       const response = await this.chatService.generateResponse(message, userId);`;
        } else if (selectedFile === 'src/services/governmentSupportService.js') {
          dummyDiff = `diff --git a/src/services/governmentSupportService.js b/src/services/governmentSupportService.js
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/src/services/governmentSupportService.js
@@ -0,0 +1,62 @@
+/**
+ * 정부 지원사업 검색 및 추천 서비스
+ */
+const database = require('../config/database');
+const Logger = require('../utils/logger');
+
+class GovernmentSupportService {
+  constructor() {
+    this.db = database.getConnection();
+    this.logger = new Logger('GovernmentSupportService');
+    this.collection = 'government_support_programs';
+  }
+
+  /**
+   * 키워드 기반으로 관련 정부 지원사업을 검색합니다.
+   * @param {Array} keywords - 검색 키워드 배열
+   * @param {number} limit - 최대 결과 수
+   * @returns {Array} 지원사업 목록
+   */
+  async findByKeywords(keywords, limit = 3) {
+    this.logger.info(\`키워드로 지원사업 검색: \${keywords.join(', ')}\`);
+    
+    try {
+      // 키워드 기반 검색 쿼리 구성
+      const query = {
+        $or: keywords.map(keyword => ({
+          $or: [
+            { title: { $regex: keyword, $options: 'i' } },
+            { description: { $regex: keyword, $options: 'i' } },
+            { target: { $regex: keyword, $options: 'i' } },
+            { tags: { $in: [keyword] } }
+          ]
+        }))
+      };
+      
+      // 데이터베이스 검색 실행
+      const programs = await this.db.collection(this.collection)
+        .find(query)
+        .sort({ relevance: -1, deadline: 1 })
+        .limit(limit)
+        .toArray();
+      
+      return programs.map(program => ({
+        id: program._id,
+        title: program.title,
+        organization: program.organization,
+        description: program.description,
+        eligibility: program.eligibility,
+        benefits: program.benefits,
+        deadline: program.deadline,
+        applicationUrl: program.applicationUrl,
+        contactInfo: program.contactInfo
+      }));
+    } catch (error) {
+      this.logger.error(\`지원사업 검색 오류: \${error.message}\`);
+      throw new Error(\`정부 지원사업 검색 중 오류 발생: \${error.message}\`);
+    }
+  }
+}
+
+module.exports = GovernmentSupportService;`;
        } else {
          dummyDiff = `// ${selectedFile} 파일의 diff 내용이 준비되지 않았습니다.`;
        }
        
        setFileContent(dummyDiff);
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
            onClick={() => alert('계획 상세 보기 기능은 아직 구현되지 않았습니다.')}
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
            onClick={() => alert('테스트 로그 보기 기능은 아직 구현되지 않았습니다.')}
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