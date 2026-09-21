import { useMemo, useState } from 'react'
import { ClayButton } from '../../components/ui/ClayButton'
import { ClayInput } from '../../components/ui/ClayInput'
import { importCards, previewImport } from './api'
import type { ImportPreviewCard } from './types'

type Props = {
  setId: string
  onClose: () => void
  onImported: () => void
}

type FieldSep = 'tab' | 'comma' | 'custom'
type CardSep = 'newline' | 'semicolon' | 'custom'

const PLACEHOLDER = `Title 1\tDefinition 1\thttps://example.com/img.png\tOptional notes
Title 2\tDefinition 2
Title 3\tDefinition 3\t\tJust notes in the 4th column`

export function ImportModal({ setId, onClose, onImported }: Props) {
  const [raw, setRaw] = useState('')
  const [fieldSep, setFieldSep] = useState<FieldSep>('tab')
  const [fieldCustom, setFieldCustom] = useState('')
  const [cardSep, setCardSep] = useState<CardSep>('newline')
  const [cardCustom, setCardCustom] = useState('')
  const [preview, setPreview] = useState<ImportPreviewCard[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const payload = useMemo(
    () => ({
      raw_text: raw,
      field_sep: fieldSep,
      field_sep_custom: fieldSep === 'custom' ? fieldCustom : undefined,
      card_sep: cardSep,
      card_sep_custom: cardSep === 'custom' ? cardCustom : undefined,
    }),
    [raw, fieldSep, fieldCustom, cardSep, cardCustom],
  )

  async function refreshPreview() {
    setError(null)
    try {
      const result = await previewImport(setId, payload)
      setPreview(result.cards)
    } catch (e) {
      setError('Could not parse preview')
      console.error(e)
    }
  }

  async function onImport() {
    setBusy(true)
    setError(null)
    try {
      const result = await importCards(setId, payload)
      if (result.imported_count === 0) {
        setError('Nothing to import — check separators and paste format.')
        setPreview(result.cards)
        return
      }
      onImported()
      onClose()
    } catch (e) {
      setError('Import failed')
      console.error(e)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/55 p-4 backdrop-blur-sm">
      <div className="shadow-clay flex max-h-[92vh] w-full max-w-3xl flex-col overflow-hidden rounded-clay border border-panel bg-panel">
        <div className="flex items-start justify-between gap-4 border-b border-panel px-6 py-5">
          <div>
            <h2 className="font-display text-2xl font-semibold text-ink">Import your data</h2>
            <p className="mt-1 text-sm text-muted">
              Paste from Word, Excel, or Docs. Order per card: title · definition · image URL
              (optional) · notes (optional).
            </p>
          </div>
          <button
            type="button"
            className="text-2xl leading-none text-muted hover:text-ink"
            onClick={onClose}
            aria-label="Close"
          >
            ×
          </button>
        </div>

        <div className="overflow-y-auto px-6 py-5">
          <textarea
            value={raw}
            onChange={(e) => setRaw(e.target.value)}
            onBlur={() => void refreshPreview()}
            placeholder={PLACEHOLDER}
            className="shadow-clay min-h-40 w-full resize-y rounded-clay border border-panel bg-[var(--color-input)] p-4 font-mono text-sm text-ink outline-none focus:ring-2 focus:ring-mint/40"
          />

          <div className="mt-6 grid gap-6 sm:grid-cols-2">
            <fieldset>
              <legend className="mb-2 text-sm font-bold text-ink">Between title and definition</legend>
              {(
                [
                  ['tab', 'Tab'],
                  ['comma', 'Comma'],
                  ['custom', 'Custom'],
                ] as const
              ).map(([value, label]) => (
                <label key={value} className="mb-2 flex items-center gap-2 text-sm text-ink">
                  <input
                    type="radio"
                    name="fieldSep"
                    checked={fieldSep === value}
                    onChange={() => {
                      setFieldSep(value)
                      setTimeout(() => void refreshPreview(), 0)
                    }}
                  />
                  {label}
                  {value === 'custom' && (
                    <ClayInput
                      className="ml-1 !w-20 !py-1"
                      value={fieldCustom}
                      placeholder="|"
                      onChange={(e) => setFieldCustom(e.target.value)}
                      onBlur={() => void refreshPreview()}
                    />
                  )}
                </label>
              ))}
            </fieldset>

            <fieldset>
              <legend className="mb-2 text-sm font-bold text-ink">Between cards</legend>
              {(
                [
                  ['newline', 'New line'],
                  ['semicolon', 'Semicolon'],
                  ['custom', 'Custom'],
                ] as const
              ).map(([value, label]) => (
                <label key={value} className="mb-2 flex items-center gap-2 text-sm text-ink">
                  <input
                    type="radio"
                    name="cardSep"
                    checked={cardSep === value}
                    onChange={() => {
                      setCardSep(value)
                      setTimeout(() => void refreshPreview(), 0)
                    }}
                  />
                  {label}
                  {value === 'custom' && (
                    <ClayInput
                      className="ml-1 !w-20 !py-1"
                      value={cardCustom}
                      placeholder="||"
                      onChange={(e) => setCardCustom(e.target.value)}
                      onBlur={() => void refreshPreview()}
                    />
                  )}
                </label>
              ))}
            </fieldset>
          </div>

          <div className="mt-6">
            <h3 className="font-bold text-ink">
              Preview {preview.length} card{preview.length === 1 ? '' : 's'}
            </h3>
            {preview.length === 0 ? (
              <p className="mt-2 text-sm text-muted">Nothing to preview yet.</p>
            ) : (
              <ul className="mt-3 max-h-48 space-y-2 overflow-y-auto">
                {preview.slice(0, 40).map((c, i) => (
                  <li
                    key={`${c.front}-${i}`}
                    className="rounded-xl border border-panel bg-[var(--color-input)] px-3 py-2 text-sm"
                  >
                    <span className="font-bold text-ink">{c.front}</span>
                    <span className="text-muted"> — {c.back}</span>
                    {c.image_url ? (
                      <span className="mt-1 block truncate text-xs text-sky">🖼 {c.image_url}</span>
                    ) : null}
                    {c.notes ? (
                      <span className="mt-1 block text-xs text-muted">Notes: {c.notes}</span>
                    ) : null}
                  </li>
                ))}
              </ul>
            )}
          </div>
          {error && <p className="mt-3 text-sm text-again">{error}</p>}
        </div>

        <div className="flex justify-end gap-3 border-t border-panel px-6 py-4">
          <ClayButton type="button" tone="butter" onClick={onClose}>
            Cancel import
          </ClayButton>
          <ClayButton
            type="button"
            tone="mint"
            disabled={busy || preview.length === 0}
            onClick={() => void onImport()}
          >
            Import {preview.length ? `(${preview.length})` : ''}
          </ClayButton>
        </div>
      </div>
    </div>
  )
}
