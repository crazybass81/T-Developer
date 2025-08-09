'use client'

import React from 'react'
import { AlertTriangle, RefreshCw, Home } from 'lucide-react'
import { Button } from './Button'
import { Card } from './Card'

interface ErrorBoundaryState {
  hasError: boolean
  error?: Error
  errorInfo?: React.ErrorInfo
}

interface ErrorBoundaryProps {
  children: React.ReactNode
  fallback?: React.ComponentType<{ error?: Error; resetError: () => void }>
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  private resetTimeoutId: number | null = null

  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      error,
    }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
    
    this.setState({
      error,
      errorInfo,
    })

    // Call onError callback if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo)
    }
  }

  resetError = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined })
  }

  render() {
    if (this.state.hasError) {
      const FallbackComponent = this.props.fallback || DefaultErrorFallback
      return <FallbackComponent error={this.state.error} resetError={this.resetError} />
    }

    return this.props.children
  }
}

interface ErrorFallbackProps {
  error?: Error
  resetError: () => void
}

function DefaultErrorFallback({ error, resetError }: ErrorFallbackProps) {
  const isDevelopment = process.env.NODE_ENV === 'development'

  const handleReload = () => {
    window.location.reload()
  }

  const handleGoHome = () => {
    window.location.href = '/'
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gray-50">
      <Card className="max-w-lg w-full text-center p-8">
        <div className="flex justify-center mb-6">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
            <AlertTriangle className="w-8 h-8 text-red-600" />
          </div>
        </div>
        
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          앗! 문제가 발생했습니다
        </h1>
        
        <p className="text-gray-600 mb-6">
          예상치 못한 오류가 발생했습니다. 페이지를 새로 고침하거나 홈으로 돌아가 주세요.
        </p>

        {isDevelopment && error && (
          <div className="mb-6 p-4 bg-gray-100 rounded-lg text-left overflow-auto max-h-48">
            <h3 className="font-mono text-sm font-semibold text-red-600 mb-2">
              개발 모드 오류 정보:
            </h3>
            <pre className="text-xs text-gray-800 whitespace-pre-wrap">
              {error.name}: {error.message}
              {error.stack && `\n\n${error.stack}`}
            </pre>
          </div>
        )}
        
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Button
            onClick={resetError}
            leftIcon={<RefreshCw className="w-4 h-4" />}
            variant="primary"
          >
            다시 시도
          </Button>
          
          <Button
            onClick={handleReload}
            leftIcon={<RefreshCw className="w-4 h-4" />}
            variant="secondary"
          >
            페이지 새로고침
          </Button>
          
          <Button
            onClick={handleGoHome}
            leftIcon={<Home className="w-4 h-4" />}
            variant="ghost"
          >
            홈으로 가기
          </Button>
        </div>

        {isDevelopment && (
          <p className="mt-4 text-xs text-gray-400">
            개발 모드에서만 표시되는 오류 정보입니다.
          </p>
        )}
      </Card>
    </div>
  )
}

// Hook version for functional components
export function useErrorHandler() {
  return (error: Error, errorInfo?: React.ErrorInfo) => {
    console.error('Error caught by error handler:', error, errorInfo)
    
    // You can add error reporting logic here
    // e.g., send to analytics service, crash reporting tool, etc.
  }
}

// Simple error boundary wrapper component
interface SimpleErrorBoundaryProps {
  children: React.ReactNode
  message?: string
}

export function SimpleErrorBoundary({ children, message }: SimpleErrorBoundaryProps) {
  return (
    <ErrorBoundary
      fallback={({ error, resetError }) => (
        <div className="p-4 border border-red-200 rounded-lg bg-red-50">
          <div className="flex items-center space-x-2 text-red-700">
            <AlertTriangle className="w-4 h-4 flex-shrink-0" />
            <span className="text-sm font-medium">
              {message || '이 섹션을 불러오는 중 오류가 발생했습니다.'}
            </span>
          </div>
          {process.env.NODE_ENV === 'development' && error && (
            <pre className="mt-2 text-xs text-red-600 overflow-auto">
              {error.message}
            </pre>
          )}
          <Button
            size="sm"
            variant="ghost"
            onClick={resetError}
            className="mt-2 text-red-700 hover:text-red-800"
          >
            다시 시도
          </Button>
        </div>
      )}
    >
      {children}
    </ErrorBoundary>
  )
}