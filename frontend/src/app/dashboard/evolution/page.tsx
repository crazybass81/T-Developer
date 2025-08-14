'use client';

import React, { useEffect, useState } from 'react';
import {
  Brain,
  Activity,
  TrendingUp,
  Zap,
  Shield,
  Users,
  GitBranch,
  AlertTriangle,
  Play,
  Pause,
  RotateCcw,
  Settings
} from 'lucide-react';
import { MetricCard } from '@/components/dashboard/MetricCard';
import { EvolutionChart } from '@/components/evolution/EvolutionChart';
import { useEvolutionStore } from '@/lib/store/evolutionStore';
import getSocketManager from '@/lib/socket/manager';

export default function EvolutionDashboard() {
  const {
    currentGeneration,
    parameters,
    isEvolving,
    fitnessMetrics,
    diversityMetrics,
    convergenceStatus,
    safetyMetrics,
    fetchCurrentGeneration,
    fetchMetrics,
    startEvolution,
    stopEvolution,
    updateParameters,
  } = useEvolutionStore();

  const [chartData, setChartData] = useState({
    generations: [] as number[],
    fitness: [] as number[],
    diversity: [] as number[],
    convergence: [] as number[],
  });

  const [showSettings, setShowSettings] = useState(false);

  useEffect(() => {
    // Initial data fetch
    fetchCurrentGeneration();
    fetchMetrics();

    // Setup WebSocket listeners
    const socketManager = getSocketManager();

    const unsubscribers = [
      socketManager.subscribe('evolution:update', (data) => {
        fetchCurrentGeneration();
        fetchMetrics();
      }),
      socketManager.subscribe('evolution:generation', (data) => {
        // Update chart data
        setChartData(prev => ({
          generations: [...prev.generations.slice(-49), data.generation],
          fitness: [...prev.fitness.slice(-49), data.fitness],
          diversity: [...prev.diversity.slice(-49), data.diversity],
          convergence: [...prev.convergence.slice(-49), data.convergence],
        }));
      }),
      socketManager.subscribe('evolution:alert', (data) => {
        console.warn('Evolution alert:', data);
      }),
    ];

    return () => {
      unsubscribers.forEach(unsub => unsub());
    };
  }, []);

  const handleParameterChange = (key: keyof typeof parameters, value: number) => {
    updateParameters({ [key]: value });
  };

  const getStatus = (value: number, threshold: number): 'healthy' | 'warning' | 'error' => {
    if (value >= threshold) return 'healthy';
    if (value >= threshold * 0.7) return 'warning';
    return 'error';
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Evolution Engine</h1>
          <p className="text-gray-600 mt-1">AI Autonomous Evolution System</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg flex items-center space-x-2"
          >
            <Settings className="w-4 h-4" />
            <span>Settings</span>
          </button>
          {isEvolving ? (
            <button
              onClick={stopEvolution}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg flex items-center space-x-2"
            >
              <Pause className="w-4 h-4" />
              <span>Stop Evolution</span>
            </button>
          ) : (
            <button
              onClick={startEvolution}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg flex items-center space-x-2"
            >
              <Play className="w-4 h-4" />
              <span>Start Evolution</span>
            </button>
          )}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          title="Generation"
          value={currentGeneration?.generation || 0}
          icon={<Brain />}
          trend={isEvolving ? '+1/min' : 'Paused'}
          status={isEvolving ? 'healthy' : 'neutral'}
        />
        <MetricCard
          title="Population Size"
          value={currentGeneration?.agents?.length || 0}
          icon={<Users />}
          target={String(parameters.populationSize)}
          status="healthy"
        />
        <MetricCard
          title="Best Fitness"
          value={`${((fitnessMetrics?.best || 0) * 100).toFixed(1)}%`}
          icon={<TrendingUp />}
          target={`${(parameters.fitnessThreshold * 100).toFixed(0)}%`}
          status={getStatus(fitnessMetrics?.best || 0, parameters.fitnessThreshold)}
        />
        <MetricCard
          title="Safety Score"
          value={`${safetyMetrics?.safetyScore || 100}%`}
          icon={<Shield />}
          constraint="100%"
          status={safetyMetrics?.violations ? 'warning' : 'healthy'}
        />
      </div>

      {/* Evolution Chart */}
      <EvolutionChart
        data={chartData}
        title="Evolution Progress Over Time"
        height={400}
      />

      {/* Detailed Metrics */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Fitness Metrics */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-blue-600" />
            Fitness Metrics
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Current</span>
              <span className="font-medium">{fitnessMetrics?.current?.toFixed(3) || '0.000'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Average</span>
              <span className="font-medium">{fitnessMetrics?.average?.toFixed(3) || '0.000'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Best</span>
              <span className="font-medium text-green-600">{fitnessMetrics?.best?.toFixed(3) || '0.000'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Worst</span>
              <span className="font-medium text-red-600">{fitnessMetrics?.worst?.toFixed(3) || '0.000'}</span>
            </div>
          </div>
        </div>

        {/* Diversity Metrics */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <GitBranch className="w-5 h-5 mr-2 text-green-600" />
            Diversity Metrics
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Genetic</span>
              <span className="font-medium">{diversityMetrics?.genetic?.toFixed(3) || '0.000'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Phenotypic</span>
              <span className="font-medium">{diversityMetrics?.phenotypic?.toFixed(3) || '0.000'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Behavioral</span>
              <span className="font-medium">{diversityMetrics?.behavioral?.toFixed(3) || '0.000'}</span>
            </div>
          </div>
        </div>

        {/* Convergence Status */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <Activity className="w-5 h-5 mr-2 text-orange-600" />
            Convergence Status
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Status</span>
              <span className={`font-medium ${convergenceStatus?.converged ? 'text-green-600' : 'text-orange-600'}`}>
                {convergenceStatus?.converged ? 'Converged' : 'Evolving'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Rate</span>
              <span className="font-medium">{convergenceStatus?.convergenceRate?.toFixed(3) || '0.000'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Est. Generations</span>
              <span className="font-medium">{convergenceStatus?.estimatedGenerations || 'N/A'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Plateau</span>
              <span className={`font-medium ${convergenceStatus?.plateauDetected ? 'text-yellow-600' : 'text-gray-600'}`}>
                {convergenceStatus?.plateauDetected ? 'Detected' : 'None'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Evolution Parameters (Settings) */}
      {showSettings && (
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold mb-4">Evolution Parameters</h3>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Population Size
              </label>
              <input
                type="number"
                value={parameters.populationSize}
                onChange={(e) => handleParameterChange('populationSize', Number(e.target.value))}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                min="10"
                max="1000"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Mutation Rate
              </label>
              <input
                type="number"
                value={parameters.mutationRate}
                onChange={(e) => handleParameterChange('mutationRate', Number(e.target.value))}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                min="0"
                max="1"
                step="0.01"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Crossover Rate
              </label>
              <input
                type="number"
                value={parameters.crossoverRate}
                onChange={(e) => handleParameterChange('crossoverRate', Number(e.target.value))}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                min="0"
                max="1"
                step="0.01"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Elite Size
              </label>
              <input
                type="number"
                value={parameters.eliteSize}
                onChange={(e) => handleParameterChange('eliteSize', Number(e.target.value))}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                min="1"
                max="100"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Generations
              </label>
              <input
                type="number"
                value={parameters.maxGenerations}
                onChange={(e) => handleParameterChange('maxGenerations', Number(e.target.value))}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                min="10"
                max="10000"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Fitness Threshold
              </label>
              <input
                type="number"
                value={parameters.fitnessThreshold}
                onChange={(e) => handleParameterChange('fitnessThreshold', Number(e.target.value))}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                min="0"
                max="1"
                step="0.01"
              />
            </div>
          </div>
        </div>
      )}

      {/* Safety Alerts */}
      {safetyMetrics?.alerts && safetyMetrics.alerts.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center mb-2">
            <AlertTriangle className="w-5 h-5 text-yellow-600 mr-2" />
            <h3 className="text-lg font-semibold text-yellow-800">Safety Alerts</h3>
          </div>
          <ul className="space-y-1">
            {safetyMetrics.alerts.map((alert, index) => (
              <li key={index} className="text-sm text-yellow-700">• {alert}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
