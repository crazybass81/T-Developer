'use client';

import { useEffect, useState } from 'react';
import { apiService, EvolutionStatus, HealthResponse, SystemMetrics } from '@/services/api';

export default function Home() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [evolution, setEvolution] = useState<EvolutionStatus | null>(null);
  const [agents, setAgents] = useState<string[]>([]);
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [healthData, evolutionData, agentsList, metricsData] = await Promise.all([
          apiService.health(),
          apiService.getEvolutionStatus(),
          apiService.listAgents(),
          apiService.getMetrics()
        ]);

        setHealth(healthData);
        setEvolution(evolutionData);
        setAgents(agentsList);
        setMetrics(metricsData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to connect to backend');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading T-Developer Dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-red-500">
          <h2 className="text-2xl font-bold mb-4">Connection Error</h2>
          <p>{error}</p>
          <p className="mt-2 text-sm">Make sure the backend is running on port 8000</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-8">
      <header className="mb-8">
        <h1 className="text-4xl font-bold text-center">🧬 T-Developer AI Evolution System</h1>
        <p className="text-center text-gray-600 mt-2">Autonomous AI Development Platform</p>
      </header>

      <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Health Status */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">System Health</h2>
          {health && (
            <div>
              <div className="flex items-center mb-2">
                <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
                <span className="capitalize">{health.status}</span>
              </div>
              <p className="text-sm text-gray-600">Service: {health.service}</p>
              <p className="text-xs text-gray-500 mt-2">
                {new Date(health.timestamp).toLocaleString()}
              </p>
            </div>
          )}
        </div>

        {/* Evolution Status */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Evolution Status</h2>
          {evolution && (
            <div>
              <div className="mb-3">
                <div className="flex justify-between mb-1">
                  <span className="text-sm">AI Autonomy</span>
                  <span className="text-sm font-bold">{(evolution.ai_autonomy_level * 100).toFixed(0)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full"
                    style={{ width: `${evolution.ai_autonomy_level * 100}%` }}
                  ></div>
                </div>
              </div>
              <p className="text-sm">Phase: {evolution.phase}</p>
              <p className="text-sm">Day: {evolution.day}</p>
              <p className="text-sm">Progress: {(evolution.progress * 100).toFixed(0)}%</p>
              <p className="text-xs text-gray-500 mt-2">Mode: {evolution.evolution_mode}</p>
            </div>
          )}
        </div>

        {/* Active Agents */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Active Agents ({agents.length})</h2>
          <div className="max-h-40 overflow-y-auto">
            {agents.length > 0 ? (
              <ul className="space-y-1">
                {agents.map((agent, index) => (
                  <li key={index} className="text-sm py-1 border-b border-gray-200 dark:border-gray-700">
                    {agent}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-gray-500">No agents deployed</p>
            )}
          </div>
        </div>

        {/* Metrics */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 md:col-span-2 lg:col-span-3">
          <h2 className="text-xl font-semibold mb-4">System Metrics (실시간)</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{metrics?.avg_agent_size_kb || 0}KB</p>
              <p className="text-sm text-gray-600">평균 에이전트 크기</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">{metrics?.instantiation_speed_us || 0}μs</p>
              <p className="text-sm text-gray-600">인스턴스화 속도</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">{metrics?.test_coverage_percent || 0}%</p>
              <p className="text-sm text-gray-600">테스트 커버리지</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-orange-600">{metrics?.total_agents || 0}</p>
              <p className="text-sm text-gray-600">총 에이전트 수</p>
            </div>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-indigo-600">{metrics?.total_tests || 0}</p>
              <p className="text-sm text-gray-600">총 테스트 수</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-pink-600">{metrics?.memory_usage_mb || 0}MB</p>
              <p className="text-sm text-gray-600">메모리 사용량</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-600">Phase {evolution?.phase || 0}</p>
              <p className="text-sm text-gray-600">현재 단계</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-teal-600">Day {evolution?.day || 0}</p>
              <p className="text-sm text-gray-600">진행 일수</p>
            </div>
          </div>
        </div>

        {/* Phase Progress */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 md:col-span-2 lg:col-span-3">
          <h2 className="text-xl font-semibold mb-4">Phase Progress</h2>
          <div className="space-y-3">
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm">Phase 1: Foundation</span>
                <span className="text-sm text-green-600">✅ 100%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-600 h-2 rounded-full" style={{ width: `${metrics?.phase_stats.phase1.progress || 0}%` }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm">Phase 2: Meta Agents</span>
                <span className="text-sm text-green-600">✅ {metrics?.phase_stats.phase2.progress || 0}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-600 h-2 rounded-full" style={{ width: `${metrics?.phase_stats.phase2.progress || 0}%` }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm">Phase 3: Evolution Engine</span>
                <span className="text-sm text-blue-600">🚧 {metrics?.phase_stats.phase3.progress || 0}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${metrics?.phase_stats.phase3.progress || 0}%` }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm">Phase 4: Production</span>
                <span className="text-sm text-gray-400">⏸ {metrics?.phase_stats.phase4.progress || 0}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-gray-400 h-2 rounded-full" style={{ width: `${metrics?.phase_stats.phase4.progress || 0}%` }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
