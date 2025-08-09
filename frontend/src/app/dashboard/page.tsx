'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import { useProjectStore } from '@/stores/useProjectStore'
import { Card, CardHeader, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Progress } from '@/components/ui/Progress'
import { cn, formatRelativeTime } from '@/lib/utils'
import {
  Plus,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
  Zap,
  Users,
  Code,
  Globe,
  BarChart3,
  Activity
} from 'lucide-react'

export default function DashboardPage() {
  const { projects, loadProjects, isLoading } = useProjectStore()
  const [stats, setStats] = useState({
    totalProjects: 0,
    activeProjects: 0,
    completedProjects: 0,
    totalGenerationTime: 0
  })

  useEffect(() => {
    loadProjects()
  }, [loadProjects])

  useEffect(() => {
    // Calculate stats when projects change
    if (projects.length > 0) {
      setStats({
        totalProjects: projects.length,
        activeProjects: projects.filter(p => p.status === 'building').length,
        completedProjects: projects.filter(p => p.status === 'completed').length,
        totalGenerationTime: projects.length * 3.5 // Mock average time
      })
    }
  }, [projects])

  const recentProjects = projects.slice(0, 5)
  const quickStats = [
    { label: '총 프로젝트', value: stats.totalProjects, icon: <Code className="w-5 h-5" />, color: 'text-blue-600' },
    { label: '활성 프로젝트', value: stats.activeProjects, icon: <Activity className="w-5 h-5" />, color: 'text-green-600' },
    { label: '완료된 프로젝트', value: stats.completedProjects, icon: <CheckCircle className="w-5 h-5" />, color: 'text-purple-600' },
    { label: '평균 생성 시간', value: `${stats.totalGenerationTime.toFixed(1)}분`, icon: <Clock className="w-5 h-5" />, color: 'text-orange-600' }
  ]

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">대시보드</h1>
          <p className="text-gray-600 mt-1">프로젝트 현황과 AI 에이전트 활동을 한눈에 확인하세요</p>
        </div>

        <div className="flex gap-3">
          <Link href="/create">
            <Button leftIcon={<Plus className="w-4 h-4" />}>
              새 프로젝트
            </Button>
          </Link>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {quickStats.map((stat, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1, duration: 0.5 }}
          >
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-1">{stat.label}</p>
                    <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                  </div>
                  <div className={cn('p-3 rounded-lg bg-gray-100', stat.color)}>
                    {stat.icon}
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Projects */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-900">최근 프로젝트</h2>
                <Link href="/projects">
                  <Button variant="ghost" size="sm">
                    모두 보기
                  </Button>
                </Link>
              </div>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="space-y-4">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="animate-pulse">
                      <div className="flex items-center space-x-4 p-4">
                        <div className="w-12 h-12 bg-gray-200 rounded-lg"></div>
                        <div className="flex-1">
                          <div className="h-4 bg-gray-200 rounded w-1/3 mb-2"></div>
                          <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                        </div>
                        <div className="h-6 bg-gray-200 rounded w-16"></div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : recentProjects.length === 0 ? (
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Plus className="w-6 h-6 text-gray-400" />
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">프로젝트가 없습니다</h3>
                  <p className="text-gray-500 mb-4">첫 번째 프로젝트를 만들어보세요!</p>
                  <Link href="/create">
                    <Button>프로젝트 만들기</Button>
                  </Link>
                </div>
              ) : (
                <div className="space-y-3">
                  {recentProjects.map((project, index) => (
                    <motion.div
                      key={project.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05, duration: 0.3 }}
                    >
                      <ProjectItem project={project} />
                    </motion.div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Activity Feed */}
        <div>
          <Card>
            <CardHeader>
              <h2 className="text-xl font-semibold text-gray-900">활동 피드</h2>
            </CardHeader>
            <CardContent>
              <ActivityFeed />
            </CardContent>
          </Card>
        </div>
      </div>

      {/* AI Agent Status */}
      <div className="mt-8">
        <Card>
          <CardHeader>
            <h2 className="text-xl font-semibold text-gray-900">AI 에이전트 시스템 상태</h2>
          </CardHeader>
          <CardContent>
            <AgentSystemStatus />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

interface ProjectItemProps {
  project: any
}

function ProjectItem({ project }: ProjectItemProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100'
      case 'building': return 'text-blue-600 bg-blue-100'
      case 'error': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'completed': return '완료'
      case 'building': return '빌드 중'
      case 'error': return '오류'
      case 'draft': return '초안'
      default: return status
    }
  }

  return (
    <div className="flex items-center justify-between p-4 border border-gray-100 rounded-lg hover:border-gray-200 transition-colors">
      <div className="flex items-center space-x-4">
        <div className="w-12 h-12 bg-gradient-to-br from-primary-400 to-secondary-400 rounded-lg flex items-center justify-center">
          <Code className="w-6 h-6 text-white" />
        </div>
        <div>
          <h3 className="font-medium text-gray-900">{project.name}</h3>
          <p className="text-sm text-gray-500">
            {formatRelativeTime(project.updatedAt)} • {project.framework}
          </p>
        </div>
      </div>
      
      <div className="flex items-center space-x-2">
        <Badge className={getStatusColor(project.status)}>
          {getStatusLabel(project.status)}
        </Badge>
        {project.status === 'building' && (
          <Link href={`/pipeline?project=${project.id}`}>
            <Button size="sm" variant="outline">
              모니터링
            </Button>
          </Link>
        )}
      </div>
    </div>
  )
}

function ActivityFeed() {
  const activities = [
    { 
      type: 'project_created',
      message: '새 프로젝트 "할일 관리 앱"이 생성되었습니다',
      time: '5분 전',
      icon: <Plus className="w-4 h-4" />
    },
    {
      type: 'generation_complete',
      message: 'AI 에이전트가 코드 생성을 완료했습니다',
      time: '1시간 전',
      icon: <CheckCircle className="w-4 h-4" />
    },
    {
      type: 'deployment',
      message: '프로젝트가 성공적으로 배포되었습니다',
      time: '2시간 전',
      icon: <Globe className="w-4 h-4" />
    },
    {
      type: 'error',
      message: '빌드 과정에서 오류가 발생했습니다',
      time: '3시간 전',
      icon: <AlertCircle className="w-4 h-4" />
    },
    {
      type: 'optimization',
      message: 'AI가 코드 최적화를 완료했습니다',
      time: '5시간 전',
      icon: <Zap className="w-4 h-4" />
    }
  ]

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'project_created': return 'text-blue-500'
      case 'generation_complete': return 'text-green-500'
      case 'deployment': return 'text-purple-500'
      case 'error': return 'text-red-500'
      case 'optimization': return 'text-yellow-500'
      default: return 'text-gray-500'
    }
  }

  return (
    <div className="space-y-4">
      {activities.map((activity, index) => (
        <div key={index} className="flex items-start space-x-3">
          <div className={cn('p-1 rounded-full', getActivityColor(activity.type))}>
            {activity.icon}
          </div>
          <div className="flex-1">
            <p className="text-sm text-gray-900">{activity.message}</p>
            <p className="text-xs text-gray-500 mt-1">{activity.time}</p>
          </div>
        </div>
      ))}
    </div>
  )
}

