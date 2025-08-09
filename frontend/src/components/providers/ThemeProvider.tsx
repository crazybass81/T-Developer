'use client'

import { useEffect } from 'react'
import { useThemeStore } from '@/stores/useThemeStore'

interface ThemeProviderProps {
  children: React.ReactNode
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const { mode, isDark } = useThemeStore()

  useEffect(() => {
    // Apply theme on mount and when it changes
    const applyTheme = () => {
      const isDarkMode = mode === 'dark' || 
        (mode === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)
      
      document.documentElement.setAttribute('data-theme', isDarkMode ? 'dark' : 'light')
      
      // Update store state
      useThemeStore.setState({ isDark: isDarkMode })
    }

    applyTheme()

    // Listen to system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handleSystemThemeChange = () => {
      if (mode === 'system') {
        applyTheme()
      }
    }

    mediaQuery.addEventListener('change', handleSystemThemeChange)
    return () => mediaQuery.removeEventListener('change', handleSystemThemeChange)
  }, [mode])

  return <>{children}</>
}