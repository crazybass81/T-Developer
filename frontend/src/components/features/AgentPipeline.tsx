'use client'

import { useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useProjectStore } from '@/stores/useProjectStore'
import { useWebSocketStore } from '@/stores/useWebSocketStore'
import { Badge } from '@/components/ui/Badge'
import { Progress, CircularProgress } from '@/components/ui/Progress'
import { Card } from '@/components/ui/Card'
import { cn, getAgentColor, getAgentName } from '@/lib/utils'
import { type AgentState, type AgentStatusUpdate } from '@/types'
import { 
  Play, 
  Pause, 
  CheckCircle, 
  AlertCircle, 
  Clock,
  Zap,
  ArrowRight
} from 'lucide-react'

export function AgentPipeline() {
  const { pipeline, updateAgentStatus } = useProjectStore()
  const { subscribe } = useWebSocketStore()

  useEffect(() => {
    // Subscribe to agent status updates
    const unsubscribe = subscribe('agent_status', (data: AgentStatusUpdate['data']) => {
      updateAgentStatus(data.agentId, {
        status: data.status,
        progress: data.progress,
        output: data.output,
        error: data.error,
        endTime: data.status === 'completed' ? new Date() : undefined,
      })
    })

    return unsubscribe
  }, [subscribe, updateAgentStatus])

  if (!pipeline) {
    return (
      <Card className="p-8 text-center">
        <div className="text-gray-500">
          <Clock className="h-12 w-12 mx-auto mb-4" />
          <h3 className="text-lg font-medium mb-2">에이전트 파이프라인 대기 중</h3>
          <p className="text-sm">프로젝트 생성을 시작하면 AI 에이전트들이 협업을 시작합니다.</p>
        </div>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Pipeline Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">AI 에이전트 파이프라인</h2>
          <p className="text-gray-600">9개의 전문 AI 에이전트가 협업하여 프로젝트를 생성합니다</p>
        </div>
        <div className="flex items-center space-x-4">
          <Badge 
            variant={pipeline.status === 'running' ? 'processing' : pipeline.status}
            className="px-3 py-1"
          >
            {pipeline.status === 'running' && <Zap className="h-3 w-3 mr-1" />}
            {pipeline.status === 'running' ? '실행 중' : 
             pipeline.status === 'completed' ? '완료' :
             pipeline.status === 'error' ? '오류' : '대기 중'}
          </Badge>
          <div className="text-right">
            <div className="text-2xl font-bold text-gray-900">{pipeline.totalProgress}%</div>
            <div className="text-sm text-gray-500">전체 진행률</div>
          </div>
        </div>
      </div>

      {/* Overall Progress */}
      <Progress
        value={pipeline.totalProgress}
        variant={pipeline.status === 'error' ? 'error' : 'default'}
        size="lg"
        animated={pipeline.status === 'running'}
        className="w-full"
      />

      {/* Agent Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {pipeline.agents.map((agent, index) => (
          <AgentCard
            key={agent.id}
            agent={agent}
            isActive={pipeline.currentAgent === agent.id}
            isNext={pipeline.currentAgent === agent.id - 1}
          />
        ))}
      </div>

      {/* Pipeline Flow (Desktop) */}
      <div className="hidden lg:block">
        <PipelineFlow agents={pipeline.agents} currentAgent={pipeline.currentAgent} />
      </div>
    </div>
  )
}

interface AgentCardProps {
  agent: AgentState
  isActive?: boolean
  isNext?: boolean
}

function AgentCard({ agent, isActive, isNext }: AgentCardProps) {
  const getStatusIcon = () => {
    switch (agent.status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-600" />
      case 'processing':
        return <Play className="h-4 w-4 text-blue-600 animate-pulse" />
      case 'paused':
        return <Pause className="h-4 w-4 text-yellow-600" />
      default:
        return <Clock className="h-4 w-4 text-gray-400" />
    }
  }

  const getBadgeVariant = () => {
    const variants: Record<string, any> = {
      idle: 'idle',
      processing: 'processing',
      completed: 'completed',
      error: 'error',
      paused: 'paused',
    }
    return variants[agent.status] || 'idle'
  }

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card
        className={cn(
          'relative overflow-hidden transition-all duration-300',
          isActive && 'ring-2 ring-primary-500 shadow-glow',
          isNext && 'ring-1 ring-primary-300',
          agent.status === 'processing' && 'animate-pulse'
        )}
        hover={agent.status !== 'processing' ? 'lift' : 'none'}
      >
        {/* Agent Avatar */}
        <div className="flex items-center space-x-3 mb-4">
          <div className={cn(
            'w-10 h-10 rounded-lg flex items-center justify-center text-white font-semibold text-sm',
            getAgentColor(agent.id)
          )}>
            {agent.id}
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900">{getAgentName(agent.id)}</h3>
            <div className="flex items-center space-x-2 mt-1">
              {getStatusIcon()}
              <Badge variant={getBadgeVariant()} size="sm">
                {agent.status === 'processing' ? '처리 중' :
                 agent.status === 'completed' ? '완료' :
                 agent.status === 'error' ? '오류' :
                 agent.status === 'paused' ? '일시정지' : '대기'}
              </Badge>
            </div>
          </div>
        </div>

        {/* Progress */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">진행률</span>
            <span className="font-medium">{agent.progress}%</span>
          </div>
          <Progress
            value={agent.progress}
            variant={agent.status === 'error' ? 'error' : 
                    agent.status === 'completed' ? 'success' : 'default'}
            animated={agent.status === 'processing'}
          />
        </div>

        {/* Timing Info */}
        {agent.startTime && (
          <div className="mt-3 text-xs text-gray-500">
            시작: {agent.startTime.toLocaleTimeString()}
            {agent.endTime && (
              <>
                <br />
                완료: {agent.endTime.toLocaleTimeString()}
              </>
            )}
          </div>
        )}

        {/* Error Message */}
        {agent.error && (
          <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-600">
            {agent.error}
          </div>
        )}

        {/* Processing Glow Effect */}
        {agent.status === 'processing' && (
          <div className="absolute inset-0 pointer-events-none">
            <div className="absolute inset-0 rounded-lg bg-primary-500 opacity-10 animate-pulse" />
          </div>
        )}
      </Card>
    </motion.div>
  )
}

interface PipelineFlowProps {
  agents: AgentState[]
  currentAgent?: number
}

function PipelineFlow({ agents, currentAgent }: PipelineFlowProps) {
  return (
    <div className="relative">
      <div className="flex items-center justify-between">
        {agents.map((agent, index) => (
          <div key={agent.id} className="flex items-center">
            {/* Agent Node */}
            <div className="flex flex-col items-center space-y-2">
              <div
                className={cn(
                  'w-12 h-12 rounded-full flex items-center justify-center text-white font-bold border-2',
                  getAgentColor(agent.id),
                  agent.status === 'completed' && 'ring-2 ring-green-300',
                  agent.status === 'processing' && 'ring-2 ring-primary-300 animate-pulse',
                  agent.status === 'error' && 'ring-2 ring-red-300'
                )}
              >
                {agent.status === 'completed' ? (
                  <CheckCircle className="h-6 w-6" />
                ) : agent.status === 'processing' ? (
                  <CircularProgress size={24} strokeWidth={2} indeterminate />
                ) : agent.status === 'error' ? (
                  <AlertCircle className="h-6 w-6" />
                ) : (
                  agent.id
                )}
              </div>
              <div className="text-xs text-center max-w-20">
                <div className="font-medium truncate">{getAgentName(agent.id).split(' ')[0]}</div>
                <div className="text-gray-500">{agent.progress}%</div>
              </div>
            </div>

            {/* Connection Arrow */}
            {index < agents.length - 1 && (
              <div className="flex-1 px-4">
                <div className="flex items-center">
                  <div
                    className={cn(
                      'flex-1 h-0.5 transition-colors duration-500',
                      agent.status === 'completed' ? 'bg-green-300' :
                      agent.status === 'processing' ? 'bg-primary-300' :
                      'bg-gray-200'
                    )}
                  />
                  <ArrowRight
                    className={cn(
                      'h-4 w-4 ml-1 transition-colors duration-500',
                      agent.status === 'completed' ? 'text-green-500' :
                      agent.status === 'processing' ? 'text-primary-500' :
                      'text-gray-400'
                    )}
                  />
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}