function AgentSystemStatus() {
  const agents = [
    { id: 1, name: 'NL Input Agent', status: 'active', load: 45 },
    { id: 2, name: 'UI Selection Agent', status: 'active', load: 32 },
    { id: 3, name: 'Parser Agent', status: 'idle', load: 12 },
    { id: 4, name: 'Component Decision Agent', status: 'active', load: 67 },
    { id: 5, name: 'Match Rate Agent', status: 'idle', load: 8 },
    { id: 6, name: 'Search/Call Agent', status: 'maintenance', load: 0 },
    { id: 7, name: 'Generation Agent', status: 'active', load: 89 },
    { id: 8, name: 'Service Assembly Agent', status: 'active', load: 23 },
    { id: 9, name: 'Download/Package Agent', status: 'idle', load: 5 }
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500'
      case 'idle': return 'bg-gray-400'
      case 'maintenance': return 'bg-yellow-500'
      case 'error': return 'bg-red-500'
      default: return 'bg-gray-400'
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'active': return '활성'
      case 'idle': return '대기'
      case 'maintenance': return '점검'
      case 'error': return '오류'
      default: return status
    }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {agents.map((agent) => (
        <div key={agent.id} className="p-4 border border-gray-100 rounded-lg">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <div className={cn('w-2 h-2 rounded-full', getStatusColor(agent.status))} />
              <span className="text-sm font-medium text-gray-900">{agent.name}</span>
            </div>
            <Badge variant="outline" size="sm">
              {getStatusLabel(agent.status)}
            </Badge>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-xs text-gray-500">
              <span>부하율</span>
              <span>{agent.load}%</span>
            </div>
            <Progress value={agent.load} size="sm" />
          </div>
        </div>
      ))}
    </div>
  )
}