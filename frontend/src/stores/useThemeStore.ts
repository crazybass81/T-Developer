import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type ThemeMode = 'light' | 'dark' | 'system'

interface ThemeState {
  mode: ThemeMode
  isDark: boolean
  setMode: (mode: ThemeMode) => void
  toggleTheme: () => void
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      mode: 'system',
      isDark: false,

      setMode: (mode) => {
        set({ mode })
        
        // Apply theme immediately
        const isDark = mode === 'dark' || 
          (mode === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)
        
        document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light')
        set({ isDark })
      },

      toggleTheme: () => {
        const { mode } = get()
        const newMode = mode === 'light' ? 'dark' : 'light'
        get().setMode(newMode)
      },
    }),
    {
      name: 't-developer-theme',
      version: 1,
    }
  )
)

// Initialize theme on app load
if (typeof window !== 'undefined') {
  const { mode, setMode } = useThemeStore.getState()
  
  // Listen to system theme changes
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  const handleChange = () => {
    if (useThemeStore.getState().mode === 'system') {
      setMode('system')
    }
  }
  
  mediaQuery.addEventListener('change', handleChange)
  
  // Set initial theme
  setMode(mode)
}