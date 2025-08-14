'use client';

import { useEffect, useState } from 'react';

interface OrchestrationStatus {
  active_cycles: number;
  total_iterations: number;
  average_cycle_time: number;
  success_rate: number;
  current_phase: string;
  queue_length: number;
}

export default function MetricsPage() {
  const [status, setStatus] = useState<OrchestrationStatus | null>(null);
  const [cycleHistory, setCycleHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:8000/orchestration/status');
        const data = await response.json();
        setStatus(data);
      } catch (error) {
        console.error('Failed to fetch orchestration status:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  const runCycle = async () => {
    try {
      const response = await fetch('http://localhost:8000/orchestrate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          input: 'Create a REST API for user management',
          iteration: (status?.total_iterations || 0) + 1
        })
      });

      const result = await response.json();
      setCycleHistory(prev => [result, ...prev.slice(0, 4)]);
    } catch (error) {
      console.error('Failed to run cycle:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading Orchestration Metrics...</div>
      </div>
    );
  }

  const phaseColors = {
    ServiceBuilder: 'blue',
    ServiceImprover: 'green',
    ServiceValidator: 'purple'
  };

  return (
    <div className="min-h-screen p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold">📊 Orchestration Metrics</h1>
        <p className="text-gray-600 mt-2">3-Agent Evolution Cycle 실시간 모니터링</p>
      </header>

      {/* Control Panel */}
      <div className="max-w-6xl mx-auto mb-8">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Control Panel</h2>
          <button
            onClick={runCycle}
            className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-semibold"
          >
            🔄 Run Evolution Cycle
          </button>
        </div>
      </div>

      {/* Current Status */}
      <div className="max-w-6xl mx-auto mb-8">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">오케스트레이션 현황</h2>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <div className="text-center">
              <p className="text-3xl font-bold text-blue-600">{status?.active_cycles || 0}</p>
              <p className="text-sm text-gray-600">활성 사이클</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-green-600">{status?.total_iterations || 0}</p>
              <p className="text-sm text-gray-600">총 반복 횟수</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-purple-600">{status?.average_cycle_time || 0}s</p>
              <p className="text-sm text-gray-600">평균 사이클 시간</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-orange-600">{((status?.success_rate || 0) * 100).toFixed(0)}%</p>
              <p className="text-sm text-gray-600">성공률</p>
            </div>
            <div className="text-center">
              <p className={`text-3xl font-bold text-${phaseColors[status?.current_phase as keyof typeof phaseColors] || 'gray'}-600`}>
                {status?.current_phase?.replace('Service', '') || 'N/A'}
              </p>
              <p className="text-sm text-gray-600">현재 단계</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-red-600">{status?.queue_length || 0}</p>
              <p className="text-sm text-gray-600">대기 큐</p>
            </div>
          </div>
        </div>
      </div>

      {/* 3-Agent Cycle Visualization */}
      <div className="max-w-6xl mx-auto mb-8">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">3-Agent Evolution Cycle</h2>

          <div className="flex justify-around items-center">
            {['ServiceBuilder', 'ServiceImprover', 'ServiceValidator'].map((agent, index) => (
              <div key={agent} className="text-center">
                <div className={`w-32 h-32 rounded-full flex items-center justify-center text-white font-bold text-lg ${
                  status?.current_phase === agent
                    ? `bg-${phaseColors[agent as keyof typeof phaseColors]}-600 animate-pulse`
                    : 'bg-gray-400'
                }`}>
                  {agent.replace('Service', '')}
                </div>
                <p className="mt-2 font-semibold">{agent}</p>
                <p className="text-sm text-gray-600">
                  {index === 0 && '프로그램 생성'}
                  {index === 1 && '리팩터링/최적화'}
                  {index === 2 && '평가/검증'}
                </p>
                {index < 2 && (
                  <div className="absolute ml-32 -mt-20 text-4xl">→</div>
                )}
              </div>
            ))}
            <div className="absolute ml-[-40px] mt-40 text-4xl rotate-180">↩</div>
          </div>
        </div>
      </div>

      {/* Cycle History */}
      {cycleHistory.length > 0 && (
        <div className="max-w-6xl mx-auto">
          <h2 className="text-xl font-semibold mb-4">최근 실행 이력</h2>

          <div className="space-y-4">
            {cycleHistory.map((cycle, index) => (
              <div key={index} className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="font-semibold">Iteration #{cycle.iteration}</h3>
                  <span className={`px-3 py-1 rounded text-sm ${
                    cycle.final_output?.status === 'success'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {cycle.final_output?.status || 'processing'}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {cycle.cycle?.map((step: any, stepIndex: number) => (
                    <div key={stepIndex} className="border rounded p-3">
                      <h4 className="font-semibold text-sm mb-2">{step.agent}</h4>
                      <p className="text-xs text-gray-600">Action: {step.action}</p>
                      {step.metrics && (
                        <div className="mt-2 text-xs">
                          <p>Quality: {step.metrics.quality_score}</p>
                          <p>Performance: {step.metrics.performance_score}</p>
                        </div>
                      )}
                      {step.improvements && (
                        <ul className="mt-2 text-xs">
                          {step.improvements.slice(0, 2).map((imp: string, i: number) => (
                            <li key={i}>• {imp}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
