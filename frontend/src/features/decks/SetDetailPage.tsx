import { useEffect, useState } from 'react'
import { Link, Navigate, useNavigate, useParams } from 'react-router-dom'
import { ClayButton } from '../../components/ui/ClayButton'
import { ClayCard } from '../../components/ui/ClayCard'
import { ClayInput } from '../../components/ui/ClayInput'
import { useProfileStore } from '../../store/profileStore'
import { addCard, deleteCard, deleteSet, getSet } from './api'
import { ImportModal } from './ImportModal'
import type { FlashcardSet } from './types'

export function SetDetailPage() {
  const { setId } = useParams()
  const profile = useProfileStore((s) => s.activeProfile)
  const navigate = useNavigate()
  const [set, setSet] = useState<FlashcardSet | null>(null)
  const [front, setFront] = useState('')
  const [back, setBack] = useState('')
  const [imageUrl, setImageUrl] = useState('')
  const [notes, setNotes] = useState('')
  const [showImport, setShowImport] = useState(false)

  async function reload() {
    if (!setId) return
    const data = await getSet(setId, profile?.id)
    setSet(data)
  }

  useEffect(() => {
    reload().catch(console.error)
  }, [setId, profile?.id])

  if (!profile) return <Navigate to="/" replace />
  if (!set) {
    return <div className="p-10 text-muted">Loading set…</div>
  }

  async function onAdd(e: React.FormEvent) {
    e.preventDefault()
    if (!front.trim() || !back.trim() || !setId) return
    await addCard(setId, {
      front: front.trim(),
      back: back.trim(),
      image_url: imageUrl.trim() || undefined,
      notes: notes.trim() || undefined,
    })
    setFront('')
    setBack('')
    setImageUrl('')
    setNotes('')
    await reload()
  }

  return (
    <div className="mx-auto max-w-3xl px-6 py-10 pr-28">
      <Link to="/home" className="text-sm font-bold text-mint-deep">
        ← All sets
      </Link>
      <div className="mt-4 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="font-display text-4xl font-semibold text-ink">{set.title}</h1>
          <p className="mt-2 text-muted">{set.description || 'No description yet.'}</p>
          <p className="mt-2 text-sm font-semibold text-ink">
            {set.card_count} cards · {set.due_count} due for {profile.display_name}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <ClayButton tone="sky" type="button" onClick={() => setShowImport(true)}>
            Import
          </ClayButton>
          <ClayButton
            tone="mint"
            type="button"
            disabled={set.card_count === 0}
            onClick={() => navigate(`/sets/${set.id}/study`)}
          >
            Study
          </ClayButton>
          <ClayButton
            tone="peach"
            type="button"
            onClick={async () => {
              if (!confirm('Delete this set?')) return
              await deleteSet(set.id)
              navigate('/home')
            }}
          >
            Delete
          </ClayButton>
        </div>
      </div>

      <ul className="mt-8 space-y-3">
        {(set.cards ?? []).map((card) => (
          <ClayCard key={card.id} accent={set.accent} className="border border-panel p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="font-bold text-ink">{card.front}</div>
                <div className="mt-1 text-sm text-muted">{card.back}</div>
                {card.image_url ? (
                  <img
                    src={card.image_url}
                    alt=""
                    className="mt-2 max-h-28 rounded-xl object-cover"
                  />
                ) : null}
                {card.notes ? (
                  <p className="mt-2 text-xs text-muted">Notes: {card.notes}</p>
                ) : null}
              </div>
              <button
                type="button"
                className="text-sm font-semibold text-again"
                onClick={async () => {
                  await deleteCard(card.id)
                  await reload()
                }}
              >
                Remove
              </button>
            </div>
          </ClayCard>
        ))}
      </ul>

      <ClayCard className="mt-8 border border-panel p-6">
        <h2 className="text-lg font-bold text-ink">Add a card</h2>
        <form className="mt-3 grid gap-3" onSubmit={onAdd}>
          <ClayInput
            placeholder="Title / prompt *"
            value={front}
            onChange={(e) => setFront(e.target.value)}
          />
          <ClayInput
            placeholder="Definition / answer *"
            value={back}
            onChange={(e) => setBack(e.target.value)}
          />
          <ClayInput
            placeholder="Image URL (optional)"
            value={imageUrl}
            onChange={(e) => setImageUrl(e.target.value)}
          />
          <ClayInput
            placeholder="Additional notes (optional)"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
          <ClayButton type="submit" tone="sky">
            Add card
          </ClayButton>
        </form>
      </ClayCard>

      {showImport && (
        <ImportModal
          setId={set.id}
          onClose={() => setShowImport(false)}
          onImported={() => void reload()}
        />
      )}
    </div>
  )
}
