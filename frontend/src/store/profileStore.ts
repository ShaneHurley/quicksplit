import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { Profile } from '../features/profiles/types'

type ProfileState = {
  activeProfile: Profile | null
  fallbackTheme: 'dark' | 'light'
  setActiveProfile: (profile: Profile | null) => void
  setFallbackTheme: (theme: 'dark' | 'light') => void
}

export const useProfileStore = create<ProfileState>()(
  persist(
    (set) => ({
      activeProfile: null,
      fallbackTheme: 'dark',
      setActiveProfile: (profile) => set({ activeProfile: profile }),
      setFallbackTheme: (theme) => set({ fallbackTheme: theme }),
    }),
    { name: 'quicksplit-profile' },
  ),
)
