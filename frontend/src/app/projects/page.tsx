'use client';

import { useState, useEffect } from 'react';

interface Project {
  project_id: string;
  status: string;
  created_at: string;
  input: string;
  download_url?: string;
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);

  const fetchProjects = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/projects');
      const data = await response.json();
      setProjects(data.projects || []);
    } catch (error) {
      console.error('Failed to fetch projects:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleGenerate = async () => {
    if (!input.trim()) return;

    setGenerating(true);
    try {
      const response = await fetch('http://localhost:8000/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          input,
          requirements: {},
          options: {}
        }),
      });

      if (response.ok) {
        const result = await response.json();
        alert(`프로젝트 생성 완료! ID: ${result.project_id}`);
        setInput('');
        fetchProjects();
      } else {
        alert('프로젝트 생성 실패');
      }
    } catch (error) {
      console.error('Generation error:', error);
      alert('프로젝트 생성 중 오류 발생');
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = (projectId: string) => {
    window.open(`http://localhost:8000/download/${projectId}`, '_blank');
  };

  const handleDelete = async (projectId: string) => {
    if (!confirm('정말 삭제하시겠습니까?')) return;

    try {
      const response = await fetch(`http://localhost:8000/projects/${projectId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        fetchProjects();
      }
    } catch (error) {
      console.error('Delete error:', error);
    }
  };

  return (
    <div className="min-h-screen p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold">📦 Project Generator</h1>
        <p className="text-gray-600 mt-2">AI가 자동으로 전체 프로젝트를 생성합니다</p>
      </header>

      {/* Generation Form */}
      <div className="max-w-4xl mx-auto mb-8">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">새 프로젝트 생성</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                프로젝트 설명 (자연어로 입력)
              </label>
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="예: React로 간단한 Todo 앱 만들어줘. 로컬 스토리지에 데이터 저장하고 다크모드 지원해줘."
                className="w-full p-3 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                rows={4}
              />
            </div>

            <button
              onClick={handleGenerate}
              disabled={generating || !input.trim()}
              className="w-full py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 transition-colors font-semibold"
            >
              {generating ? '🔄 생성 중...' : '🚀 프로젝트 생성'}
            </button>
          </div>

          {/* Pipeline Steps */}
          <div className="mt-6 p-4 bg-gray-100 dark:bg-gray-900 rounded-lg">
            <h3 className="text-sm font-semibold mb-2">생성 파이프라인</h3>
            <div className="flex flex-wrap gap-2">
              {[
                '1. NL Input',
                '2. UI Selection',
                '3. Parser',
                '4. Component',
                '5. Match Rate',
                '6. Search',
                '7. Generation',
                '8. Assembly',
                '9. Download'
              ].map((step) => (
                <span
                  key={step}
                  className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded text-xs"
                >
                  {step}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Projects List */}
      <div className="max-w-6xl mx-auto">
        <h2 className="text-2xl font-semibold mb-4">생성된 프로젝트</h2>

        {loading ? (
          <div className="text-center py-8">Loading...</div>
        ) : projects.length === 0 ? (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 text-center">
            <p className="text-gray-500">아직 생성된 프로젝트가 없습니다</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {projects.map((project) => (
              <div
                key={project.project_id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold">Project ID: {project.project_id.slice(0, 8)}...</h3>
                      <span
                        className={`px-2 py-1 rounded text-xs ${
                          project.status === 'completed'
                            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                            : project.status === 'processing'
                            ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                            : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                        }`}
                      >
                        {project.status}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                      {project.input}
                    </p>
                    <p className="text-xs text-gray-500">
                      생성 시간: {new Date(project.created_at).toLocaleString()}
                    </p>
                  </div>

                  <div className="flex gap-2">
                    {project.status === 'completed' && (
                      <button
                        onClick={() => handleDownload(project.project_id)}
                        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                      >
                        📥 다운로드
                      </button>
                    )}
                    <button
                      onClick={() => handleDelete(project.project_id)}
                      className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                    >
                      🗑️ 삭제
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
