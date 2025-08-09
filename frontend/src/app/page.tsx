'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { 
  Zap, 
  Sparkles, 
  Code, 
  Rocket,
  Users,
  Globe,
  ArrowRight,
  Play,
  Check,
  Star
} from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="overflow-hidden">
      {/* Hero Section */}
      <HeroSection />
      
      {/* Features Section */}
      <FeaturesSection />
      
      {/* Interactive Demo Section */}
      <DemoSection />
      
      {/* Agent Pipeline Preview */}
      <AgentSection />
      
      {/* Testimonials/Stats */}
      <StatsSection />
      
      {/* CTA Section */}
      <CTASection />
    </div>
  )
}

function HeroSection() {
  return (
    <section className="relative pt-20 pb-32 overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary-50 via-white to-secondary-50" />
      <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))]" />
      
      <div className="relative container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center max-w-4xl mx-auto"
        >
          {/* Hero Badge */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="inline-flex items-center space-x-2 bg-white/80 backdrop-blur-sm border border-primary-200 rounded-full px-4 py-2 mb-8"
          >
            <Sparkles className="w-4 h-4 text-primary-500" />
            <span className="text-sm font-medium text-primary-700">
              9개의 AI 에이전트가 협업하는 차세대 개발 플랫폼
            </span>
          </motion.div>

          {/* Main Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.8 }}
            className="text-5xl md:text-7xl font-bold font-display mb-6 text-gray-900 tracking-tight"
          >
            자연어로 앱을 만드는
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-500 to-secondary-500">
              가장 빠른 방법
            </span>
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.8 }}
            className="text-xl md:text-2xl text-gray-600 mb-10 max-w-3xl mx-auto leading-relaxed"
          >
            복잡한 코딩 없이 <strong>자연어 대화만으로</strong> 완전한 웹 애플리케이션을 생성하세요. 
            AWS와 OpenAI의 첨단 기술이 만든 혁신적인 개발 경험을 제공합니다.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.8 }}
            className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6"
          >
            <Button
              size="xl"
              className="w-full sm:w-auto shadow-lg hover:shadow-xl"
              rightIcon={<ArrowRight className="w-5 h-5" />}
            >
              무료로 시작하기
            </Button>
            
            <Button
              size="xl"
              variant="ghost"
              className="w-full sm:w-auto group"
              leftIcon={<Play className="w-5 h-5 group-hover:scale-110 transition-transform" />}
            >
              데모 보기
            </Button>
          </motion.div>

          {/* Social Proof */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8, duration: 0.8 }}
            className="mt-12 flex items-center justify-center space-x-8 text-sm text-gray-500"
          >
            <div className="flex items-center space-x-2">
              <div className="flex -space-x-1">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div key={i} className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-400 to-secondary-400 border-2 border-white" />
                ))}
              </div>
              <span>1,000+ 개발자들이 사용 중</span>
            </div>
            <div className="flex items-center space-x-1">
              <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
              <span>4.9/5 만족도</span>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}

