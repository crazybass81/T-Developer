'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { useProjectStore } from '@/stores/useProjectStore'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Badge } from '@/components/ui/Badge'
import { cn } from '@/lib/utils'
import { 
  MessageCircle,
  Sparkles,
  ArrowRight,
  ArrowLeft,
  Lightbulb,
  Code,
  Palette,
  Zap
} from 'lucide-react'

type Step = 'idea' | 'details' | 'preferences'

const frameworks = [
  { id: 'react', name: 'React', description: '가장 인기있는 JavaScript 라이브러리' },
  { id: 'nextjs', name: 'Next.js', description: 'React 기반 풀스택 프레임워크' },
  { id: 'vue', name: 'Vue.js', description: '직관적이고 배우기 쉬운 프레임워크' },
  { id: 'svelte', name: 'Svelte', description: '컴파일 시점에 최적화되는 프레임워크' }
]

const templates = [
  { id: 'blank', name: '빈 프로젝트', description: '처음부터 자유롭게 시작' },
  { id: 'dashboard', name: '대시보드', description: '관리자 패널 및 분석 화면' },
  { id: 'ecommerce', name: '이커머스', description: '온라인 쇼핑몰' },
  { id: 'blog', name: '블로그', description: '콘텐츠 관리 시스템' },
  { id: 'portfolio', name: '포트폴리오', description: '개인/회사 소개 사이트' },
  { id: 'todo', name: '할일 관리', description: '작업 추적 및 관리 도구' }
]

const suggestions = [
  '간단한 할일 관리 앱을 만들어주세요',
  '온라인 쇼핑몰을 만들고 싶어요',
  '개인 포트폴리오 웹사이트가 필요해요',
  '블로그 플랫폼을 개발하고 싶습니다',
  '관리자 대시보드를 만들어주세요'
]

