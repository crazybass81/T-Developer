import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { Project, AgentPipeline, AgentState, AgentStatus } from '@/types'

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
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/projects`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
          }).catch(() => null)

          if (!response || !response.ok) {
            throw new Error('프로젝트 생성 실패: API 서버에 연결할 수 없습니다')
          }

          const project: Project = await response.json()
          get().addProject(project)
          get().setCurrentProject(project)
        } catch (error) {
          console.warn('API not available, using mock data:', error)
          // Use empty array if everything fails
          get().setProjects([])
          // Don't throw error to prevent app crash
        } finally {
          set({ isLoading: false })
        }
      },

      loadProjects: async () => {
        set({ isLoading: true, error: null })
        try {
          // Try to fetch from API
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/projects`)
          
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
          }
          
          get().setPipeline(pipeline)

          // Update project status
          get().updateProject(projectId, { status: 'building' })

          // Call the actual generation API endpoint with the project data
          const project = get().projects.find(p => p.id === projectId)
          if (!project) {
            throw new Error('Project not found')
          }

          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/generate`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              name: project.name,
              description: project.description,
              framework: project.framework,
              template: project.template || 'blank',
              settings: project.settings || {},
            }),
          }).catch(() => null)

          if (response && response.ok) {
            const result = await response.json()
            // Store the actual project ID from backend
            get().updateProject(projectId, { 
              status: 'completed',
              downloadId: result.project_id,
              downloadUrl: result.download_url,
            })
            
            // Update pipeline to complete
            get().setPipeline({
              ...pipeline,
              status: 'completed',
              totalProgress: 100,
              endTime: new Date(),
            })
            
            // Update all agents to complete
            for (let i = 1; i <= 9; i++) {
              get().updateAgentStatus(i, { status: 'completed', progress: 100 })
            }
          } else {
            throw new Error('프로젝트 생성 실패: 서버 응답 오류')
          }
        } catch (error) {
          get().setError(error instanceof Error ? error.message : 'Unknown error')
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