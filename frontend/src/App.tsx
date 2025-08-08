import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL || window.location.origin;
const WS_URL = API_URL.replace('http', 'ws');

interface AgentStep {
  id: number;
  name: string;
  status: 'waiting' | 'active' | 'completed' | 'error';
  progress?: number;
  message?: string;
  timestamp?: string;
}

interface GenerationProgress {
  step: number;
  stepName: string;
  progress: number;
  message: string;
  timestamp: string;
}

function App() {
  const [query, setQuery] = useState('');
  const [framework, setFramework] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connected' | 'error'>('disconnected');
  const wsRef = useRef<WebSocket | null>(null);
  const [currentProjectId, setCurrentProjectId] = useState<string | null>(null);
  const [agentSteps, setAgentSteps] = useState<AgentStep[]>([
    { id: 1, name: '자연어 분석 중...', status: 'waiting' },
    { id: 2, name: 'UI 기술 스택 선택 중...', status: 'waiting' },
    { id: 3, name: '프로젝트 구조 파싱 중...', status: 'waiting' },
    { id: 4, name: '컴포넌트 설계 중...', status: 'waiting' },
    { id: 5, name: '매칭률 계산 중...', status: 'waiting' },
    { id: 6, name: '코드 템플릿 검색 중...', status: 'waiting' },
    { id: 7, name: '프로젝트 코드 생성 중...', status: 'waiting' },
    { id: 8, name: '프로젝트 조립 및 검증 중...', status: 'waiting' },
    { id: 9, name: '다운로드 패키지 생성 중...', status: 'waiting' },
  ]);

  const exampleQueries = [
    'Todo 앱을 만들어줘',
    '블로그 웹사이트를 만들어줘',
    'QR코드 근태관리 시스템',
    '이커머스 쇼핑몰을 만들어줘',
    '대시보드를 만들어줘',
    '채팅 앱을 만들어줘'
  ];

  // WebSocket 연결 관리
  const connectWebSocket = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      wsRef.current = new WebSocket(`${WS_URL}/ws`);
      
      wsRef.current.onopen = () => {
        console.log('WebSocket connected');
        setConnectionStatus('connected');
      };

      wsRef.current.onmessage = (event) => {
        try {
          const data: GenerationProgress = JSON.parse(event.data);
          updateAgentStep(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      wsRef.current.onclose = () => {
        console.log('WebSocket disconnected');
        setConnectionStatus('disconnected');
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('error');
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      setConnectionStatus('error');
    }
  };

  // Agent 단계 업데이트
  const updateAgentStep = (progress: GenerationProgress) => {
    setAgentSteps(prev => 
      prev.map(step => {
        if (step.id === progress.step) {
          return {
            ...step,
            status: progress.progress === 100 ? 'completed' : 'active',
            progress: progress.progress,
            message: progress.message,
            timestamp: progress.timestamp
          };
        } else if (step.id < progress.step) {
          return { ...step, status: 'completed', progress: 100 };
        }
        return step;
      })
    );
  };

  const simulateProgress = () => {
    let currentStep = 0;
    const interval = setInterval(() => {
      if (currentStep < agentSteps.length) {
        setAgentSteps(prev => 
          prev.map(step => {
            if (step.id === currentStep + 1) {
              return { ...step, status: 'active' };
            } else if (step.id < currentStep + 1) {
              return { ...step, status: 'completed' };
            }
            return step;
          })
        );
        currentStep++;
      } else {
        setAgentSteps(prev => 
          prev.map(step => ({ ...step, status: 'completed' }))
        );
        clearInterval(interval);
      }
    }, 400);
    
    return interval;
  };

  const resetSteps = () => {
    setAgentSteps(prev => 
      prev.map(step => ({ ...step, status: 'waiting' }))
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('프로젝트 설명을 입력해주세요.');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);
    resetSteps();

    // WebSocket 연결 확인
    connectWebSocket();

    try {
      const response = await fetch(`${API_URL}/api/v1/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          user_input: query.trim(),
          project_name: `project_${Date.now()}`,
          project_type: framework || 'react',
          features: extractFeatures(query.trim())
        }),
      });

      const data = await response.json();

      if (data.success) {
        setResult(data);
        setCurrentProjectId(data.project_id);
        // 모든 단계 완료 표시
        setAgentSteps(prev => 
          prev.map(step => ({ ...step, status: 'completed' }))
        );
      } else {
        setError(data.detail || '요청 처리 중 오류가 발생했습니다.');
        resetSteps();
      }
    } catch (err: any) {
      console.error('Error:', err);
      setError(`서버와의 연결에 실패했습니다: ${err.message}`);
      resetSteps();
    } finally {
      setLoading(false);
    }
  };

  // 특성 추출 헬퍼 함수
  const extractFeatures = (query: string): string[] => {
    const features = [];
    const queryLower = query.toLowerCase();
    
    if (queryLower.includes('todo') || queryLower.includes('할일')) {
      features.push('todo');
    }
    if (queryLower.includes('로그인') || queryLower.includes('인증')) {
      features.push('auth');
    }
    if (queryLower.includes('라우팅') || queryLower.includes('페이지')) {
      features.push('routing');
    }
    if (queryLower.includes('상태관리') || queryLower.includes('redux')) {
      features.push('state-management');
    }
    
    return features;
  };

  const handleExampleClick = (exampleQuery: string) => {
    setQuery(exampleQuery);
  };

  const handleDownload = (downloadUrl: string) => {
    // 다운로드 추적 및 사용자 알림
    setTimeout(() => {
      alert('다운로드가 시작됩니다. ZIP 파일을 받은 후 압축을 해제하여 프로젝트를 사용하세요!');
    }, 100);
  };

  // 컴포넌트 마운트 시 서버 상태 확인 및 WebSocket 연결
  useEffect(() => {
    const checkServerHealth = async () => {
      try {
        const response = await fetch(`${API_URL}/health`);
        const data = await response.json();
        console.log('Server status:', data);
        
        // 서버가 정상이면 WebSocket 연결 시도
        connectWebSocket();
      } catch (error) {
        console.error('Server not available:', error);
      }
    };
    
    checkServerHealth();

    // 컴포넌트 언마운트 시 WebSocket 연결 해제
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // 연결 상태에 따른 재연결 시도
  useEffect(() => {
    let reconnectTimeout: NodeJS.Timeout;

    if (connectionStatus === 'disconnected' || connectionStatus === 'error') {
      reconnectTimeout = setTimeout(() => {
        console.log('Attempting to reconnect WebSocket...');
        connectWebSocket();
      }, 5000);
    }

    return () => {
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
    };
  }, [connectionStatus]);

  return (
    <div className="App">
      <header className="App-header">
        <h1>🤖 T-Developer</h1>
        <p>자연어로 완전한 프로젝트를 생성하는 AI 개발 도우미</p>
        <div className="tech-badges">
          <span className="badge">🧠 9-Agent Pipeline</span>
          <span className="badge">⚡ 실시간 생성</span>
          <span className="badge">📦 즉시 다운로드</span>
          <span className={`connection-status ${connectionStatus}`}>
            {connectionStatus === 'connected' && '🟢 실시간 연결'}
            {connectionStatus === 'disconnected' && '🟡 연결 중...'}
            {connectionStatus === 'error' && '🔴 연결 오류'}
          </span>
        </div>
      </header>

      <main className="main-content">
        <form onSubmit={handleSubmit} className="project-form">
          <div className="form-group">
            <label htmlFor="query">어떤 프로젝트를 만들고 싶나요?</label>
            <textarea
              id="query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="예: QR코드 기반 근태관리 시스템을 만들어줘. 직원이 QR 스캔하면 출퇴근 시간이 데이터베이스에 기록되도록

또는

블로그 웹사이트를 만들어줘. 글 작성, 수정, 삭제가 가능하고 로그인 기능도 필요해"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="framework">선호하는 프레임워크 (선택사항)</label>
            <select
              id="framework"
              value={framework}
              onChange={(e) => setFramework(e.target.value)}
            >
              <option value="">자동 선택</option>
              <option value="react">React</option>
              <option value="vue">Vue.js</option>
              <option value="nextjs">Next.js</option>
              <option value="angular">Angular</option>
            </select>
          </div>

          <button type="submit" disabled={loading} className="generate-btn">
            {loading ? (
              <>
                <div className="spinner"></div>
                AI가 프로젝트를 생성하고 있습니다...
              </>
            ) : (
              '프로젝트 생성하기'
            )}
          </button>
        </form>

        {/* 예제 프로젝트 */}
        <div className="examples-section">
          <h3>예제 프로젝트</h3>
          <div className="example-tags">
            {exampleQueries.map((example, index) => (
              <button
                key={index}
                className="example-tag"
                onClick={() => handleExampleClick(example)}
                type="button"
              >
                {example}
              </button>
            ))}
          </div>
        </div>

        {/* 진행 단계 */}
        {loading && (
          <div className="progress-section">
            <h3>9-Agent Pipeline 진행 상황</h3>
            <div className="progress-steps">
              {agentSteps.map(step => (
                <div key={step.id} className={`progress-step ${step.status}`}>
                  <div className="step-number">{step.id}</div>
                  <div className="step-content">
                    <div className="step-name">{step.name}</div>
                    {step.message && (
                      <div className="step-message">{step.message}</div>
                    )}
                    {step.progress !== undefined && step.status === 'active' && (
                      <div className="progress-bar">
                        <div 
                          className="progress-fill" 
                          style={{ width: `${step.progress}%` }}
                        ></div>
                      </div>
                    )}
                    {step.timestamp && (
                      <div className="step-timestamp">{new Date(step.timestamp).toLocaleTimeString()}</div>
                    )}
                  </div>
                  <div className="step-status">
                    {step.status === 'completed' && <span>✅</span>}
                    {step.status === 'active' && <div className="step-spinner"></div>}
                    {step.status === 'error' && <span>❌</span>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {error && (
          <div className="error-message">
            <strong>오류:</strong> {error}
          </div>
        )}

        {result && (
          <div className="result-container">
            <div className="result-header">
              <h2>프로젝트 생성 완료!</h2>
            </div>
            
            <div className="result-grid">
              <div className="result-item">
                <div className="label">프로젝트명</div>
                <div className="value">{result.projectName}</div>
              </div>
              <div className="result-item">
                <div className="label">프레임워크</div>
                <div className="value">{result.framework}</div>
              </div>
              <div className="result-item">
                <div className="label">총 파일 수</div>
                <div className="value">{result.result?.totalFiles}</div>
              </div>
              <div className="result-item">
                <div className="label">품질 점수</div>
                <div className="value">
                  {result.result?.qualityScore ? Math.round(result.result.qualityScore) + '/100' : 'N/A'}
                </div>
              </div>
              <div className="result-item">
                <div className="label">패키지 크기</div>
                <div className="value">{result.result?.packageSize}</div>
              </div>
              <div className="result-item">
                <div className="label">예상 설치 시간</div>
                <div className="value">{result.result?.estimatedInstallTime}</div>
              </div>
            </div>

            <div className="download-section">
              <h3>프로젝트 다운로드</h3>
              <p>완전한 프로젝트가 준비되었습니다. ZIP 파일을 다운로드하여 즉시 사용하세요!</p>
              <div className="download-info">
                <div className="download-stats">
                  <div className="stat">
                    <span>{result.result?.totalFiles}개 파일</span>
                  </div>
                  <div className="stat">
                    <span>{result.result?.validationScore}% 검증</span>
                  </div>
                  <div className="stat">
                    <span>{Math.round(result.result?.qualityScore || 0)}/100 품질</span>
                  </div>
                </div>
                <a 
                  href={`${API_URL}${result.download_url}`}
                  download
                  className="download-btn"
                  onClick={() => handleDownload(result.download_url)}
                >
                  📦 ZIP 파일 다운로드 ({result.project_id}.zip)
                </a>
              </div>
              
              {result.result?.buildCommands && (
                <div className="build-instructions">
                  <h4>설치 가이드</h4>
                  <ol>
                    {result.result.buildCommands.map((cmd: string, index: number) => (
                      <li key={index}>{cmd}</li>
                    ))}
                  </ol>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App;