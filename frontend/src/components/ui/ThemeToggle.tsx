'use client'

import { Sun, Moon, Monitor } from 'lucide-react'
import { useThemeStore, type ThemeMode } from '@/stores/useThemeStore'
import { Button } from './Button'
import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import { cn } from '@/lib/utils'

export function ThemeToggle() {
  const { mode, setMode } = useThemeStore()

  const themeOptions: { value: ThemeMode; label: string; icon: React.ReactNode }[] = [
    { value: 'light', label: '라이트 모드', icon: <Sun className="h-4 w-4" /> },
    { value: 'dark', label: '다크 모드', icon: <Moon className="h-4 w-4" /> },
    { value: 'system', label: '시스템 설정', icon: <Monitor className="h-4 w-4" /> },
  ]

  const currentTheme = themeOptions.find(option => option.value === mode)

  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="relative h-9 w-9"
          aria-label="테마 변경"
        >
          {currentTheme?.icon}
        </Button>
      </DropdownMenu.Trigger>
      
      <DropdownMenu.Portal>
        <DropdownMenu.Content
          className={cn(
            'z-50 min-w-[8rem] overflow-hidden rounded-md border border-gray-200 bg-white p-1 shadow-lg',
            'data-[state=open]:animate-in data-[state=closed]:animate-out',
            'data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0',
            'data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95',
            'data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2',
            'data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2'
          )}
          sideOffset={4}
          align="end"
        >
          {themeOptions.map((option) => (
            <DropdownMenu.Item
              key={option.value}
              className={cn(
                'relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none',
                'focus:bg-gray-100 focus:text-gray-900',
                'data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
                mode === option.value && 'bg-primary-50 text-primary-900'
              )}
              onClick={() => setMode(option.value)}
            >
              <span className="mr-2">{option.icon}</span>
              {option.label}
              {mode === option.value && (
                <span className="ml-auto h-2 w-2 bg-primary-500 rounded-full" />
              )}
            </DropdownMenu.Item>
          ))}
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  )
}

// Simple theme toggle button (for mobile or compact layouts)
export function SimpleThemeToggle() {
  const { mode, toggleTheme } = useThemeStore()
  
  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={toggleTheme}
      className="h-9 w-9"
      aria-label="테마 전환"
    >
      {mode === 'dark' ? (
        <Sun className="h-4 w-4" />
      ) : (
        <Moon className="h-4 w-4" />
      )}
    </Button>
  )
}