export default function CreateProjectPage() {
  const [currentStep, setCurrentStep] = useState<Step>('idea')
  const [projectData, setProjectData] = useState({
    name: '',
    description: '',
    idea: '',
    framework: 'react',
    template: 'blank',
    features: [] as string[]
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  
  const { createProject } = useProjectStore()
  const router = useRouter()

  const handleNext = () => {
    if (currentStep === 'idea') setCurrentStep('details')
    else if (currentStep === 'details') setCurrentStep('preferences')
  }

  const handleBack = () => {
    if (currentStep === 'details') setCurrentStep('idea')
    else if (currentStep === 'preferences') setCurrentStep('details')
  }

  const handleSubmit = async () => {
    setIsSubmitting(true)
    try {
      await createProject({
        name: projectData.name || '새 프로젝트',
        description: projectData.description || projectData.idea.slice(0, 100),
        status: 'draft' as const,
        framework: projectData.framework as any,
        template: projectData.template,
        userId: 'user-1', // TODO: Get from auth
        settings: {
          theme: 'light' as const,
          language: 'typescript' as const,
          cssFramework: 'tailwind' as const,
          buildTool: 'vite' as const,
          packageManager: 'npm' as const,
          features: projectData.features
        }
      })
      router.push('/projects')
    } catch (error) {
      console.error('Failed to create project:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const canProceed = () => {
    switch (currentStep) {
      case 'idea':
        return projectData.idea.trim().length > 10
      case 'details':
        return projectData.name.trim().length > 0
      case 'preferences':
        return true
      default:
        return false
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="inline-flex items-center space-x-2 bg-white/80 backdrop-blur-sm border border-primary-200 rounded-full px-4 py-2 mb-4">
              <Sparkles className="w-4 h-4 text-primary-500" />
              <span className="text-sm font-medium text-primary-700">
                AI 에이전트와 함께 프로젝트 생성
              </span>
            </div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              새 프로젝트 만들기
            </h1>
            <p className="text-lg text-gray-600">
              자연어로 아이디어를 설명하면 AI가 완전한 앱을 만들어드립니다
            </p>
          </motion.div>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-center mb-12">
          <div className="flex items-center space-x-4">
            {[
              { key: 'idea', label: '아이디어', icon: <Lightbulb className="w-4 h-4" /> },
              { key: 'details', label: '상세정보', icon: <MessageCircle className="w-4 h-4" /> },
              { key: 'preferences', label: '환경설정', icon: <Code className="w-4 h-4" /> }
            ].map((step, index) => (
              <div key={step.key} className="flex items-center">
                <div
                  className={cn(
                    'flex items-center justify-center w-10 h-10 rounded-full border-2 transition-colors',
                    currentStep === step.key || (index === 0 && currentStep === 'details') || (index <= 1 && currentStep === 'preferences')
                      ? 'bg-primary-500 border-primary-500 text-white'
                      : 'bg-white border-gray-200 text-gray-400'
                  )}
                >
                  {step.icon}
                </div>
                <span
                  className={cn(
                    'ml-2 text-sm font-medium transition-colors',
                    currentStep === step.key
                      ? 'text-primary-600'
                      : 'text-gray-500'
                  )}
                >
                  {step.label}
                </span>
                {index < 2 && (
                  <div className="w-8 h-px bg-gray-200 mx-4" />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Step Content */}
        <div className="max-w-2xl mx-auto">
          {currentStep === 'idea' && (
            <IdeaStep
              value={projectData.idea}
              onChange={(idea) => setProjectData({ ...projectData, idea })}
              suggestions={suggestions}
            />
          )}

          {currentStep === 'details' && (
            <DetailsStep
              name={projectData.name}
              description={projectData.description}
              template={projectData.template}
              onNameChange={(name) => setProjectData({ ...projectData, name })}
              onDescriptionChange={(description) => setProjectData({ ...projectData, description })}
              onTemplateChange={(template) => setProjectData({ ...projectData, template })}
              templates={templates}
            />
          )}

          {currentStep === 'preferences' && (
            <PreferencesStep
              framework={projectData.framework}
              features={projectData.features}
              onFrameworkChange={(framework) => setProjectData({ ...projectData, framework })}
              onFeaturesChange={(features) => setProjectData({ ...projectData, features })}
              frameworks={frameworks}
            />
          )}
        </div>

        {/* Navigation */}
        <div className="flex justify-between items-center mt-12 max-w-2xl mx-auto">
          <Button
            variant="ghost"
            leftIcon={<ArrowLeft className="w-4 h-4" />}
            onClick={handleBack}
            disabled={currentStep === 'idea'}
          >
            이전
          </Button>

          <div className="flex items-center space-x-1">
            {['idea', 'details', 'preferences'].map((step, index) => (
              <div
                key={step}
                className={cn(
                  'w-2 h-2 rounded-full transition-colors',
                  (currentStep === step || 
                   (index === 0 && (currentStep === 'details' || currentStep === 'preferences')) ||
                   (index === 1 && currentStep === 'preferences'))
                    ? 'bg-primary-500'
                    : 'bg-gray-200'
                )}
              />
            ))}
          </div>

          {currentStep === 'preferences' ? (
            <Button
              onClick={handleSubmit}
              loading={isSubmitting}
              disabled={!canProceed() || isSubmitting}
              rightIcon={<Zap className="w-4 h-4" />}
            >
              프로젝트 생성
            </Button>
          ) : (
            <Button
              onClick={handleNext}
              disabled={!canProceed()}
              rightIcon={<ArrowRight className="w-4 h-4" />}
            >
              다음
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}

interface IdeaStepProps {
  value: string
  onChange: (value: string) => void
  suggestions: string[]
}

function IdeaStep({ value, onChange, suggestions }: IdeaStepProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card>
        <CardHeader>
          <h2 className="text-2xl font-semibold text-gray-900">
            어떤 앱을 만들고 싶으신가요?
          </h2>
          <p className="text-gray-600">
            자연어로 자유롭게 설명해주세요. AI가 이해하고 완벽한 앱을 만들어드립니다.
          </p>
        </CardHeader>

        <CardContent>
          <div className="space-y-4">
            <div>
              <textarea
                className="w-full h-32 p-4 border border-gray-200 rounded-lg resize-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="예: 할일을 추가하고 완료 상태를 관리할 수 있는 간단한 할일 관리 앱을 만들어주세요. 카테고리별로 분류하고 우선순위를 설정할 수 있었으면 좋겠어요."
                value={value}
                onChange={(e) => onChange(e.target.value)}
              />
            </div>

            <div>
              <p className="text-sm font-medium text-gray-700 mb-3">
                💡 아이디어가 필요하신가요? 아래 예시를 클릭해보세요
              </p>
              <div className="grid gap-2">
                {suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => onChange(suggestion)}
                    className="p-3 text-left border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors text-sm"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>

            {value.length > 0 && (
              <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center text-green-700 text-sm">
                  <Sparkles className="w-4 h-4 mr-2" />
                  {value.length < 20 
                    ? '조금 더 자세히 설명해주시면 더 좋은 결과를 얻을 수 있어요!'
                    : '훌륭해요! AI가 이해할 수 있을 만큼 충분히 설명해주셨네요.'
                  }
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

interface DetailsStepProps {
  name: string
  description: string
  template: string
  onNameChange: (name: string) => void
  onDescriptionChange: (description: string) => void
  onTemplateChange: (template: string) => void
  templates: Array<{ id: string; name: string; description: string }>
}

function DetailsStep({ 
  name, 
  description, 
  template, 
  onNameChange, 
  onDescriptionChange, 
  onTemplateChange,
  templates 
}: DetailsStepProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      <Card>
        <CardHeader>
          <h2 className="text-2xl font-semibold text-gray-900">
            프로젝트 세부 정보
          </h2>
          <p className="text-gray-600">
            프로젝트의 이름과 설명을 입력해주세요.
          </p>
        </CardHeader>

        <CardContent className="space-y-4">
          <Input
            label="프로젝트 이름"
            placeholder="나만의 할일 관리 앱"
            value={name}
            onChange={(e) => onNameChange(e.target.value)}
            required
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              프로젝트 설명 (선택사항)
            </label>
            <textarea
              className="w-full h-24 p-3 border border-gray-200 rounded-lg resize-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="프로젝트에 대한 간단한 설명을 입력해주세요..."
              value={description}
              onChange={(e) => onDescriptionChange(e.target.value)}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <h3 className="text-xl font-semibold text-gray-900">
            시작 템플릿 선택
          </h3>
          <p className="text-gray-600">
            프로젝트 유형에 맞는 템플릿을 선택하면 더 빠르게 시작할 수 있어요.
          </p>
        </CardHeader>

        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {templates.map((temp) => (
              <button
                key={temp.id}
                onClick={() => onTemplateChange(temp.id)}
                className={cn(
                  'p-4 border-2 rounded-lg text-left transition-colors',
                  template === temp.id
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                )}
              >
                <h4 className="font-medium text-gray-900 mb-1">
                  {temp.name}
                </h4>
                <p className="text-sm text-gray-600">
                  {temp.description}
                </p>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

interface PreferencesStepProps {
  framework: string
  features: string[]
  onFrameworkChange: (framework: string) => void
  onFeaturesChange: (features: string[]) => void
  frameworks: Array<{ id: string; name: string; description: string }>
}

function PreferencesStep({ 
  framework, 
  features, 
  onFrameworkChange, 
  onFeaturesChange,
  frameworks 
}: PreferencesStepProps) {
  const availableFeatures = [
    'TypeScript',
    'Dark Mode',
    'Authentication',
    'Database Integration',
    'API Integration',
    'Real-time Updates',
    'Mobile Responsive',
    'PWA Support'
  ]

  const toggleFeature = (feature: string) => {
    if (features.includes(feature)) {
      onFeaturesChange(features.filter(f => f !== feature))
    } else {
      onFeaturesChange([...features, feature])
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      <Card>
        <CardHeader>
          <h2 className="text-2xl font-semibold text-gray-900">
            기술 스택 선택
          </h2>
          <p className="text-gray-600">
            프로젝트에 사용할 프레임워크를 선택해주세요.
          </p>
        </CardHeader>

        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {frameworks.map((fw) => (
              <button
                key={fw.id}
                onClick={() => onFrameworkChange(fw.id)}
                className={cn(
                  'p-4 border-2 rounded-lg text-left transition-colors',
                  framework === fw.id
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                )}
              >
                <h4 className="font-medium text-gray-900 mb-1">
                  {fw.name}
                </h4>
                <p className="text-sm text-gray-600">
                  {fw.description}
                </p>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <h3 className="text-xl font-semibold text-gray-900">
            추가 기능 (선택사항)
          </h3>
          <p className="text-gray-600">
            프로젝트에 포함할 기능들을 선택해주세요.
          </p>
        </CardHeader>

        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {availableFeatures.map((feature) => (
              <label
                key={feature}
                className="flex items-center space-x-2 cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={features.includes(feature)}
                  onChange={() => toggleFeature(feature)}
                  className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                />
                <span className="text-sm text-gray-700">{feature}</span>
              </label>
            ))}
          </div>

          {features.length > 0 && (
            <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-700">
                선택된 기능: {features.join(', ')}
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}