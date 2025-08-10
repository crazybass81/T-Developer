import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { Project, AgentPipeline, AgentState, AgentStatus } from '@/types'
import { API_ENDPOINTS, handleApiResponse } from '@/config/api'

interface ProjectState {
  // Projects
  projects: Project[]
  currentProject: Project | null
  isLoading: boolean
  error: string | null
  
  // Agent Pipeline
  pipeline: AgentPipeline | null
  
  // Actions
  setProjects: (projects: Project[]) => void
  addProject: (project: Project) => void
  updateProject: (id: string, updates: Partial<Project>) => void
  deleteProject: (id: string) => void
  setCurrentProject: (project: Project | null) => void
  
  // Agent actions
  setPipeline: (pipeline: AgentPipeline) => void
  updateAgentStatus: (agentId: number, status: Partial<AgentState>) => void
  resetPipeline: () => void
  
  // Loading and error states
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  
  // API actions
  createProject: (data: Omit<Project, 'id' | 'createdAt' | 'updatedAt'>) => Promise<void>
  loadProjects: () => Promise<void>
  startProjectGeneration: (projectId: string) => Promise<void>
}

const initialAgentStates: AgentState[] = [
  { id: 1, name: 'NL Input Agent', status: 'idle', progress: 0 },
  { id: 2, name: 'UI Selection Agent', status: 'idle', progress: 0 },
  { id: 3, name: 'Parser Agent', status: 'idle', progress: 0 },
  { id: 4, name: 'Component Decision Agent', status: 'idle', progress: 0 },
  { id: 5, name: 'Match Rate Agent', status: 'idle', progress: 0 },
  { id: 6, name: 'Search/Call Agent', status: 'idle', progress: 0 },
  { id: 7, name: 'Generation Agent', status: 'idle', progress: 0 },
  { id: 8, name: 'Service Assembly Agent', status: 'idle', progress: 0 },
  { id: 9, name: 'Download/Package Agent', status: 'idle', progress: 0 },
]

