import { motion } from 'framer-motion'
import { updateProfile } from '../../features/profiles/api'
import { useProfileStore, type Palette, type ThemeMode } from '../../store/profileStore'
import { applyAppearance, normalizeMode, normalizePalette } from '../../app/ThemeProvider'

const PALETTES: { id: Palette; label: string; swatch: string }[] = [
  { id: 'mint', label: 'Mint', swatch: '#7dcbbe' },
  { id: 'peach', label: 'Peach', swatch: '#f0b7a0' },
  { id: 'sky', label: 'Sky', swatch: '#8ec5e8' },
  { id: 'butter', label: 'Butter', swatch: '#f6e7a9' },
]

/** Top-right appearance control: color palette + light/dark. */
export function ThemeToggle() {
  const profile = useProfileStore((s) => s.activeProfile)
  const setActiveProfile = useProfileStore((s) => s.setActiveProfile)
  const fallbackMode = useProfileStore((s) => s.fallbackMode)
  const fallbackPalette = useProfileStore((s) => s.fallbackPalette)
  const setFallbackMode = useProfileStore((s) => s.setFallbackMode)
  const setFallbackPalette = useProfileStore((s) => s.setFallbackPalette)

  const mode = normalizeMode(profile?.theme ?? fallbackMode)
  const palette = normalizePalette(profile?.accent_hue ?? fallbackPalette)

  async function persist(nextMode: ThemeMode, nextPalette: Palette) {
    applyAppearance(nextMode, nextPalette)
    if (profile) {
      const updated = await updateProfile(profile.id, {
        theme: nextMode,
        accent_hue: nextPalette,
      })
      setActiveProfile(updated)
    } else {
      setFallbackMode(nextMode)
      setFallbackPalette(nextPalette)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -6 }}
      animate={{ opacity: 1, y: 0 }}
      className="shadow-clay fixed right-4 top-4 z-50 flex items-center gap-2 rounded-clay border border-panel bg-panel px-3 py-2"
    >
      <div className="flex items-center gap-1.5" role="group" aria-label="Color theme">
        {PALETTES.map((p) => (
          <button
            key={p.id}
            type="button"
            title={p.label}
            aria-label={`${p.label} theme`}
            aria-pressed={palette === p.id}
            onClick={() => void persist(mode, p.id)}
            className={`h-7 w-7 rounded-full border-2 transition ${
              palette === p.id ? 'scale-110 border-ink' : 'border-transparent opacity-80 hover:opacity-100'
            }`}
            style={{ background: p.swatch }}
          />
        ))}
      </div>
      <div className="mx-1 h-6 w-px bg-[var(--color-panel-border)]" />
      <button
        type="button"
        className="rounded-full px-3 py-1 text-xs font-bold text-ink hover:bg-black/5"
        onClick={() => void persist(mode === 'dark' ? 'light' : 'dark', palette)}
        aria-label={`Switch to ${mode === 'dark' ? 'light' : 'dark'} mode`}
      >
        {mode === 'dark' ? 'Light' : 'Dark'}
      </button>
    </motion.div>
  )
}
