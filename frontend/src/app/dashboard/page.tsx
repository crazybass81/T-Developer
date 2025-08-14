'use client';

import React, { useEffect, useState } from 'react';
import {
  Brain,
  Users,
  Activity,
  TrendingUp,
  Zap,
  Shield,
  DollarSign,
  GitBranch,
  Layers,
  CheckCircle,
  AlertCircle,
  XCircle,
  Clock,
  ArrowUp,
  ArrowDown
} from 'lucide-react';
import { MetricCard } from '@/components/dashboard/MetricCard';
import { EvolutionChart } from '@/components/evolution/EvolutionChart';
import Link from 'next/link';
import { clsx } from 'clsx';

export default function Dashboard() {
  const [systemMetrics, setSystemMetrics] = useState({
    cpu: 42,
    memory: 68,
    disk: 35,
    network: { in: 125, out: 89 },
    activeAgents: 247,
    runningWorkflows: 12,
    queuedTasks: 34,
  });

  const [evolutionData] = useState({
    generations: Array.from({ length: 20 }, (_, i) => i + 1),
    fitness: Array.from({ length: 20 }, (_, i) => 0.5 + (i * 0.02) + Math.random() * 0.1),
    diversity: Array.from({ length: 20 }, (_, i) => 0.8 - (i * 0.01) + Math.random() * 0.05),
    convergence: Array.from({ length: 20 }, (_, i) => 0.3 + (i * 0.03) + Math.random() * 0.05),
  });

  const [recentActivities] = useState([
    { id: 1, type: 'evolution', message: 'Generation 45 completed with fitness 0.925', time: '2 min ago', status: 'success' },
    { id: 2, type: 'agent', message: 'Agent #NL-INPUT-v3.2 deployed to production', time: '5 min ago', status: 'success' },
    { id: 3, type: 'workflow', message: 'Workflow "Data Processing Pipeline" started', time: '10 min ago', status: 'running' },
    { id: 4, type: 'service', message: 'Service improvement detected 25% performance gain', time: '15 min ago', status: 'success' },
    { id: 5, type: 'alert', message: 'High memory usage detected in Agent #PARSER-v2.1', time: '20 min ago', status: 'warning' },
  ]);

  const getActivityIcon = (type: string, status: string) => {
    if (status === 'success') return <CheckCircle className="w-4 h-4 text-green-600" />;
    if (status === 'warning') return <AlertCircle className="w-4 h-4 text-yellow-600" />;
    if (status === 'error') return <XCircle className="w-4 h-4 text-red-600" />;
    if (status === 'running') return <Activity className="w-4 h-4 text-blue-600 animate-pulse" />;
    return <Clock className="w-4 h-4 text-gray-600" />;
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">System Dashboard</h1>
        <p className="text-gray-600 mt-1">T-Developer AI Autonomous Evolution System</p>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          title="AI Autonomy"
          value="88%"
          icon={<Brain />}
          trend="+3%"
          target="85%"
          status="healthy"
        />
        <MetricCard
          title="Active Agents"
          value={247}
          icon={<Users />}
          status="healthy"
        />
        <MetricCard
          title="Performance"
          value="2.8μs"
          icon={<Zap />}
          constraint="< 3μs"
          status="healthy"
        />
        <MetricCard
          title="Cost Savings"
          value="20%"
          icon={<DollarSign />}
          trend="+5%"
          target="30%"
          status="healthy"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Evolution Progress Chart */}
        <div className="lg:col-span-2">
          <EvolutionChart
            data={evolutionData}
            title="Evolution Progress (Last 20 Generations)"
            height={350}
          />
        </div>

        {/* System Resources */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold mb-4">System Resources</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">CPU Usage</span>
                <span className="font-medium">{systemMetrics.cpu}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all"
                  style={{ width: `${systemMetrics.cpu}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">Memory Usage</span>
                <span className="font-medium">{systemMetrics.memory}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-600 h-2 rounded-full transition-all"
                  style={{ width: `${systemMetrics.memory}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">Disk Usage</span>
                <span className="font-medium">{systemMetrics.disk}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-yellow-600 h-2 rounded-full transition-all"
                  style={{ width: `${systemMetrics.disk}%` }}
                />
              </div>
            </div>

            <div className="pt-2 border-t">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Network I/O</span>
                <div className="flex space-x-3">
                  <span className="flex items-center">
                    <ArrowDown className="w-3 h-3 mr-1 text-green-600" />
                    {systemMetrics.network.in} KB/s
                  </span>
                  <span className="flex items-center">
                    <ArrowUp className="w-3 h-3 mr-1 text-blue-600" />
                    {systemMetrics.network.out} KB/s
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions and Recent Activity */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Quick Actions */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
          <div className="grid grid-cols-2 gap-3">
            <Link
              href="/dashboard/evolution"
              className="p-4 border rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Brain className="w-6 h-6 text-blue-600 mb-2" />
              <div className="font-medium">Evolution Engine</div>
              <div className="text-sm text-gray-600">Manage evolution</div>
            </Link>
            <Link
              href="/dashboard/agents"
              className="p-4 border rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Users className="w-6 h-6 text-green-600 mb-2" />
              <div className="font-medium">Agents</div>
              <div className="text-sm text-gray-600">247 active agents</div>
            </Link>
            <Link
              href="/dashboard/workflows"
              className="p-4 border rounded-lg hover:bg-gray-50 transition-colors"
            >
              <GitBranch className="w-6 h-6 text-purple-600 mb-2" />
              <div className="font-medium">Workflows</div>
              <div className="text-sm text-gray-600">12 running</div>
            </Link>
            <Link
              href="/dashboard/services"
              className="p-4 border rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Layers className="w-6 h-6 text-orange-600 mb-2" />
              <div className="font-medium">Service Builder</div>
              <div className="text-sm text-gray-600">Create services</div>
            </Link>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
          <div className="space-y-3">
            {recentActivities.map(activity => (
              <div key={activity.id} className="flex items-start space-x-3">
                {getActivityIcon(activity.type, activity.status)}
                <div className="flex-1">
                  <p className="text-sm text-gray-900">{activity.message}</p>
                  <p className="text-xs text-gray-500">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
          <Link
            href="/dashboard/logs"
            className="mt-4 block text-center text-sm text-blue-600 hover:text-blue-700"
          >
            View all activity →
          </Link>
        </div>
      </div>

      {/* System Overview Stats */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6 text-white">
        <h3 className="text-xl font-semibold mb-4">System Overview</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div className="text-3xl font-bold">45</div>
            <div className="text-blue-100">Generations</div>
          </div>
          <div>
            <div className="text-3xl font-bold">92.5%</div>
            <div className="text-blue-100">Best Fitness</div>
          </div>
          <div>
            <div className="text-3xl font-bold">3.66μs</div>
            <div className="text-blue-100">Avg. Execution</div>
          </div>
          <div>
            <div className="text-3xl font-bold">100%</div>
            <div className="text-blue-100">Safety Score</div>
          </div>
        </div>
      </div>
    </div>
  );
};
