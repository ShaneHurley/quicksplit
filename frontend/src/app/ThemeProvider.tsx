import { useEffect } from 'react'
import type { Profile } from '../features/profiles/types'
import { useProfileStore } from '../store/profileStore'

/** Apply theme to <html data-theme> and keep profile + local preference in sync. */
export function applyTheme(theme: 'dark' | 'light') {
  document.documentElement.setAttribute('data-theme', theme)
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const profile = useProfileStore((s) => s.activeProfile)
  const fallback = useProfileStore((s) => s.fallbackTheme)

  useEffect(() => {
    const theme = (profile?.theme as 'dark' | 'light' | undefined) ?? fallback
    applyTheme(theme === 'light' ? 'light' : 'dark')
  }, [profile?.theme, fallback])

  return children
}

export function themeFromProfile(profile: Profile | null): 'dark' | 'light' {
  return profile?.theme === 'light' ? 'light' : 'dark'
}
