import { motion } from 'framer-motion'
import { updateProfile } from '../../features/profiles/api'
import { useProfileStore } from '../../store/profileStore'
import { applyTheme } from '../../app/ThemeProvider'

/** Top-right site-wide theme switch — persists on the active Profile. */
export function ThemeToggle() {
  const profile = useProfileStore((s) => s.activeProfile)
  const setActiveProfile = useProfileStore((s) => s.setActiveProfile)
  const fallbackTheme = useProfileStore((s) => s.fallbackTheme)
  const setFallbackTheme = useProfileStore((s) => s.setFallbackTheme)

  const theme = (profile?.theme as 'dark' | 'light' | undefined) ?? fallbackTheme
  const next = theme === 'dark' ? 'light' : 'dark'

  async function toggle() {
    applyTheme(next)
    if (profile) {
      const updated = await updateProfile(profile.id, { theme: next })
      setActiveProfile(updated)
    } else {
      setFallbackTheme(next)
    }
  }

  return (
    <motion.button
      type="button"
      whileTap={{ scale: 0.94 }}
      onClick={() => void toggle()}
      className="shadow-clay rounded-clay fixed right-4 top-4 z-50 border border-panel bg-panel px-4 py-2 text-sm font-bold text-ink"
      aria-label={`Switch to ${next} theme`}
      title={`Switch to ${next} theme`}
    >
      {theme === 'dark' ? 'Light mode' : 'Dark mode'}
    </motion.button>
  )
}
