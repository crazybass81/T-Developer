import React, { useState, useEffect } from 'react';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL || window.location.origin;

interface AgentStep {
  id: number;
  name: string;
  status: 'waiting' | 'active' | 'completed';
}

function App() {
  const [query, setQuery] = useState('');
  const [framework, setFramework] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
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

    const progressInterval = simulateProgress();

    try {
      const response = await fetch(`${API_URL}/api/v1/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          query: query.trim(),
          framework: framework || undefined 
        }),
      });

      const data = await response.json();

      if (data.status === 'success') {
        setResult(data);
        // 모든 단계 완료 표시
        setAgentSteps(prev => 
          prev.map(step => ({ ...step, status: 'completed' }))
        );
      } else {
        setError(data.message || '요청 처리 중 오류가 발생했습니다.');
        clearInterval(progressInterval);
        resetSteps();
      }
    } catch (err: any) {
      console.error('Error:', err);
      setError('서버와의 연결에 실패했습니다.');
      clearInterval(progressInterval);
      resetSteps();
    } finally {
      setLoading(false);
    }
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

  // 컴포넌트 마운트 시 서버 상태 확인
  useEffect(() => {
    const checkServerHealth = async () => {
      try {
        const response = await fetch(`${API_URL}/health`);
        const data = await response.json();
        console.log('Server status:', data);
      } catch (error) {
        console.error('Server not available:', error);
      }
    };
    
    checkServerHealth();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>🤖 T-Developer</h1>
        <p>자연어로 완전한 프로젝트를 생성하는 AI 개발 도우미</p>
        <div className="tech-badges">
          <span className="badge">🧠 9-Agent Pipeline</span>
          <span className="badge">⚡ 실시간 생성</span>
          <span className="badge">📦 즉시 다운로드</span>
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
                  <div className="step-name">{step.name}</div>
                  <div className="step-status">
                    {step.status === 'completed' && <span>✅</span>}
                    {step.status === 'active' && <div className="step-spinner"></div>}
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
                  href={`${API_URL}${result.result?.downloadUrl}`}
                  download
                  className="download-btn"
                  onClick={() => handleDownload(result.result?.downloadUrl)}
                >
                  📦 ZIP 파일 다운로드
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