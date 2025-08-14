'use client';

import React, { useEffect, useState } from 'react';
import {
  Search,
  Filter,
  Grid3x3,
  List,
  Plus,
  Play,
  Pause,
  RotateCcw,
  Trash2,
  Download,
  Upload,
  Activity,
  Cpu,
  MemoryStick,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react';
import { Agent, AgentStatus, AgentType, FilterOptions } from '@/types';
import { agentsApi } from '@/lib/api/agents';
import getSocketManager from '@/lib/socket/manager';
import { clsx } from 'clsx';

export default function AgentsManagement() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedAgents, setSelectedAgents] = useState<Set<string>>(new Set());
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [filters, setFilters] = useState<FilterOptions>({
    search: '',
    status: [],
    type: [],
    sortBy: 'name',
    sortOrder: 'asc',
  });
  const [statistics, setStatistics] = useState<any>(null);

  useEffect(() => {
    fetchAgents();
    fetchStatistics();

    // Setup WebSocket listeners
    const socketManager = getSocketManager();
    const unsubscribers = [
      socketManager.subscribe('agent:status', (data) => {
        updateAgentStatus(data.agentId, data.status);
      }),
      socketManager.subscribe('agent:created', (data) => {
        fetchAgents();
      }),
      socketManager.subscribe('agent:deleted', (data) => {
        setAgents(prev => prev.filter(a => a.id !== data.agentId));
      }),
    ];

    return () => {
      unsubscribers.forEach(unsub => unsub());
    };
  }, []);

  const fetchAgents = async () => {
    setLoading(true);
    try {
      const response = await agentsApi.getAgents(filters);
      if (response.success && response.data) {
        setAgents(response.data.items);
      }
    } catch (error) {
      console.error('Failed to fetch agents:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await agentsApi.getStatistics();
      if (response.success && response.data) {
        setStatistics(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch statistics:', error);
    }
  };

  const updateAgentStatus = (agentId: string, status: AgentStatus) => {
    setAgents(prev => prev.map(agent =>
      agent.id === agentId ? { ...agent, status } : agent
    ));
  };

  const handleBatchAction = async (action: 'start' | 'stop' | 'delete') => {
    const agentIds = Array.from(selectedAgents);
    if (agentIds.length === 0) return;

    try {
      let response;
      switch (action) {
        case 'start':
          response = await agentsApi.batchStart(agentIds);
          break;
        case 'stop':
          response = await agentsApi.batchStop(agentIds);
          break;
        case 'delete':
          if (!confirm(`Are you sure you want to delete ${agentIds.length} agents?`)) return;
          response = await agentsApi.batchDelete(agentIds);
          break;
      }

      setSelectedAgents(new Set());
      await fetchAgents();
    } catch (error) {
      console.error(`Failed to ${action} agents:`, error);
    }
  };

  const getStatusIcon = (status: AgentStatus) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'idle':
        return <AlertCircle className="w-4 h-4 text-yellow-600" />;
      case 'processing':
        return <Activity className="w-4 h-4 text-blue-600 animate-pulse" />;
      case 'error':
        return <XCircle className="w-4 h-4 text-red-600" />;
      default:
        return <AlertCircle className="w-4 h-4 text-gray-600" />;
    }
  };

  const getStatusColor = (status: AgentStatus) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'idle':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'processing':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'error':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const AgentCard = ({ agent }: { agent: Agent }) => (
    <div className={clsx(
      'bg-white rounded-lg border-2 p-4 hover:shadow-lg transition-all cursor-pointer',
      selectedAgents.has(agent.id) ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
    )}
      onClick={() => setSelectedAgent(agent)}
    >
      <div className="flex justify-between items-start mb-3">
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            checked={selectedAgents.has(agent.id)}
            onChange={(e) => {
              e.stopPropagation();
              const newSelected = new Set(selectedAgents);
              if (e.target.checked) {
                newSelected.add(agent.id);
              } else {
                newSelected.delete(agent.id);
              }
              setSelectedAgents(newSelected);
            }}
            className="w-4 h-4"
          />
          <h3 className="font-semibold text-gray-900">{agent.name}</h3>
        </div>
        <div className={clsx(
          'px-2 py-1 rounded-full text-xs font-medium flex items-center space-x-1',
          getStatusColor(agent.status)
        )}>
          {getStatusIcon(agent.status)}
          <span>{agent.status}</span>
        </div>
      </div>

      <div className="space-y-2 text-sm">
        <div className="flex justify-between text-gray-600">
          <span>Type:</span>
          <span className="font-medium">{agent.type}</span>
        </div>
        <div className="flex justify-between text-gray-600">
          <span>Version:</span>
          <span className="font-medium">{agent.version}</span>
        </div>
        <div className="flex justify-between text-gray-600">
          <span>Size:</span>
          <span className="font-medium">{(agent.size / 1024).toFixed(1)} KB</span>
        </div>
      </div>

      <div className="mt-3 pt-3 border-t grid grid-cols-2 gap-2 text-xs">
        <div className="flex items-center space-x-1">
          <Clock className="w-3 h-3 text-gray-400" />
          <span>{agent.performance.executionTime.toFixed(1)}μs</span>
        </div>
        <div className="flex items-center space-x-1">
          <MemoryStick className="w-3 h-3 text-gray-400" />
          <span>{(agent.performance.memoryUsage / 1024).toFixed(1)}KB</span>
        </div>
        <div className="flex items-center space-x-1">
          <Cpu className="w-3 h-3 text-gray-400" />
          <span>{agent.performance.cpuUsage.toFixed(0)}%</span>
        </div>
        <div className="flex items-center space-x-1">
          <Activity className="w-3 h-3 text-gray-400" />
          <span>{agent.performance.successRate.toFixed(0)}%</span>
        </div>
      </div>

      <div className="mt-3 flex space-x-2">
        <button
          onClick={(e) => {
            e.stopPropagation();
            agent.status === 'active' ? agentsApi.stopAgent(agent.id) : agentsApi.startAgent(agent.id);
          }}
          className="flex-1 px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded text-xs flex items-center justify-center space-x-1"
        >
          {agent.status === 'active' ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3" />}
          <span>{agent.status === 'active' ? 'Stop' : 'Start'}</span>
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            agentsApi.restartAgent(agent.id);
          }}
          className="flex-1 px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded text-xs flex items-center justify-center space-x-1"
        >
          <RotateCcw className="w-3 h-3" />
          <span>Restart</span>
        </button>
      </div>
    </div>
  );

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Agent Management</h1>
          <p className="text-gray-600 mt-1">247 AI Agents System</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center space-x-2">
          <Plus className="w-4 h-4" />
          <span>New Agent</span>
        </button>
      </div>

      {/* Statistics */}
      {statistics && (
        <div className="grid gap-4 md:grid-cols-5">
          <div className="bg-white p-4 rounded-lg border">
            <div className="text-2xl font-bold">{statistics.total}</div>
            <div className="text-sm text-gray-600">Total Agents</div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg border border-green-200">
            <div className="text-2xl font-bold text-green-600">{statistics.active}</div>
            <div className="text-sm text-green-700">Active</div>
          </div>
          <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
            <div className="text-2xl font-bold text-yellow-600">{statistics.idle}</div>
            <div className="text-sm text-yellow-700">Idle</div>
          </div>
          <div className="bg-red-50 p-4 rounded-lg border border-red-200">
            <div className="text-2xl font-bold text-red-600">{statistics.error}</div>
            <div className="text-sm text-red-700">Error</div>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <div className="text-2xl font-bold text-blue-600">
              {statistics.performance?.avgSuccessRate?.toFixed(0)}%
            </div>
            <div className="text-sm text-blue-700">Success Rate</div>
          </div>
        </div>
      )}

      {/* Filters and Actions */}
      <div className="bg-white p-4 rounded-lg border flex justify-between items-center">
        <div className="flex space-x-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search agents..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              className="pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <button className="px-4 py-2 border rounded-lg flex items-center space-x-2 hover:bg-gray-50">
            <Filter className="w-4 h-4" />
            <span>Filters</span>
          </button>
        </div>

        <div className="flex space-x-2">
          {selectedAgents.size > 0 && (
            <>
              <button
                onClick={() => handleBatchAction('start')}
                className="px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm"
              >
                Start ({selectedAgents.size})
              </button>
              <button
                onClick={() => handleBatchAction('stop')}
                className="px-3 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg text-sm"
              >
                Stop ({selectedAgents.size})
              </button>
              <button
                onClick={() => handleBatchAction('delete')}
                className="px-3 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm"
              >
                Delete ({selectedAgents.size})
              </button>
            </>
          )}
          <div className="flex bg-gray-100 rounded-lg">
            <button
              onClick={() => setViewMode('grid')}
              className={clsx(
                'px-3 py-2 rounded-l-lg',
                viewMode === 'grid' ? 'bg-white shadow' : 'hover:bg-gray-200'
              )}
            >
              <Grid3x3 className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={clsx(
                'px-3 py-2 rounded-r-lg',
                viewMode === 'list' ? 'bg-white shadow' : 'hover:bg-gray-200'
              )}
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Agents Grid/List */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className={clsx(
          viewMode === 'grid'
            ? 'grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'
            : 'space-y-4'
        )}>
          {agents.map(agent => (
            <AgentCard key={agent.id} agent={agent} />
          ))}
        </div>
      )}

      {/* Agent Details Modal */}
      {selectedAgent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-4">
              <h2 className="text-2xl font-bold">{selectedAgent.name}</h2>
              <button
                onClick={() => setSelectedAgent(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                <XCircle className="w-6 h-6" />
              </button>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-sm text-gray-600">Status</span>
                  <div className={clsx(
                    'mt-1 px-3 py-1 rounded-full inline-flex items-center space-x-1',
                    getStatusColor(selectedAgent.status)
                  )}>
                    {getStatusIcon(selectedAgent.status)}
                    <span>{selectedAgent.status}</span>
                  </div>
                </div>
                <div>
                  <span className="text-sm text-gray-600">Type</span>
                  <div className="mt-1 font-medium">{selectedAgent.type}</div>
                </div>
                <div>
                  <span className="text-sm text-gray-600">Version</span>
                  <div className="mt-1 font-medium">{selectedAgent.version}</div>
                </div>
                <div>
                  <span className="text-sm text-gray-600">Size</span>
                  <div className="mt-1 font-medium">{(selectedAgent.size / 1024).toFixed(2)} KB</div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-2">Performance Metrics</h3>
                <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
                  <div>
                    <span className="text-sm text-gray-600">Execution Time</span>
                    <div className="mt-1 font-medium">{selectedAgent.performance.executionTime.toFixed(2)}μs</div>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Memory Usage</span>
                    <div className="mt-1 font-medium">{(selectedAgent.performance.memoryUsage / 1024).toFixed(2)} KB</div>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">CPU Usage</span>
                    <div className="mt-1 font-medium">{selectedAgent.performance.cpuUsage.toFixed(1)}%</div>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Success Rate</span>
                    <div className="mt-1 font-medium">{selectedAgent.performance.successRate.toFixed(1)}%</div>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-2">Capabilities</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedAgent.capabilities.map((cap, index) => (
                    <span key={index} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                      {cap}
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex space-x-3 pt-4 border-t">
                <button className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg">
                  Execute
                </button>
                <button className="flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg">
                  View Logs
                </button>
                <button className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg">
                  Deploy
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
