'use client'

import { forwardRef } from 'react'
import { cn } from '@/lib/utils'

export interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value?: number
  max?: number
  variant?: 'default' | 'success' | 'warning' | 'error'
  size?: 'sm' | 'default' | 'lg'
  showValue?: boolean
  animated?: boolean
  indeterminate?: boolean
}

const Progress = forwardRef<HTMLDivElement, ProgressProps>(
  ({
    className,
    value = 0,
    max = 100,
    variant = 'default',
    size = 'default',
    showValue = false,
    animated = false,
    indeterminate = false,
    ...props
  }, ref) => {
    const percentage = Math.min(Math.max((value / max) * 100, 0), 100)

    const variantClasses = {
      default: 'bg-primary-500',
      success: 'bg-green-500',
      warning: 'bg-yellow-500',
      error: 'bg-red-500',
    }

    const sizeClasses = {
      sm: 'h-1',
      default: 'h-2',
      lg: 'h-3',
    }

    return (
      <div className={cn('space-y-1', className)} ref={ref} {...props}>
        {showValue && (
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Progress</span>
            <span className="text-gray-900 font-medium">
              {indeterminate ? 'Processing...' : `${Math.round(percentage)}%`}
            </span>
          </div>
        )}
        <div
          className={cn(
            'w-full bg-gray-200 rounded-full overflow-hidden',
            sizeClasses[size]
          )}
        >
          {indeterminate ? (
            <div
              className={cn(
                'h-full rounded-full animate-pulse',
                variantClasses[variant],
                'w-1/3 animate-[loading_1.5s_ease-in-out_infinite]'
              )}
              style={{
                animationName: 'indeterminate',
                animationDuration: '1.5s',
                animationTimingFunction: 'linear',
                animationIterationCount: 'infinite',
              }}
            />
          ) : (
            <div
              className={cn(
                'h-full rounded-full transition-all duration-500 ease-out',
                variantClasses[variant],
                animated && 'animate-pulse'
              )}
              style={{
                width: `${percentage}%`,
              }}
            />
          )}
        </div>
      </div>
    )
  }
)

Progress.displayName = 'Progress'

// Circular Progress Component
export interface CircularProgressProps {
  value?: number
  max?: number
  size?: number
  strokeWidth?: number
  variant?: 'default' | 'success' | 'warning' | 'error'
  showValue?: boolean
  className?: string
  indeterminate?: boolean
}

export const CircularProgress = ({
  value = 0,
  max = 100,
  size = 40,
  strokeWidth = 4,
  variant = 'default',
  showValue = false,
  className,
  indeterminate = false,
}: CircularProgressProps) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100)
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const offset = circumference - (percentage / 100) * circumference

  const variantColors = {
    default: 'stroke-primary-500',
    success: 'stroke-green-500',
    warning: 'stroke-yellow-500',
    error: 'stroke-red-500',
  }

  return (
    <div className={cn('relative inline-flex items-center justify-center', className)}>
      <svg
        width={size}
        height={size}
        className={cn(
          'transform -rotate-90',
          indeterminate && 'animate-spin'
        )}
      >
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="none"
          className="text-gray-200"
        />
        
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={indeterminate ? circumference * 0.75 : offset}
          strokeLinecap="round"
          className={cn(
            'transition-all duration-500 ease-out',
            variantColors[variant]
          )}
        />
      </svg>
      
      {showValue && !indeterminate && (
        <span className="absolute text-xs font-medium text-gray-900">
          {Math.round(percentage)}%
        </span>
      )}
    </div>
  )
}

export { Progress }

// Add keyframes for indeterminate animation
const style = document.createElement('style')
style.textContent = `
  @keyframes indeterminate {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(400%); }
  }
`
if (typeof document !== 'undefined') {
  document.head.appendChild(style)
}