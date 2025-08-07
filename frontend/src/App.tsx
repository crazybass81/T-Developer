import React, { useState } from 'react';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Framework {
  id: string;
  name: string;
  version: string;
}

function App() {
  const [query, setQuery] = useState('');
  const [selectedFramework, setSelectedFramework] = useState('auto-detect');
  const [frameworks, setFrameworks] = useState<Framework[]>([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  // Fetch frameworks on component mount
  React.useEffect(() => {
    fetchFrameworks();
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const response = await fetch(`${API_URL}/health`);
      const data = await response.json();
      console.log('Server health:', data);
    } catch (err) {
      console.error('Server is not responding:', err);
      setError('서버에 연결할 수 없습니다. 백엔드 서버를 실행해주세요.');
    }
  };

  const fetchFrameworks = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/frameworks`);
      const data = await response.json();
      setFrameworks(data.frameworks || []);
    } catch (err) {
      console.error('Failed to fetch frameworks:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('자연어로 만들고 싶은 기능을 입력해주세요.');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/api/v1/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          framework: selectedFramework !== 'auto-detect' ? selectedFramework : undefined
        })
      });

      if (!response.ok) {
        throw new Error('요청 처리 중 오류가 발생했습니다.');
      }

      const data = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || '알 수 없는 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🚀 T-Developer</h1>
        <p>자연어로 웹 애플리케이션을 만들어보세요</p>
      </header>

      <main className="app-main">
        <form onSubmit={handleSubmit} className="input-form">
          <div className="form-group">
            <label htmlFor="query">무엇을 만들고 싶으신가요?</label>
            <textarea
              id="query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="예: 사용자 로그인과 회원가입이 가능한 대시보드를 만들어줘"
              rows={4}
              className="query-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="framework">프레임워크 선택 (선택사항)</label>
            <select
              id="framework"
              value={selectedFramework}
              onChange={(e) => setSelectedFramework(e.target.value)}
              className="framework-select"
            >
              <option value="auto-detect">자동 선택</option>
              {frameworks.map((fw) => (
                <option key={fw.id} value={fw.id}>
                  {fw.name} ({fw.version})
                </option>
              ))}
            </select>
          </div>

          <button 
            type="submit" 
            disabled={loading || !query.trim()}
            className="submit-button"
          >
            {loading ? '처리 중...' : '생성하기'}
          </button>
        </form>

        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}

        {result && (
          <div className="result-container">
            <h2>처리 결과</h2>
            <div className="result-content">
              <p><strong>상태:</strong> {result.status}</p>
              <p><strong>입력:</strong> {result.query}</p>
              <p><strong>프레임워크:</strong> {result.framework}</p>
              {result.result && (
                <div className="result-details">
                  <h3>분석 결과</h3>
                  <p><strong>컴포넌트:</strong> {result.result.components?.join(', ')}</p>
                  <p><strong>예상 시간:</strong> {result.result.estimatedTime}</p>
                  <p><strong>신뢰도:</strong> {(result.result.confidence * 100).toFixed(0)}%</p>
                </div>
              )}
              <pre className="json-output">
                {JSON.stringify(result, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>© 2024 T-Developer | AWS Bedrock Agent 기반 AI 개발 플랫폼</p>
      </footer>
    </div>
  );
}

export default App;