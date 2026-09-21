import { useEffect, useRef, useState } from 'react'
import { Link, Navigate, useNavigate, useParams } from 'react-router-dom'
import confetti from 'canvas-confetti'
import { ClayButton } from '../../components/ui/ClayButton'
import { ClayCard } from '../../components/ui/ClayCard'
import { useProfileStore } from '../../store/profileStore'
import { useStudyStore } from '../../store/studyStore'
import { endSession, startSession, submitReview } from './api'
import { FlippingCard } from './FlippingCard'
import { GradeBar } from './GradeBar'

export function StudyPage() {
  const { setId } = useParams()
  const profile = useProfileStore((s) => s.activeProfile)
  const navigate = useNavigate()
  const {
    sessionId,
    current,
    stats,
    setSession,
    setCurrent,
    setStats,
    clear,
  } = useStudyStore()

  const [flipped, setFlipped] = useState(false)
  const [done, setDone] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const shownAt = useRef<number>(Date.now())
  const flippedAt = useRef<number | null>(null)

  useEffect(() => {
    if (!profile || !setId) return
    let cancelled = false
    ;(async () => {
      try {
        const data = await startSession(profile.id, setId)
        if (cancelled) return
        setSession(data.session.id, data.queue, data.session)
        setDone(data.queue.length === 0)
        shownAt.current = Date.now()
        flippedAt.current = null
        setFlipped(false)
      } catch (e) {
        setError('Could not start study session.')
        console.error(e)
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [profile, setId, setSession])

  if (!profile) return <Navigate to="/" replace />

  async function finish(celebrated: boolean) {
    if (sessionId) {
      await endSession(sessionId)
    }
    if (celebrated) {
      confetti({ particleCount: 120, spread: 0.65, origin: { y: 0.7 } })
    }
    setDone(true)
  }

  async function onGrade(grade: 1 | 2 | 3 | 4) {
    if (!sessionId || !current || !profile) return
    const duration = Date.now() - shownAt.current
    const flipMs = flippedAt.current ? flippedAt.current - shownAt.current : null
    const result = await submitReview({
      session_id: sessionId,
      profile_id: profile.id,
      card_id: current.id,
      grade,
      duration_ms: duration,
      time_to_flip_ms: flipMs,
    })
    setStats(result.session_stats)
    setFlipped(false)
    flippedAt.current = null
    shownAt.current = Date.now()
    if (result.celebrated || !result.next_card) {
      setCurrent(null)
      await finish(true)
      return
    }
    setCurrent(result.next_card)
  }

  if (loading) {
    return <div className="p-10 text-muted">Building your study queue…</div>
  }

  if (error) {
    return (
      <div className="mx-auto max-w-lg p-10">
        <ClayCard className="p-6">
          <p>{error}</p>
          <Link to={`/sets/${setId}`} className="mt-4 inline-block font-bold text-mint-deep">
            Back to set
          </Link>
        </ClayCard>
      </div>
    )
  }

  if (done || !current) {
    return (
      <div className="mx-auto flex min-h-screen max-w-lg flex-col justify-center px-6">
        <ClayCard className="p-8 text-center">
          <h1 className="font-display text-4xl font-semibold">Nice work</h1>
          <p className="mt-3 text-muted">
            Reviewed {stats?.cards_reviewed ?? 0} cards this session.
            {stats ? ` Again ${stats.again_count} · Good ${stats.good_count}` : ''}
          </p>
          <div className="mt-6 flex justify-center gap-3">
            <ClayButton
              type="button"
              onClick={() => {
                clear()
                navigate(`/sets/${setId}`)
              }}
            >
              Back to set
            </ClayButton>
            <ClayButton
              tone="sky"
              type="button"
              onClick={() => {
                clear()
                navigate('/home')
              }}
            >
              Home
            </ClayButton>
          </div>
        </ClayCard>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <div className="mb-6 flex items-center justify-between">
        <Link to={`/sets/${setId}`} className="text-sm font-bold text-mint-deep">
          Exit
        </Link>
        <p className="text-sm font-semibold text-muted">
          Reviewed {stats?.cards_reviewed ?? 0}
        </p>
      </div>

      <FlippingCard
        front={current.front}
        back={current.back}
        hint={current.hint}
        imageUrl={current.image_url}
        notes={current.notes}
        flipped={flipped}
        onFlip={() => {
          if (!flipped) flippedAt.current = Date.now()
          setFlipped((v) => !v)
        }}
      />

      <GradeBar disabled={!flipped} onGrade={onGrade} />
      {!flipped && (
        <p className="mt-4 text-center text-sm text-muted">Flip the card before grading.</p>
      )}
    </div>
  )
}
