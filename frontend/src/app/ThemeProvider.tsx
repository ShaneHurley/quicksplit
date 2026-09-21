import { useEffect } from 'react'
import { useProfileStore, type Palette, type ThemeMode } from '../store/profileStore'

const PALETTES: Palette[] = ['mint', 'peach', 'sky', 'butter']

export function normalizePalette(value: string | null | undefined): Palette {
  return PALETTES.includes(value as Palette) ? (value as Palette) : 'mint'
}

export function normalizeMode(value: string | null | undefined): ThemeMode {
  return value === 'dark' ? 'dark' : 'light'
}

/** Apply palette + light/dark mode to <html>. */
export function applyAppearance(mode: ThemeMode, palette: Palette) {
  document.documentElement.setAttribute('data-mode', mode)
  document.documentElement.setAttribute('data-palette', palette)
  // Keep legacy data-theme for any leftover selectors
  document.documentElement.setAttribute('data-theme', mode)
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const profile = useProfileStore((s) => s.activeProfile)
  const fallbackMode = useProfileStore((s) => s.fallbackMode)
  const fallbackPalette = useProfileStore((s) => s.fallbackPalette)

  useEffect(() => {
    const mode = normalizeMode(profile?.theme ?? fallbackMode)
    const palette = normalizePalette(profile?.accent_hue ?? fallbackPalette)
    applyAppearance(mode, palette)
  }, [profile?.theme, profile?.accent_hue, fallbackMode, fallbackPalette])

  return children
}
