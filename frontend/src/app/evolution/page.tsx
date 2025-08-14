'use client';

import { useEffect, useState } from 'react';
import { apiService, EvolutionStatus, SystemMetrics } from '@/services/api';

export default function EvolutionPage() {
  const [evolution, setEvolution] = useState<EvolutionStatus | null>(null);
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [evolutionData, metricsData] = await Promise.all([
          apiService.getEvolutionStatus(),
          apiService.getMetrics()
        ]);
        setEvolution(evolutionData);
        setMetrics(metricsData);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading Evolution Data...</div>
      </div>
    );
  }

  const phases = [
    {
      name: 'Phase 1: Foundation',
      days: '1-20',
      description: '기초 인프라 구축',
      tasks: ['Agent Core', 'Message Queue', 'API Gateway', 'Orchestration']
    },
    {
      name: 'Phase 2: Meta Agents',
      days: '21-40',
      description: '메타 에이전트 시스템',
      tasks: ['ServiceBuilder', 'ServiceImprover', 'ServiceValidator', 'Meta Coordinator']
    },
    {
      name: 'Phase 3: Evolution Engine',
      days: '41-60',
      description: '진화 엔진 구현',
      tasks: ['Genetic Algorithm', 'Fitness Evaluation', 'Mutation System', 'Safety Controls']
    },
    {
      name: 'Phase 4: Production',
      days: '61-80',
      description: '프로덕션 배포',
      tasks: ['Monitoring', 'Scaling', 'Optimization', 'Documentation']
    }
  ];

  const currentPhase = evolution?.phase || 3;
  const currentDay = evolution?.day || 45;

  return (
    <div className="min-h-screen p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold">🧬 Evolution Engine Status</h1>
        <p className="text-gray-600 mt-2">AI 자율 진화 시스템 실시간 모니터링</p>
      </header>

      {/* Current Status */}
      <div className="max-w-6xl mx-auto mb-8">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-semibold mb-4">현재 상태</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-5xl font-bold text-blue-600 mb-2">
                {(evolution?.ai_autonomy_level || 0) * 100}%
              </div>
              <p className="text-gray-600">AI 자율성 레벨</p>
              <p className="text-sm text-gray-500 mt-1">목표: 85%</p>
            </div>

            <div className="text-center">
              <div className="text-5xl font-bold text-green-600 mb-2">
                Day {currentDay}
              </div>
              <p className="text-gray-600">진행 일수</p>
              <p className="text-sm text-gray-500 mt-1">총 80일 계획</p>
            </div>

            <div className="text-center">
              <div className="text-5xl font-bold text-purple-600 mb-2">
                Phase {currentPhase}
              </div>
              <p className="text-gray-600">현재 단계</p>
              <p className="text-sm text-gray-500 mt-1">{phases[currentPhase - 1]?.description}</p>
            </div>
          </div>

          <div className="mt-6">
            <div className="flex justify-between mb-2">
              <span>전체 진행률</span>
              <span className="font-bold">{Math.round((currentDay / 80) * 100)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-gradient-to-r from-blue-500 to-green-500 h-3 rounded-full transition-all"
                style={{ width: `${(currentDay / 80) * 100}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Phase Details */}
      <div className="max-w-6xl mx-auto">
        <h2 className="text-2xl font-semibold mb-4">Phase 상세 정보</h2>

        <div className="grid gap-4">
          {phases.map((phase, index) => {
            const phaseNum = index + 1;
            const phaseStats = metrics?.phase_stats[`phase${phaseNum}` as keyof typeof metrics.phase_stats];
            const isActive = phaseNum === currentPhase;
            const isCompleted = phaseStats?.completed;

            return (
              <div
                key={phase.name}
                className={`bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border-2 ${
                  isActive ? 'border-blue-500' : isCompleted ? 'border-green-500' : 'border-gray-300'
                }`}
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-semibold flex items-center gap-2">
                      {phase.name}
                      {isCompleted && <span className="text-green-600">✅</span>}
                      {isActive && <span className="text-blue-600">🔄</span>}
                    </h3>
                    <p className="text-gray-600">Day {phase.days} • {phase.description}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold">
                      {phaseStats?.progress || 0}%
                    </div>
                    <p className="text-sm text-gray-500">
                      {isCompleted ? '완료' : isActive ? '진행중' : '대기'}
                    </p>
                  </div>
                </div>

                <div className="mb-4">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${
                        isCompleted ? 'bg-green-600' : isActive ? 'bg-blue-600' : 'bg-gray-400'
                      }`}
                      style={{ width: `${phaseStats?.progress || 0}%` }}
                    ></div>
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {phase.tasks.map((task) => (
                    <div
                      key={task}
                      className={`px-3 py-1 rounded text-sm text-center ${
                        isCompleted
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                          : isActive
                          ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                          : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
                      }`}
                    >
                      {task}
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Real-time Metrics */}
      <div className="max-w-6xl mx-auto mt-8">
        <h2 className="text-2xl font-semibold mb-4">실시간 메트릭</h2>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">에이전트 크기</p>
              <p className="text-xl font-bold">{metrics?.avg_agent_size_kb || 0} KB</p>
              <p className="text-xs text-gray-500">목표: &lt;6.5KB</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">인스턴스화 속도</p>
              <p className="text-xl font-bold">{metrics?.instantiation_speed_us || 0} μs</p>
              <p className="text-xs text-gray-500">목표: &lt;3μs</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">테스트 커버리지</p>
              <p className="text-xl font-bold">{metrics?.test_coverage_percent || 0}%</p>
              <p className="text-xs text-gray-500">목표: 85%</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Evolution Mode</p>
              <p className="text-xl font-bold capitalize">{evolution?.evolution_mode || 'N/A'}</p>
              <p className="text-xs text-gray-500">Status: Active</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
