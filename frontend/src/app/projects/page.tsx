'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import { API_ENDPOINTS } from '@/config/api'
import { useProjectStore } from '@/stores/useProjectStore'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Input } from '@/components/ui/Input'
import { cn, formatRelativeTime } from '@/lib/utils'
import { 
  Plus,
  Search,
  Filter,
  Grid,
  List,
  MoreHorizontal,
  Play,
  Settings,
  Download,
  Trash2,
  Copy,
  ExternalLink
} from 'lucide-react'
import * as DropdownMenu from '@radix-ui/react-dropdown-menu'

type ViewMode = 'grid' | 'list'
type FilterType = 'all' | 'active' | 'completed' | 'archived' | 'building'

export default function ProjectsPage() {
  const { projects, loadProjects, deleteProject, isLoading } = useProjectStore()
  const [searchQuery, setSearchQuery] = useState('')
  const [filter, setFilter] = useState<FilterType>('all')
  const [viewMode, setViewMode] = useState<ViewMode>('grid')

  useEffect(() => {
    loadProjects()
  }, [loadProjects])

  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         project.description.toLowerCase().includes(searchQuery.toLowerCase())
    
    const matchesFilter = filter === 'all' || project.status === filter

    return matchesSearch && matchesFilter
  })

  const getStatusVariant = (status: string) => {
    const variants: Record<string, any> = {
      draft: 'idle',
      building: 'processing',
      completed: 'completed',
      error: 'error',
      archived: 'secondary'
    }
    return variants[status] || 'idle'
  }

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      draft: '초안',
      building: '빌드 중',
      completed: '완료',
      error: '오류',
      archived: '보관됨'
    }
    return labels[status] || status
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">내 프로젝트</h1>
          <p className="text-gray-600 mt-1">
            {projects.length}개의 프로젝트 • {filteredProjects.length}개 표시 중
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-3">
          <Link href="/create">
            <Button leftIcon={<Plus className="w-4 h-4" />}>
              새 프로젝트
            </Button>
          </Link>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col lg:flex-row gap-4 mb-8">
        <div className="flex-1">
          <Input
            placeholder="프로젝트 검색..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            leftIcon={<Search className="w-4 h-4" />}
          />
        </div>

        <div className="flex gap-2">
          {/* Filter Buttons */}
          <div className="flex gap-1 bg-gray-100 rounded-lg p-1">
            {[
              { key: 'all', label: '전체' },
              { key: 'active', label: '활성' },
              { key: 'building', label: '빌드중' },
              { key: 'completed', label: '완료' },
              { key: 'archived', label: '보관' }
            ].map(({ key, label }) => (
              <button
                key={key}
                onClick={() => setFilter(key as FilterType)}
                className={cn(
                  'px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
                  filter === key
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                )}
              >
                {label}
              </button>
            ))}
          </div>

          {/* View Mode Toggle */}
          <div className="flex gap-1 bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={cn(
                'p-2 rounded-md transition-colors',
                viewMode === 'grid'
                  ? 'bg-white shadow-sm text-gray-900'
                  : 'text-gray-600 hover:text-gray-900'
              )}
            >
              <Grid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={cn(
                'p-2 rounded-md transition-colors',
                viewMode === 'list'
                  ? 'bg-white shadow-sm text-gray-900'
                  : 'text-gray-600 hover:text-gray-900'
              )}
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Projects Grid/List */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </CardHeader>
              <CardContent>
                <div className="h-3 bg-gray-200 rounded mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-2/3"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : filteredProjects.length === 0 ? (
        <EmptyState searchQuery={searchQuery} filter={filter} />
      ) : (
        <div
          className={cn(
            viewMode === 'grid'
              ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
              : 'space-y-4'
          )}
        >
          {filteredProjects.map((project, index) => (
            <motion.div
              key={project.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05, duration: 0.3 }}
            >
              {viewMode === 'grid' ? (
                <ProjectCard project={project} onDelete={deleteProject} />
              ) : (
                <ProjectListItem project={project} onDelete={deleteProject} />
              )}
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}

interface ProjectCardProps {
  project: any
  onDelete: (id: string) => void
}

function ProjectCard({ project, onDelete }: ProjectCardProps) {
  const getStatusVariant = (status: string) => {
    switch (status) {
      case 'completed': return 'success'
      case 'building': return 'warning'
      case 'error': return 'error'
      default: return 'default'
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
    <Card hover="lift" className="group">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
              {project.name}
            </h3>
            <p className="text-sm text-gray-500 mt-1 line-clamp-2">
              {project.description}
            </p>
          </div>
          
          <ProjectMenu project={project} onDelete={onDelete} />
        </div>
      </CardHeader>

      <CardContent>
        <div className="flex items-center gap-2 mb-3">
          <Badge variant={getStatusVariant(project.status)}>
            {getStatusLabel(project.status)}
          </Badge>
          <Badge variant="outline">{project.framework}</Badge>
        </div>
        
        {project.thumbnail && (
          <div className="aspect-video bg-gray-100 rounded-lg mb-3 overflow-hidden">
            <img 
              src={project.thumbnail} 
              alt={project.name}
              className="w-full h-full object-cover"
            />
          </div>
        )}
        
        <div className="text-xs text-gray-500">
          생성: {formatRelativeTime(project.createdAt)}
        </div>
      </CardContent>

      <CardFooter>
        <div className="flex gap-2 w-full">
          <Link href={`/pipeline?project=${project.id}`} className="flex-1">
            <Button size="sm" variant="outline" className="w-full">
              <Play className="w-3 h-3 mr-1" />
              열기
            </Button>
          </Link>
          {project.status === 'completed' && (
            <Button 
              size="sm" 
              variant="ghost"
              onClick={() => {
                if (project.downloadUrl) {
                  window.open(project.downloadUrl, '_blank')
                } else if (project.downloadId) {
                  window.open(API_ENDPOINTS.download(project.downloadId), '_blank')
                } else {
                  console.error('No download URL or ID available')
                }
              }}
              title="다운로드"
            >
              <Download className="w-3 h-3" />
            </Button>
          )}
          {project.deployUrl && (
            <Button 
              size="sm" 
              variant="ghost"
              onClick={() => window.open(project.deployUrl, '_blank')}
              title="미리보기"
            >
              <ExternalLink className="w-3 h-3" />
            </Button>
          )}
        </div>
      </CardFooter>
    </Card>
  )
}

function ProjectListItem({ project, onDelete }: ProjectCardProps) {
  const getStatusVariant = (status: string) => {
    switch (status) {
      case 'completed': return 'success'
      case 'building': return 'warning'
      case 'error': return 'error'
      default: return 'default'
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
    <Card className="group">
      <div className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4 flex-1">
            <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
              {project.thumbnail ? (
                <img 
                  src={project.thumbnail} 
                  alt={project.name}
                  className="w-full h-full object-cover rounded-lg"
                />
              ) : (
                <div className="w-6 h-6 bg-primary-500 rounded"></div>
              )}
            </div>
            
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
                {project.name}
              </h3>
              <p className="text-sm text-gray-500 mt-1">
                {project.description}
              </p>
            </div>
            
            <div className="flex items-center gap-2">
              <Badge variant={getStatusVariant(project.status)}>
                {getStatusLabel(project.status)}
              </Badge>
              <Badge variant="outline">{project.framework}</Badge>
            </div>
            
            <div className="text-sm text-gray-500">
              {formatRelativeTime(project.createdAt)}
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Link href={`/pipeline?project=${project.id}`}>
              <Button size="sm" variant="outline">
                <Play className="w-3 h-3 mr-1" />
                열기
              </Button>
            </Link>
            {project.deployUrl && (
              <Button 
                size="sm" 
                variant="ghost"
                onClick={() => window.open(project.deployUrl, '_blank')}
              >
                <ExternalLink className="w-3 h-3" />
              </Button>
            )}
            <ProjectMenu project={project} onDelete={onDelete} />
          </div>
        </div>
      </div>
    </Card>
  )
}

function ProjectMenu({ project, onDelete }: ProjectCardProps) {
  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <Button size="sm" variant="ghost" className="h-8 w-8 p-0">
          <MoreHorizontal className="h-4 w-4" />
        </Button>
      </DropdownMenu.Trigger>

      <DropdownMenu.Portal>
        <DropdownMenu.Content
          className="z-50 min-w-[160px] overflow-hidden rounded-md border border-gray-200 bg-white p-1 shadow-lg"
          sideOffset={4}
          align="end"
        >
          <DropdownMenu.Item className="flex cursor-pointer items-center rounded-sm px-2 py-1.5 text-sm hover:bg-gray-100">
            <Play className="mr-2 h-4 w-4" />
            열기
          </DropdownMenu.Item>
          
          <DropdownMenu.Item className="flex cursor-pointer items-center rounded-sm px-2 py-1.5 text-sm hover:bg-gray-100">
            <Settings className="mr-2 h-4 w-4" />
            설정
          </DropdownMenu.Item>
          
          <DropdownMenu.Item className="flex cursor-pointer items-center rounded-sm px-2 py-1.5 text-sm hover:bg-gray-100">
            <Copy className="mr-2 h-4 w-4" />
            복제
          </DropdownMenu.Item>
          
          {project.status === 'completed' && (
            <DropdownMenu.Item 
              className="flex cursor-pointer items-center rounded-sm px-2 py-1.5 text-sm hover:bg-gray-100"
              onClick={() => {
                if (project.downloadUrl) {
                  window.open(project.downloadUrl, '_blank')
                } else if (project.downloadId) {
                  window.open(API_ENDPOINTS.download(project.downloadId), '_blank')
                } else {
                  console.error('No download URL or ID available')
                }
              }}
            >
              <Download className="mr-2 h-4 w-4" />
              다운로드
            </DropdownMenu.Item>
          )}
          
          <DropdownMenu.Separator className="my-1 h-px bg-gray-200" />
          
          <DropdownMenu.Item
            className="flex cursor-pointer items-center rounded-sm px-2 py-1.5 text-sm text-red-600 hover:bg-red-50"
            onClick={() => onDelete(project.id)}
          >
            <Trash2 className="mr-2 h-4 w-4" />
            삭제
          </DropdownMenu.Item>
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  )
}

interface EmptyStateProps {
  searchQuery: string
  filter: FilterType
}

function EmptyState({ searchQuery, filter }: EmptyStateProps) {
  const isFiltered = searchQuery || filter !== 'all'
  
  return (
    <div className="text-center py-16">
      <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
        {isFiltered ? (
          <Search className="w-6 h-6 text-gray-400" />
        ) : (
          <Plus className="w-6 h-6 text-gray-400" />
        )}
      </div>
      
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        {isFiltered ? '검색 결과가 없습니다' : '아직 프로젝트가 없습니다'}
      </h3>
      
      <p className="text-gray-500 mb-6 max-w-md mx-auto">
        {isFiltered 
          ? '다른 검색어를 시도하거나 필터를 변경해보세요.'
          : '첫 번째 프로젝트를 만들어서 AI 에이전트의 협업을 경험해보세요.'
        }
      </p>
      
      {!isFiltered && (
        <Link href="/create">
          <Button leftIcon={<Plus className="w-4 h-4" />}>
            첫 프로젝트 만들기
          </Button>
        </Link>
      )}
    </div>
  )
}