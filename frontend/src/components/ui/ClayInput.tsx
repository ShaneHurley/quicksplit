import type { InputHTMLAttributes } from 'react'

export function ClayInput({ className = '', ...rest }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={`shadow-clay rounded-clay w-full border border-panel bg-[var(--color-input)] px-4 py-3 text-ink outline-none ring-2 ring-transparent focus:ring-mint-deep/40 ${className}`}
      {...rest}
    />
  )
}
