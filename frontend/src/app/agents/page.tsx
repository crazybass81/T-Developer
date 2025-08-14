'use client';

import { useState } from 'react';
import { apiService } from '@/services/api';

const agentDescriptions: Record<string, { title: string; description: string; example: string }> = {
  nl_input: {
    title: '🗣️ Natural Language Input',
    description: '자연어 입력을 구조화된 요구사항으로 변환합니다.',
    example: '쇼핑몰 웹사이트 만들어줘'
  },
  ui_selection: {
    title: '🎨 UI Framework Selection',
    description: '프로젝트에 적합한 UI 프레임워크를 선택합니다.',
    example: 'React, Vue, Angular 중 선택'
  },
  parser: {
    title: '📝 Requirements Parser',
    description: '요구사항을 상세하게 분석하고 파싱합니다.',
    example: '기능 요구사항, 비기능 요구사항 분리'
  },
  component_decision: {
    title: '🧩 Component Decision',
    description: '필요한 컴포넌트들을 결정합니다.',
    example: 'Header, ProductList, Cart, Footer'
  },
  match_rate: {
    title: '📊 Match Rate Analysis',
    description: '요구사항과 구현의 일치율을 분석합니다.',
    example: '요구사항 충족도 85%'
  },
  search: {
    title: '🔍 Code Search',
    description: '관련 코드와 라이브러리를 검색합니다.',
    example: 'npm packages, GitHub repos'
  },
  generation: {
    title: '⚡ Code Generation',
    description: 'AI를 사용해 코드를 생성합니다.',
    example: 'Component code, API routes'
  },
  assembly: {
    title: '🔧 Project Assembly',
    description: '생성된 코드를 프로젝트로 조립합니다.',
    example: 'File structure, dependencies'
  },
  download: {
    title: '📦 Download Package',
    description: '완성된 프로젝트를 다운로드 가능한 형태로 패키징합니다.',
    example: 'ZIP file with all files'
  }
};

export default function AgentsPage() {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [input, setInput] = useState('');
  const [output, setOutput] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleTest = async () => {
    if (!selectedAgent || !input) return;

    setLoading(true);
    setOutput(null);

    try {
      const result = await apiService.executeAgent(selectedAgent, {
        task: input,
        context: {}
      });
      setOutput(result);
    } catch (error) {
      setOutput({ error: error instanceof Error ? error.message : 'Failed to execute agent' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold">🤖 Agent Testing Lab</h1>
        <p className="text-gray-600 mt-2">각 에이전트를 개별적으로 테스트하고 결과를 확인하세요</p>
      </header>

      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Agent List */}
        <div className="lg:col-span-1">
          <h2 className="text-xl font-semibold mb-4">Available Agents</h2>
          <div className="space-y-2">
            {Object.entries(agentDescriptions).map(([key, agent]) => (
              <button
                key={key}
                onClick={() => {
                  setSelectedAgent(key);
                  setOutput(null);
                }}
                className={`w-full text-left p-4 rounded-lg border transition-all ${
                  selectedAgent === key
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-gray-300 dark:border-gray-700 hover:border-gray-400'
                }`}
              >
                <div className="font-semibold">{agent.title}</div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  {agent.description}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Test Panel */}
        <div className="lg:col-span-2">
          {selectedAgent ? (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-semibold mb-4">
                {agentDescriptions[selectedAgent].title}
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                {agentDescriptions[selectedAgent].description}
              </p>

              {/* Input */}
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Input</label>
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={`예: ${agentDescriptions[selectedAgent].example}`}
                  className="w-full p-3 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                  rows={4}
                />
              </div>

              {/* Execute Button */}
              <button
                onClick={handleTest}
                disabled={loading || !input}
                className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
              >
                {loading ? 'Executing...' : `Test ${selectedAgent} Agent`}
              </button>

              {/* Output */}
              {output && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-2">Output</h3>
                  <div className="bg-gray-100 dark:bg-gray-900 rounded-lg p-4">
                    {output.error ? (
                      <div className="text-red-600">
                        <strong>Error:</strong> {output.error}
                      </div>
                    ) : (
                      <div>
                        {output.result && (
                          <div className="mb-3">
                            <strong>Result:</strong>
                            <pre className="mt-1 text-sm overflow-auto">
                              {JSON.stringify(output.result, null, 2)}
                            </pre>
                          </div>
                        )}
                        {output.metadata && (
                          <div className="text-sm text-gray-600 dark:text-gray-400">
                            <div>Agent: {output.metadata.agent}</div>
                            <div>Execution Time: {output.metadata.execution_time}s</div>
                            <div>Timestamp: {new Date(output.metadata.timestamp).toLocaleString()}</div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Pipeline Flow */}
              <div className="mt-8">
                <h3 className="text-lg font-semibold mb-4">Pipeline Flow</h3>
                <div className="flex flex-wrap gap-2">
                  {Object.keys(agentDescriptions).map((agent, index) => (
                    <div
                      key={agent}
                      className={`px-3 py-1 rounded-full text-sm ${
                        agent === selectedAgent
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-200 dark:bg-gray-700'
                      }`}
                    >
                      {index + 1}. {agent}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 text-center">
              <p className="text-xl text-gray-500">
                ← 왼쪽에서 테스트할 에이전트를 선택하세요
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
