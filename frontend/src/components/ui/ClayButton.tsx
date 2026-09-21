import { motion } from 'framer-motion'
import type { ReactNode } from 'react'

type Props = {
  children: ReactNode
  tone?: 'mint' | 'peach' | 'sky' | 'butter' | 'ink'
  className?: string
  disabled?: boolean
  type?: 'button' | 'submit' | 'reset'
  onClick?: () => void
}

const tones: Record<NonNullable<Props['tone']>, string> = {
  mint: 'bg-mint text-ink',
  peach: 'bg-peach text-ink',
  sky: 'bg-sky text-ink',
  butter: 'bg-butter text-ink',
  ink: 'bg-ink text-clay',
}

export function ClayButton({
  children,
  tone = 'mint',
  className = '',
  disabled,
  type = 'button',
  onClick,
}: Props) {
  return (
    <motion.button
      type={type}
      whileHover={disabled ? undefined : { scale: 1.03 }}
      whileTap={disabled ? undefined : { scale: 0.96 }}
      transition={{ type: 'spring', stiffness: 420, damping: 22 }}
      disabled={disabled}
      onClick={onClick}
      className={`shadow-clay rounded-clay px-5 py-3 font-bold tracking-wide disabled:opacity-50 ${tones[tone]} ${className}`}
    >
      {children}
    </motion.button>
  )
}
