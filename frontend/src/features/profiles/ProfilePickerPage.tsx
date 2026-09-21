import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ClayButton } from '../../components/ui/ClayButton'
import { ClayCard } from '../../components/ui/ClayCard'
import { ClayInput } from '../../components/ui/ClayInput'
import { useProfileStore } from '../../store/profileStore'
import { createProfile, listProfiles, unlockProfile } from './api'
import type { Profile } from './types'

const accents = ['mint', 'peach', 'sky', 'butter'] as const

export function ProfilePickerPage() {
  const navigate = useNavigate()
  const setActiveProfile = useProfileStore((s) => s.setActiveProfile)
  const fallbackMode = useProfileStore((s) => s.fallbackMode)
  const fallbackPalette = useProfileStore((s) => s.fallbackPalette)
  const [profiles, setProfiles] = useState<Profile[]>([])
  const [name, setName] = useState('')
  const [password, setPassword] = useState('')
  const [accent, setAccent] = useState<(typeof accents)[number]>(fallbackPalette)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [unlockFor, setUnlockFor] = useState<Profile | null>(null)
  const [unlockPassword, setUnlockPassword] = useState('')
  const [unlockError, setUnlockError] = useState<string | null>(null)

  useEffect(() => {
    listProfiles()
      .then(setProfiles)
      .catch(() => setError('Could not reach the API. Is the backend running on :8000?'))
      .finally(() => setLoading(false))
  }, [])

  async function onCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim()) return
    const profile = await createProfile({
      display_name: name.trim(),
      accent_hue: accent,
      theme: fallbackMode,
      password: password || undefined,
    })
    setActiveProfile(profile)
    navigate('/home')
  }

  async function pick(profile: Profile) {
    if (profile.has_password) {
      setUnlockFor(profile)
      setUnlockPassword('')
      setUnlockError(null)
      return
    }
    setActiveProfile(profile)
    navigate('/home')
  }

  async function onUnlock(e: React.FormEvent) {
    e.preventDefault()
    if (!unlockFor) return
    try {
      const profile = await unlockProfile(unlockFor.id, unlockPassword)
      setActiveProfile(profile)
      navigate('/home')
    } catch {
      setUnlockError('Incorrect password')
    }
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-3xl flex-col justify-center gap-8 px-6 py-12 pr-28">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ type: 'spring', stiffness: 180, damping: 18 }}
      >
        <p className="text-sm font-bold uppercase tracking-[0.2em] text-muted">Welcome to</p>
        <h1 className="font-display mt-2 text-6xl font-semibold tracking-tight text-ink md:text-7xl">
          QuickSplit
        </h1>
        <p className="mt-3 max-w-md text-lg text-muted">
          Bubbly flashcards that remember how you learn — pick a profile to start.
        </p>
      </motion.div>

      {error && <p className="rounded-clay bg-again/30 px-4 py-3 text-sm">{error}</p>}

      <div className="grid gap-4 sm:grid-cols-2">
        {loading ? (
          <ClayCard className="p-6">Loading profiles…</ClayCard>
        ) : (
          profiles.map((p) => (
            <ClayCard key={p.id} accent={p.accent_hue} className="border border-panel p-5">
              <button type="button" className="w-full text-left" onClick={() => void pick(p)}>
                <div className="text-2xl font-bold text-ink">{p.display_name}</div>
                <div className="mt-1 text-sm text-muted capitalize">
                  {p.accent_hue} · {p.has_password ? 'locked' : 'open'} · {p.theme} mode
                </div>
              </button>
            </ClayCard>
          ))
        )}
      </div>

      {unlockFor && (
        <ClayCard className="border border-panel p-6">
          <h2 className="text-xl font-bold text-ink">Unlock {unlockFor.display_name}</h2>
          <form className="mt-4 flex flex-col gap-3" onSubmit={onUnlock}>
            <ClayInput
              type="password"
              placeholder="Password"
              value={unlockPassword}
              onChange={(e) => setUnlockPassword(e.target.value)}
              autoFocus
            />
            {unlockError && <p className="text-sm text-again">{unlockError}</p>}
            <div className="flex gap-2">
              <ClayButton type="submit">Unlock</ClayButton>
              <ClayButton type="button" tone="butter" onClick={() => setUnlockFor(null)}>
                Cancel
              </ClayButton>
            </div>
          </form>
        </ClayCard>
      )}

      <ClayCard className="border border-panel p-6">
        <h2 className="text-xl font-bold text-ink">New profile</h2>
        <form className="mt-4 flex flex-col gap-3" onSubmit={onCreate}>
          <ClayInput
            placeholder="Name (e.g. Alex)"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <ClayInput
            type="password"
            placeholder="Password (optional — no rules)"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <div className="flex flex-wrap gap-2">
            {accents.map((a) => (
              <button
                key={a}
                type="button"
                onClick={() => setAccent(a)}
                className={`rounded-full px-3 py-1 text-sm capitalize ${
                  accent === a ? 'bg-ink text-clay' : 'bg-panel text-ink border border-panel'
                }`}
              >
                {a}
              </button>
            ))}
          </div>
          <ClayButton type="submit" tone={accent}>
            Create & continue
          </ClayButton>
        </form>
      </ClayCard>
    </div>
  )
}
