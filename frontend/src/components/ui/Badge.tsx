'use client'

import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
  {
    variants: {
      variant: {
        default: 'border-transparent bg-primary-100 text-primary-800 hover:bg-primary-200',
        secondary: 'border-transparent bg-gray-100 text-gray-800 hover:bg-gray-200',
        destructive: 'border-transparent bg-red-100 text-red-800 hover:bg-red-200',
        success: 'border-transparent bg-green-100 text-green-800 hover:bg-green-200',
        warning: 'border-transparent bg-yellow-100 text-yellow-800 hover:bg-yellow-200',
        outline: 'text-gray-600 border-gray-200',
        
        // Status badges
        active: 'border-transparent bg-green-100 text-green-700',
        processing: 'border-transparent bg-blue-100 text-blue-700 animate-pulse',
        completed: 'border-transparent bg-green-100 text-green-700',
        error: 'border-transparent bg-red-100 text-red-700',
        paused: 'border-transparent bg-yellow-100 text-yellow-700',
        idle: 'border-transparent bg-gray-100 text-gray-700',
        
        // Agent status badges
        'agent-1': 'border-transparent bg-gradient-to-r from-indigo-100 to-purple-100 text-indigo-800',
        'agent-2': 'border-transparent bg-gradient-to-r from-pink-100 to-rose-100 text-pink-800',
        'agent-3': 'border-transparent bg-gradient-to-r from-blue-100 to-cyan-100 text-blue-800',
        'agent-4': 'border-transparent bg-gradient-to-r from-green-100 to-emerald-100 text-green-800',
        'agent-5': 'border-transparent bg-gradient-to-r from-pink-100 to-yellow-100 text-pink-800',
        'agent-6': 'border-transparent bg-gradient-to-r from-cyan-100 to-indigo-100 text-cyan-800',
        'agent-7': 'border-transparent bg-gradient-to-r from-teal-100 to-pink-100 text-teal-800',
        'agent-8': 'border-transparent bg-gradient-to-r from-rose-100 to-indigo-100 text-rose-800',
        'agent-9': 'border-transparent bg-gradient-to-r from-yellow-100 to-orange-100 text-yellow-800',
      },
      size: {
        sm: 'px-2 py-0.5 text-xs',
        default: 'px-2.5 py-0.5 text-xs',
        lg: 'px-3 py-1 text-sm',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {
  pulse?: boolean
}

function Badge({ className, variant, size, pulse, ...props }: BadgeProps) {
  return (
    <div
      className={cn(
        badgeVariants({ variant, size }),
        pulse && 'animate-pulse',
        className
      )}
      {...props}
    />
  )
}

export { Badge, badgeVariants }