function FeaturesSection() {
  const features = [
    {
      icon: <Zap className="w-6 h-6" />,
      title: '초고속 개발',
      description: '기존 개발 시간의 90%를 단축하여 아이디어를 즉시 현실로 만들어보세요.',
      color: 'from-yellow-400 to-orange-500'
    },
    {
      icon: <Users className="w-6 h-6" />,
      title: '9개 AI 에이전트',
      description: '각각의 전문 분야를 가진 AI 에이전트들이 협업하여 완벽한 앱을 제작합니다.',
      color: 'from-primary-400 to-secondary-500'
    },
    {
      icon: <Code className="w-6 h-6" />,
      title: '프로덕션 품질',
      description: '실제 서비스에 바로 배포할 수 있는 고품질 코드를 자동으로 생성합니다.',
      color: 'from-green-400 to-emerald-500'
    },
    {
      icon: <Globe className="w-6 h-6" />,
      title: '원클릭 배포',
      description: 'Vercel, AWS, Netlify 등 다양한 플랫폼으로 즉시 배포가 가능합니다.',
      color: 'from-purple-400 to-pink-500'
    }
  ]

  return (
    <section className="py-24 bg-white">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <Badge variant="secondary" className="mb-4">
            핵심 기능
          </Badge>
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            왜 T-Developer를 선택해야 할까요?
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            복잡한 개발 과정을 단순화하고, AI의 힘으로 누구나 앱을 만들 수 있게 합니다.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1, duration: 0.5 }}
            >
              <Card className="p-8 h-full" hover="lift">
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${feature.color} flex items-center justify-center text-white mb-6`}>
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {feature.description}
                </p>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

function DemoSection() {
  const steps = [
    '자연어로 앱 아이디어 설명',
    'AI가 요구사항 분석 및 설계',
    '9개 에이전트의 협업 프로세스',
    '완성된 앱 코드 생성 및 배포'
  ]

  return (
    <section className="py-24 bg-gray-50">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <Badge variant="outline" className="mb-4">
              실시간 데모
            </Badge>
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              간단한 대화로
              <br />
              <span className="text-primary-600">완벽한 앱 완성</span>
            </h2>
            <p className="text-lg text-gray-600 mb-8">
              "할일 관리 앱을 만들어주세요"라고 말하는 것만으로도 
              완전한 기능을 갖춘 웹 애플리케이션이 생성됩니다.
            </p>

            <div className="space-y-4 mb-8">
              {steps.map((step, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1, duration: 0.5 }}
                  className="flex items-center space-x-3"
                >
                  <div className="w-6 h-6 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm font-semibold">
                    {index + 1}
                  </div>
                  <span className="text-gray-700">{step}</span>
                </motion.div>
              ))}
            </div>

            <Button size="lg" rightIcon={<ArrowRight className="w-4 h-4" />}>
              지금 체험해보기
            </Button>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <Card className="p-0 overflow-hidden shadow-2xl">
              <div className="bg-gray-800 p-4 flex items-center space-x-2">
                <div className="w-3 h-3 bg-red-400 rounded-full"></div>
                <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
                <div className="w-3 h-3 bg-green-400 rounded-full"></div>
                <div className="flex-1 text-center">
                  <span className="text-white text-sm">T-Developer</span>
                </div>
              </div>
              
              <div className="p-6 bg-white min-h-96">
                {/* Demo content would go here */}
                <div className="text-center py-20 text-gray-500">
                  <Play className="w-16 h-16 mx-auto mb-4 text-primary-500" />
                  <p className="text-lg">Interactive Demo</p>
                  <p className="text-sm">실시간 앱 생성 과정을 확인하세요</p>
                </div>
              </div>
            </Card>
          </motion.div>
        </div>
      </div>
    </section>
  )
}

function AgentSection() {
  const agents = [
    { id: 1, name: 'NL Input', description: '자연어 처리' },
    { id: 2, name: 'UI Selection', description: 'UI/UX 설계' },
    { id: 3, name: 'Parser', description: '코드 분석' },
    { id: 4, name: 'Component', description: '컴포넌트 결정' },
    { id: 5, name: 'Match Rate', description: '매칭률 계산' },
    { id: 6, name: 'Search', description: '라이브러리 검색' },
    { id: 7, name: 'Generation', description: '코드 생성' },
    { id: 8, name: 'Assembly', description: '서비스 조합' },
    { id: 9, name: 'Package', description: '빌드 & 배포' }
  ]

  return (
    <section className="py-24 bg-white">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <Badge variant="secondary" className="mb-4">
            AI 에이전트 시스템
          </Badge>
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            9개의 전문 AI가 함께 일합니다
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            각각 다른 전문 분야를 담당하는 AI 에이전트들이 순차적으로 협업하여 완벽한 애플리케이션을 만들어냅니다.
          </p>
        </motion.div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-12">
          {agents.map((agent, index) => (
            <motion.div
              key={agent.id}
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.05, duration: 0.3 }}
            >
              <Card className="text-center p-4" hover="lift">
                <div className={`w-12 h-12 mx-auto mb-3 rounded-lg flex items-center justify-center text-white font-bold agent-gradient-${agent.id}`}>
                  {agent.id}
                </div>
                <h4 className="font-semibold text-gray-900 text-sm mb-1">
                  {agent.name}
                </h4>
                <p className="text-xs text-gray-500">
                  {agent.description}
                </p>
              </Card>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center"
        >
          <Button
            variant="outline"
            size="lg"
            rightIcon={<ArrowRight className="w-4 h-4" />}
          >
            에이전트 상세 보기
          </Button>
        </motion.div>
      </div>
    </section>
  )
}

function StatsSection() {
  const stats = [
    { number: '10,000+', label: '생성된 앱' },
    { number: '1,000+', label: '활성 사용자' },
    { number: '99.9%', label: '가동 시간' },
    { number: '< 5분', label: '평균 생성 시간' }
  ]

  return (
    <section className="py-24 bg-gradient-to-r from-primary-600 to-secondary-600 text-white">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center mb-12"
        >
          <h2 className="text-4xl font-bold mb-4">
            검증된 성능과 신뢰성
          </h2>
          <p className="text-xl opacity-90">
            전 세계 개발자들이 신뢰하는 플랫폼
          </p>
        </motion.div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {stats.map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1, duration: 0.5 }}
              className="text-center"
            >
              <div className="text-4xl md:text-5xl font-bold mb-2">
                {stat.number}
              </div>
              <div className="text-lg opacity-80">
                {stat.label}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

function CTASection() {
  return (
    <section className="py-24 bg-gray-900 text-white">
      <div className="container mx-auto px-4 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="max-w-4xl mx-auto"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            준비되셨나요?
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-secondary-400">
              첫 번째 앱을 만들어보세요
            </span>
          </h2>
          
          <p className="text-xl text-gray-300 mb-10">
            복잡한 설정이나 결제 없이 지금 바로 시작하세요. 
            5분 안에 첫 번째 앱을 완성할 수 있습니다.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
            <Button
              size="xl"
              className="w-full sm:w-auto bg-white text-gray-900 hover:bg-gray-100"
              rightIcon={<Rocket className="w-5 h-5" />}
            >
              무료로 시작하기
            </Button>
            
            <Button
              size="xl"
              variant="ghost"
              className="w-full sm:w-auto text-white border-white hover:bg-white/10"
            >
              요금제 보기
            </Button>
          </div>

          <div className="mt-8 text-sm text-gray-400">
            신용카드 불필요 • 즉시 시작 • 언제든지 취소 가능
          </div>
        </motion.div>
      </div>
    </section>
  )
}