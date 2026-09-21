import { motion } from 'framer-motion'

type Props = {
  front: string
  back: string
  hint?: string | null
  imageUrl?: string | null
  notes?: string | null
  flipped: boolean
  onFlip: () => void
}

export function FlippingCard({ front, back, hint, imageUrl, notes, flipped, onFlip }: Props) {
  return (
    <button
      type="button"
      onClick={onFlip}
      className="mx-auto block w-full max-w-xl [perspective:1200px]"
      aria-label={flipped ? 'Show front' : 'Show answer'}
    >
      <motion.div
        className="relative h-72 w-full"
        animate={{ rotateY: flipped ? 180 : 0 }}
        transition={{ type: 'spring', stiffness: 260, damping: 22 }}
        style={{ transformStyle: 'preserve-3d' }}
      >
        <div
          className="shadow-clay rounded-clay absolute inset-0 flex flex-col items-center justify-center bg-clay px-8 text-center border border-panel"
          style={{ backfaceVisibility: 'hidden' }}
        >
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-muted">Prompt</p>
          <p className="mt-3 text-2xl font-bold leading-snug text-ink md:text-3xl">{front}</p>
          {imageUrl ? (
            <img src={imageUrl} alt="" className="mt-3 max-h-24 rounded-xl object-cover" />
          ) : null}
          {hint ? <p className="mt-4 text-sm text-muted">Hint: {hint}</p> : null}
          <p className="mt-6 text-xs text-muted">Tap to flip</p>
        </div>
        <div
          className="shadow-clay rounded-clay absolute inset-0 flex flex-col items-center justify-center bg-mint/25 px-8 text-center border border-panel"
          style={{ backfaceVisibility: 'hidden', transform: 'rotateY(180deg)' }}
        >
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-muted">Answer</p>
          <p className="mt-3 text-2xl font-bold leading-snug text-ink md:text-3xl">{back}</p>
          {notes ? <p className="mt-4 text-sm text-muted">{notes}</p> : null}
        </div>
      </motion.div>
    </button>
  )
}
