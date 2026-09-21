import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { Profile } from '../features/profiles/types'

export type ThemeMode = 'dark' | 'light'
export type Palette = 'mint' | 'peach' | 'sky' | 'butter'

type ProfileState = {
  activeProfile: Profile | null
  fallbackMode: ThemeMode
  fallbackPalette: Palette
  setActiveProfile: (profile: Profile | null) => void
  setFallbackMode: (mode: ThemeMode) => void
  setFallbackPalette: (palette: Palette) => void
}

export const useProfileStore = create<ProfileState>()(
  persist(
    (set) => ({
      activeProfile: null,
      fallbackMode: 'light',
      fallbackPalette: 'mint',
      setActiveProfile: (profile) => set({ activeProfile: profile }),
      setFallbackMode: (mode) => set({ fallbackMode: mode }),
      setFallbackPalette: (palette) => set({ fallbackPalette: palette }),
    }),
    {
      name: 'quicksplit-profile',
      // Migrate old persisted shape that used fallbackTheme
      merge: (persisted, current) => {
        const p = (persisted ?? {}) as Partial<ProfileState> & { fallbackTheme?: ThemeMode }
        return {
          ...current,
          ...p,
          fallbackMode: p.fallbackMode ?? p.fallbackTheme ?? current.fallbackMode,
          fallbackPalette: p.fallbackPalette ?? current.fallbackPalette,
        }
      },
    },
  ),
)
