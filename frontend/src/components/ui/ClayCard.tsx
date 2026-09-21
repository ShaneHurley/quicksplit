import type { HTMLAttributes, ReactNode } from 'react'

type Props = HTMLAttributes<HTMLDivElement> & {
  children: ReactNode
  accent?: string
}

const accentBg: Record<string, string> = {
  mint: 'bg-mint/30',
  peach: 'bg-peach/35',
  sky: 'bg-sky/35',
  butter: 'bg-butter/45',
}

export function ClayCard({ children, accent = 'mint', className = '', ...rest }: Props) {
  return (
    <div
      className={`shadow-clay rounded-clay bg-clay border border-white/60 ${accentBg[accent] ?? accentBg.mint} ${className}`}
      {...rest}
    >
      {children}
    </div>
  )
}
