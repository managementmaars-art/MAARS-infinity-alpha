import { useContext } from 'react'
import { ThemeContext } from './ThemeContext'

/**
 * Hook to access and control the current theme
 */
export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}
