import { useEffect, useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ClayButton } from '../../components/ui/ClayButton'
import { ClayCard } from '../../components/ui/ClayCard'
import { ClayInput } from '../../components/ui/ClayInput'
import { useProfileStore } from '../../store/profileStore'
import { createSet, listSets } from './api'
import type { FlashcardSet } from './types'

export function HomePage() {
  const profile = useProfileStore((s) => s.activeProfile)
  const setActiveProfile = useProfileStore((s) => s.setActiveProfile)
  const navigate = useNavigate()
  const [sets, setSets] = useState<FlashcardSet[]>([])
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    if (!profile) return
    listSets(profile.id).then(setSets).catch(console.error)
  }, [profile])

  if (!profile) return <Navigate to="/" replace />

  async function onCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!title.trim() || !profile) return
    setBusy(true)
    try {
      const created = await createSet({
        title: title.trim(),
        description: description.trim(),
        owner_profile_id: profile.id,
        accent: profile.accent_hue,
      })
      setTitle('')
      setDescription('')
      navigate(`/sets/${created.id}`)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-6 py-10 pr-28">
      <header className="mb-10 flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm font-bold uppercase tracking-[0.18em] text-muted">
            Studying as {profile.display_name}
          </p>
          <h1 className="font-display mt-1 text-5xl font-semibold text-ink">QuickSplit</h1>
          <p className="mt-2 text-muted">Browse your sets or start a new one.</p>
        </div>
        <ClayButton
          tone="butter"
          type="button"
          onClick={() => {
            setActiveProfile(null)
            navigate('/')
          }}
        >
          Switch profile
        </ClayButton>
      </header>

      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {sets.map((s, i) => (
          <motion.div
            key={s.id}
            layout
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.04 }}
          >
            <Link to={`/sets/${s.id}`}>
              <ClayCard accent={s.accent} className="h-full p-5 transition hover:-translate-y-0.5">
                <h2 className="text-xl font-bold">{s.title}</h2>
                <p className="mt-2 line-clamp-2 text-sm text-muted">{s.description || 'No description'}</p>
                <div className="mt-4 flex gap-3 text-sm font-semibold">
                  <span>{s.card_count} cards</span>
                  <span className="text-mint-deep">{s.due_count} due</span>
                </div>
              </ClayCard>
            </Link>
          </motion.div>
        ))}
      </div>

      <ClayCard className="mt-10 p-6">
        <h2 className="text-xl font-bold">Add a new set</h2>
        <form className="mt-4 grid gap-3 md:grid-cols-[1fr_1fr_auto]" onSubmit={onCreate}>
          <ClayInput
            placeholder="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <ClayInput
            placeholder="Short description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
          <ClayButton type="submit" disabled={busy}>
            Create
          </ClayButton>
        </form>
      </ClayCard>
    </div>
  )
}