export const useProjectStore = create<ProjectState>()(
  devtools(
    (set, get) => ({
      // Initial state
      projects: [],
      currentProject: null,
      isLoading: false,
      error: null,
      pipeline: null,

      // Project actions
      setProjects: (projects) => set({ projects }),
      
      addProject: (project) =>
        set((state) => ({
          projects: [project, ...state.projects],
        })),

      updateProject: (id, updates) =>
        set((state) => ({
          projects: state.projects.map((project) =>
            project.id === id ? { ...project, ...updates } : project
          ),
          currentProject:
            state.currentProject?.id === id
              ? { ...state.currentProject, ...updates }
              : state.currentProject,
        })),

      deleteProject: (id) =>
        set((state) => ({
          projects: state.projects.filter((project) => project.id !== id),
          currentProject:
            state.currentProject?.id === id ? null : state.currentProject,
        })),

      setCurrentProject: (project) => set({ currentProject: project }),

      // Agent pipeline actions
      setPipeline: (pipeline) => set({ pipeline }),

      updateAgentStatus: (agentId, statusUpdate) =>
        set((state) => {
          if (!state.pipeline) return state

          const updatedAgents = state.pipeline.agents.map((agent) =>
            agent.id === agentId ? { ...agent, ...statusUpdate } : agent
          )

          // Calculate total progress
          const totalProgress = Math.round(
            updatedAgents.reduce((sum, agent) => sum + agent.progress, 0) / 9
          )

          // Determine pipeline status
          let pipelineStatus = state.pipeline.status
          if (updatedAgents.some((agent) => agent.status === 'error')) {
            pipelineStatus = 'error'
          } else if (updatedAgents.every((agent) => agent.status === 'completed')) {
            pipelineStatus = 'completed'
          } else if (updatedAgents.some((agent) => agent.status === 'processing')) {
            pipelineStatus = 'running'
          }

          return {
            pipeline: {
              ...state.pipeline,
              agents: updatedAgents,
              totalProgress,
              status: pipelineStatus,
              endTime: pipelineStatus === 'completed' ? new Date() : state.pipeline.endTime,
            },
          }
        }),

      resetPipeline: () =>
        set((state) => ({
          pipeline: state.pipeline
            ? {
                ...state.pipeline,
                agents: initialAgentStates,
                status: 'idle',
                totalProgress: 0,
                currentAgent: undefined,
                startTime: undefined,
                endTime: undefined,
              }
            : null,
        })),

      // Loading and error actions
      setLoading: (loading) => set({ isLoading: loading }),
      setError: (error) => set({ error }),

      // API actions
      createProject: async (data) => {
        set({ isLoading: true, error: null })
        try {
          // First create a local project for tracking
          const localProject: Project = {
            id: `project-${Date.now()}`,
            ...data,
            createdAt: new Date(),
            updatedAt: new Date(),
          }
          
          get().addProject(localProject)
          get().setCurrentProject(localProject)
          
          // Return the local project ID for navigation
          return localProject.id
        } catch (error) {
          console.warn('Project creation error:', error)
          get().setError(error instanceof Error ? error.message : 'Unknown error')
          throw error
        } finally {
          set({ isLoading: false })
        }
      },

      loadProjects: async () => {
        set({ isLoading: true, error: null })
        try {
          // Try to fetch from API
          const response = await fetch(API_ENDPOINTS.projects)
          
          if (!response.ok) {
            throw new Error('프로젝트 목록을 불러올 수 없습니다')
          }

          const projects: Project[] = await response.json()
          get().setProjects(projects || [])
        } catch (error) {
          get().setError(error instanceof Error ? error.message : 'Unknown error')
        } finally {
          set({ isLoading: false })
        }
      },

      startProjectGeneration: async (projectId) => {
        set({ isLoading: true, error: null })
        try {
          // Initialize pipeline
          const pipeline: AgentPipeline = {
            id: `pipeline-${projectId}`,
            projectId,
            agents: [...initialAgentStates],
            status: 'running',
            startTime: new Date(),
            totalProgress: 0,
            logs: [],
          }
          
          get().setPipeline(pipeline)

          // Update project status
          get().updateProject(projectId, { status: 'building' })

          // Get the project data
          const project = get().projects.find(p => p.id === projectId)
          if (!project) {
            throw new Error('Project not found')
          }

          // Add initial log
          const addLog = (message: string, level: 'info' | 'success' | 'error' = 'info') => {
            const currentPipeline = get().pipeline
            if (currentPipeline) {
              const logs = [...(currentPipeline.logs || []), {
                timestamp: new Date().toISOString(),
                message,
                level
              }]
              get().setPipeline({ ...currentPipeline, logs })
            }
          }

          addLog('🚀 프로젝트 생성을 시작합니다...', 'info')
          addLog(`프로젝트: ${project.name}`, 'info')
          addLog(`프레임워크: ${project.framework}`, 'info')

          // Call the actual generate API
          console.log('Using API endpoint:', API_ENDPOINTS.generate)
          
          // 타임아웃을 30초로 설정
          const controller = new AbortController()
          const timeoutId = setTimeout(() => controller.abort(), 30000) // 30초 타임아웃
          
          const response = await fetch(API_ENDPOINTS.generate, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            signal: controller.signal,
            body: JSON.stringify({
              name: project.name,
              description: project.description,
              framework: project.framework,
              template: project.template || 'blank',
              settings: project.settings || {},
              // API 필수 필드 추가
              user_input: project.description,
              project_name: project.name,
              project_type: project.framework,
              features: project.settings?.features || []
            }),
          }).catch(error => {
            clearTimeout(timeoutId)
            if (error.name === 'AbortError') {
              throw new Error('요청 시간 초과 (30초). 다시 시도해주세요.')
            }
            console.error('Fetch error:', error)
            throw new Error(`네트워크 오류: ${error.message}`)
          }).finally(() => {
            clearTimeout(timeoutId)
          })

          if (!response.ok) {
            throw new Error('백엔드 API 응답 오류')
          }

          const result = await response.json()
          
          // Simulate agent progress with real logs
          const agents = [
            'NL Input Agent - 자연어 분석 중...',
            'UI Selection Agent - UI 프레임워크 선택 중...',
            'Parser Agent - 요구사항 파싱 중...',
            'Component Decision Agent - 컴포넌트 구조 결정 중...',
            'Match Rate Agent - 템플릿 매칭 중...',
            'Search Agent - 최적 솔루션 검색 중...',
            'Generation Agent - 코드 생성 중...',
            'Assembly Agent - 프로젝트 조립 중...',
            'Download Agent - 다운로드 패키지 준비 중...'
          ]

          for (let i = 0; i < agents.length; i++) {
            addLog(agents[i], 'info')
            get().updateAgentStatus(i + 1, { status: 'processing', progress: 0 })
            
            // Simulate progress
            for (let p = 0; p <= 100; p += 20) {
              await new Promise(resolve => setTimeout(resolve, 100))
              get().updateAgentStatus(i + 1, { status: 'processing', progress: p })
            }
            
            get().updateAgentStatus(i + 1, { status: 'completed', progress: 100 })
            addLog(`✅ ${agents[i].split(' - ')[0]} 완료`, 'success')
          }

          // Update project with actual backend data
          get().updateProject(projectId, {
            status: 'completed',
            downloadId: result.project_id,
            downloadUrl: API_ENDPOINTS.download(result.project_id),
          })

          // Update pipeline to complete
          get().setPipeline({
            ...get().pipeline!,
            status: 'completed',
            totalProgress: 100,
            endTime: new Date(),
          })

          addLog('🎉 프로젝트 생성이 완료되었습니다!', 'success')
          addLog(`다운로드 준비 완료: ${result.project_id}`, 'info')

        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Unknown error'
          get().setError(errorMessage)
          
          // Add error log
          const currentPipeline = get().pipeline
          if (currentPipeline) {
            const logs = [...(currentPipeline.logs || []), {
              timestamp: new Date().toISOString(),
              message: `❌ 오류 발생: ${errorMessage}`,
              level: 'error'
            }]
            get().setPipeline({ ...currentPipeline, logs, status: 'error' })
          }
          
          get().resetPipeline()
          console.error('Generation error:', error)
        } finally {
          set({ isLoading: false })
        }
      },
    }),
    {
      name: 'project-store',
    }
  )
)