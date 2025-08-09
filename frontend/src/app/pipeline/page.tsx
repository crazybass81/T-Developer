'use client'

import { useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import { useProjectStore } from '@/stores/useProjectStore'
import { useWebSocketStore } from '@/stores/useWebSocketStore'
import { AgentPipeline } from '@/components/features/AgentPipeline'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Progress } from '@/components/ui/Progress'
import { 
  Clock, 
  Play, 
  Pause, 
  Square, 
  Download, 
  ExternalLink,
  AlertCircle,
  CheckCircle
} from 'lucide-react'

export default function PipelinePage() {
  const searchParams = useSearchParams()
  const projectId = searchParams.get('project')
  
  const { projects, currentProject, pipeline, startProjectGeneration, setCurrentProject, loadProjects } = useProjectStore()
  const { connect, disconnect, status: wsStatus } = useWebSocketStore()

  useEffect(() => {
    // Load projects if not loaded
    if (projects.length === 0) {
      loadProjects()
    }
  }, [projects.length, loadProjects])

  useEffect(() => {
    // Find and set current project
    if (projectId && projects.length > 0) {
      const project = projects.find(p => p.id === projectId)
      if (project) {
        setCurrentProject(project)
      }
    }
  }, [projectId, projects, setCurrentProject])

  useEffect(() => {
    if (projectId) {
      // Connect to WebSocket for this specific project
      connect(projectId)
      
      return () => {
        disconnect()
      }
    }
  }, [projectId, connect, disconnect])

  useEffect(() => {
    // Only start generation if explicitly requested (not automatically)
    // This prevents auto-generation when just viewing a project
    if (currentProject && !pipeline && currentProject.status === 'building') {
      // Project is already building, initialize pipeline view
      const mockPipeline = {
        id: `pipeline-${currentProject.id}`,
        projectId: currentProject.id,
        agents: [],
        status: 'running' as const,
        startTime: new Date(),
        totalProgress: 50,
      }
      // Don't auto-start, just show current state
    }
  }, [currentProject, pipeline])

  if (!currentProject) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center py-16">
          <AlertCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-2">프로젝트를 찾을 수 없습니다</h1>
          <p className="text-gray-600 mb-6">
            유효한 프로젝트 ID가 필요합니다.
          </p>
          <Button>
            프로젝트 목록으로
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {currentProject.name}
            </h1>
            <p className="text-gray-600">
              {currentProject.description}
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            <WebSocketStatus status={wsStatus} />
            {!pipeline && currentProject.status === 'draft' && (
              <Button
                onClick={() => startProjectGeneration(currentProject.id)}
                className="bg-primary-600 hover:bg-primary-700 text-white"
              >
                <Play className="w-4 h-4 mr-2" />
                프로젝트 생성 시작
              </Button>
            )}
            <ProjectControls project={currentProject} pipeline={pipeline} />
          </div>
        </div>
      </div>

      {/* Pipeline Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8">
        <Card className="lg:col-span-3">
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                전체 진행률
              </h3>
              <div className="text-2xl font-bold text-primary-600">
                {pipeline?.totalProgress || 0}%
              </div>
            </div>
            <Progress 
              value={pipeline?.totalProgress || 0} 
              size="lg"
              animated={pipeline?.status === 'running'}
            />
          </div>
        </Card>
        
        <Card>
          <div className="p-6 text-center">
            <div className="text-2xl font-bold text-gray-900 mb-1">
              {pipeline?.status === 'completed' ? (
                <CheckCircle className="w-8 h-8 text-green-500 mx-auto" />
              ) : (
                <Clock className="w-8 h-8 text-gray-400 mx-auto" />
              )}
            </div>
            <div className="text-sm text-gray-500">
              {pipeline?.status === 'running' ? '실행 중' :
               pipeline?.status === 'completed' ? '완료' :
               pipeline?.status === 'error' ? '오류 발생' : '대기 중'}
            </div>
            {pipeline?.startTime && (
              <div className="text-xs text-gray-400 mt-2">
                시작: {pipeline.startTime.toLocaleTimeString()}
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Agent Pipeline Visualization */}
      <div className="mb-8">
        <AgentPipeline />
      </div>

      {/* Logs and Output */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              실시간 로그
            </h3>
            <div className="bg-gray-900 text-green-400 p-4 rounded-lg h-64 overflow-y-auto font-mono text-sm">
              {pipeline ? (
                <LogStream pipeline={pipeline} />
              ) : (
                <div className="text-gray-500">
                  파이프라인 시작을 기다리는 중...
                </div>
              )}
            </div>
          </div>
        </Card>

        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              생성된 결과물
            </h3>
            <div className="space-y-3">
              {pipeline?.status === 'completed' ? (
                <CompletedResults project={currentProject} />
              ) : (
                <div className="text-center text-gray-500 py-8">
                  <div className="animate-pulse">
                    프로젝트 생성이 완료되면 결과물을 확인할 수 있습니다.
                  </div>
                </div>
              )}
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}

interface WebSocketStatusProps {
  status: 'disconnected' | 'connecting' | 'connected' | 'error'
}

function WebSocketStatus({ status }: WebSocketStatusProps) {
  const getStatusColor = () => {
    switch (status) {
      case 'connected': return 'bg-green-500'
      case 'connecting': return 'bg-yellow-500 animate-pulse'
      case 'error': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  const getStatusText = () => {
    switch (status) {
      case 'connected': return '실시간 연결됨'
      case 'connecting': return '연결 중...'
      case 'error': return '연결 오류'
      default: return '연결 안됨'
    }
  }

  return (
    <div className="flex items-center space-x-2 text-sm text-gray-600">
      <div className={`w-2 h-2 rounded-full ${getStatusColor()}`} />
      <span>{getStatusText()}</span>
    </div>
  )
}

interface ProjectControlsProps {
  project: any
  pipeline: any
}

function ProjectControls({ project, pipeline }: ProjectControlsProps) {
  const handlePause = () => {
    // TODO: Implement pause functionality
    console.log('Pause pipeline')
  }

  const handleStop = () => {
    // TODO: Implement stop functionality
    console.log('Stop pipeline')
  }

  const handleDownload = () => {
    // Get download URL from project
    const downloadId = project.downloadId || project.id
    const downloadUrl = project.downloadUrl || `/api/v1/download/${downloadId}`
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    
    // Open download link
    window.open(`${baseUrl}${downloadUrl}`, '_blank')
  }

  return (
    <div className="flex items-center space-x-2">
      {pipeline?.status === 'running' && (
        <>
          <Button
            variant="outline"
            size="sm"
            leftIcon={<Pause className="w-4 h-4" />}
            onClick={handlePause}
          >
            일시정지
          </Button>
          <Button
            variant="outline"
            size="sm"
            leftIcon={<Square className="w-4 h-4" />}
            onClick={handleStop}
          >
            중지
          </Button>
        </>
      )}
      
      {pipeline?.status === 'completed' && (
        <>
          <Button
            variant="outline"
            size="sm"
            leftIcon={<Download className="w-4 h-4" />}
            onClick={handleDownload}
          >
            다운로드
          </Button>
          {project.deployUrl && (
            <Button
              variant="outline"
              size="sm"
              leftIcon={<ExternalLink className="w-4 h-4" />}
              onClick={() => window.open(project.deployUrl, '_blank')}
            >
              미리보기
            </Button>
          )}
        </>
      )}
    </div>
  )
}

interface LogStreamProps {
  pipeline: any
}

function LogStream({ pipeline }: LogStreamProps) {
  const logs = [
    { timestamp: new Date(), message: '[INFO] 파이프라인 초기화 완료', level: 'info' },
    { timestamp: new Date(), message: '[INFO] NL Input Agent 시작...', level: 'info' },
    { timestamp: new Date(), message: '[SUCCESS] 자연어 처리 완료', level: 'success' },
    { timestamp: new Date(), message: '[INFO] UI Selection Agent 실행 중...', level: 'info' },
  ]

  const getLogColor = (level: string) => {
    switch (level) {
      case 'success': return 'text-green-400'
      case 'error': return 'text-red-400'
      case 'warning': return 'text-yellow-400'
      default: return 'text-green-400'
    }
  }

  return (
    <div className="space-y-1">
      {logs.map((log, index) => (
        <div key={index} className={`${getLogColor(log.level)} text-xs`}>
          <span className="text-gray-500">
            {log.timestamp.toLocaleTimeString()}
          </span>
          {' '}
          {log.message}
        </div>
      ))}
      <div className="text-gray-500 text-xs animate-pulse">
        ▋
      </div>
    </div>
  )
}

interface CompletedResultsProps {
  project: any
}

function CompletedResults({ project }: CompletedResultsProps) {
  const results = [
    { type: 'Source Code', size: '2.3 MB', status: 'ready' },
    { type: 'Build Output', size: '890 KB', status: 'ready' },
    { type: 'Documentation', size: '45 KB', status: 'ready' },
    { type: 'Deployment', size: '-', status: project.deployUrl ? 'deployed' : 'pending' },
  ]

  return (
    <div className="space-y-3">
      {results.map((result, index) => (
        <div key={index} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
          <div>
            <div className="font-medium text-gray-900">{result.type}</div>
            <div className="text-sm text-gray-500">{result.size}</div>
          </div>
          <div className="flex items-center space-x-2">
            <Badge 
              variant={result.status === 'ready' ? 'success' : 
                      result.status === 'deployed' ? 'completed' : 'warning'}
            >
              {result.status === 'ready' ? '준비됨' :
               result.status === 'deployed' ? '배포됨' : '대기중'}
            </Badge>
            {result.status === 'ready' && (
              <Button size="sm" variant="ghost">
                <Download className="w-3 h-3" />
              </Button>
            )}
            {result.status === 'deployed' && (
              <Button size="sm" variant="ghost">
                <ExternalLink className="w-3 h-3" />
              </Button>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}