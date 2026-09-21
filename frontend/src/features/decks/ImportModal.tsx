import { useEffect, useMemo, useState } from 'react'
import { ClayButton } from '../../components/ui/ClayButton'
import { ClayInput } from '../../components/ui/ClayInput'
import { importCards, importNewSet, previewImport, previewNewImport } from './api'
import type { ImportPayload, ImportPreviewCard } from './types'

type Props = {
  /** Existing set to append into. Omit to create a brand-new set. */
  setId?: string
  defaultTitle?: string
  ownerProfileId?: string
  accent?: string
  onClose: () => void
  onImported: (setId?: string) => void
}

type FieldSep = 'tab' | 'comma' | 'pipe' | 'custom'
type CardSep = 'newline' | 'semicolon' | 'blankline' | 'custom'
type ColumnRole = 'front' | 'back' | 'image_url' | 'notes' | 'ignore'

const ROLE_LABELS: Record<ColumnRole, string> = {
  front: 'Title',
  back: 'Definition',
  image_url: 'Image URL',
  notes: 'Notes',
  ignore: 'Ignore',
}

const PLACEHOLDER = `Title\tDefinition\tImage URL\tNotes
Osmosis\tWater diffusion across a membrane\thttps://example.com/osmosis.png\tAP Bio unit 2
ATP\tEnergy currency of the cell\t\tRemember mitochondria
Hypertonic\tHigher solute outside the cell`

export function ImportModal({
  setId,
  defaultTitle = '',
  ownerProfileId,
  accent = 'mint',
  onClose,
  onImported,
}: Props) {
  const creatingNew = !setId
  const [raw, setRaw] = useState('')
  const [setTitle, setSetTitle] = useState(defaultTitle)
  const [fieldSep, setFieldSep] = useState<FieldSep>('tab')
  const [fieldCustom, setFieldCustom] = useState('|')
  const [cardSep, setCardSep] = useState<CardSep>('newline')
  const [cardCustom, setCardCustom] = useState('||')
  const [skipHeader, setSkipHeader] = useState(true)
  const [columnMap, setColumnMap] = useState<ColumnRole[]>([
    'front',
    'back',
    'image_url',
    'notes',
  ])
  const [preview, setPreview] = useState<ImportPreviewCard[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const payload: ImportPayload = useMemo(
    () => ({
      raw_text: raw,
      field_sep: fieldSep,
      field_sep_custom: fieldSep === 'custom' ? fieldCustom : undefined,
      card_sep: cardSep,
      card_sep_custom: cardSep === 'custom' ? cardCustom : undefined,
      skip_header: skipHeader,
      column_map: columnMap,
      new_set_title: setTitle || undefined,
      owner_profile_id: ownerProfileId,
      accent,
    }),
    [
      raw,
      fieldSep,
      fieldCustom,
      cardSep,
      cardCustom,
      skipHeader,
      columnMap,
      setTitle,
      ownerProfileId,
      accent,
    ],
  )

  useEffect(() => {
    if (!raw.trim()) {
      setPreview([])
      return
    }
    const t = window.setTimeout(() => {
      void (async () => {
        try {
          const result = creatingNew
            ? await previewNewImport(payload)
            : await previewImport(setId!, payload)
          setPreview(result.cards)
          setError(null)
        } catch (e) {
          console.error(e)
          setError('Could not parse preview — check separators.')
        }
      })()
    }, 280)
    return () => window.clearTimeout(t)
  }, [payload, creatingNew, setId, raw])

  function setRole(index: number, role: ColumnRole) {
    setColumnMap((prev) => {
      const next = [...prev]
      next[index] = role
      return next
    })
  }

  function addColumn() {
    setColumnMap((prev) => [...prev, 'ignore'])
  }

  async function onImport() {
    setBusy(true)
    setError(null)
    try {
      if (creatingNew) {
        const result = await importNewSet(payload)
        onImported(result.set?.id)
        onClose()
        return
      }
      const result = await importCards(setId!, payload)
      if (result.imported_count === 0) {
        setError('Nothing to import — check separators, column map, and paste format.')
        setPreview(result.cards)
        return
      }
      onImported(setId)
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
      <div className="shadow-clay flex max-h-[94vh] w-full max-w-3xl flex-col overflow-hidden rounded-clay border border-panel bg-panel">
        <div className="flex items-start justify-between gap-4 border-b border-panel px-6 py-5">
          <div>
            <h2 className="font-display text-2xl font-semibold text-ink">Import your data</h2>
            <p className="mt-1 text-sm text-muted">
              Copy and paste from Word, Excel, Google Docs, etc. Map columns to title, definition,
              image, and notes.
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
          {creatingNew && (
            <div className="mb-4">
              <label className="mb-1 block text-sm font-bold text-ink">New set title</label>
              <ClayInput
                placeholder="e.g. AP Biology — Cell Transport"
                value={setTitle}
                onChange={(e) => setSetTitle(e.target.value)}
              />
            </div>
          )}

          <textarea
            value={raw}
            onChange={(e) => setRaw(e.target.value)}
            placeholder={PLACEHOLDER}
            className="shadow-clay min-h-44 w-full resize-y rounded-clay border border-panel bg-[var(--color-input)] p-4 font-mono text-sm text-ink outline-none focus:ring-2 focus:ring-mint/40"
          />

          <div className="mt-6 grid gap-6 sm:grid-cols-2">
            <fieldset>
              <legend className="mb-2 text-sm font-bold text-ink">Between term and definition</legend>
              {(
                [
                  ['tab', 'Tab'],
                  ['comma', 'Comma'],
                  ['pipe', 'Pipe ( | )'],
                  ['custom', 'Custom'],
                ] as const
              ).map(([value, label]) => (
                <label key={value} className="mb-2 flex items-center gap-2 text-sm text-ink">
                  <input
                    type="radio"
                    name="fieldSep"
                    checked={fieldSep === value}
                    onChange={() => setFieldSep(value)}
                  />
                  {label}
                  {value === 'custom' && (
                    <ClayInput
                      className="ml-1 !w-20 !py-1"
                      value={fieldCustom}
                      onChange={(e) => setFieldCustom(e.target.value)}
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
                  ['blankline', 'Blank line'],
                  ['semicolon', 'Semicolon'],
                  ['custom', 'Custom'],
                ] as const
              ).map(([value, label]) => (
                <label key={value} className="mb-2 flex items-center gap-2 text-sm text-ink">
                  <input
                    type="radio"
                    name="cardSep"
                    checked={cardSep === value}
                    onChange={() => setCardSep(value)}
                  />
                  {label}
                  {value === 'custom' && (
                    <ClayInput
                      className="ml-1 !w-20 !py-1"
                      value={cardCustom}
                      onChange={(e) => setCardCustom(e.target.value)}
                    />
                  )}
                </label>
              ))}
            </fieldset>
          </div>

          <label className="mt-4 flex items-center gap-2 text-sm font-semibold text-ink">
            <input
              type="checkbox"
              checked={skipHeader}
              onChange={(e) => setSkipHeader(e.target.checked)}
            />
            Skip first row (header)
          </label>

          <div className="mt-5">
            <div className="mb-2 flex items-center justify-between">
              <h3 className="text-sm font-bold text-ink">Column map</h3>
              <button
                type="button"
                className="text-xs font-bold text-mint-deep"
                onClick={addColumn}
              >
                + Column
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {columnMap.map((role, i) => (
                <label key={i} className="flex flex-col gap-1 text-xs text-muted">
                  Col {i + 1}
                  <select
                    value={role}
                    onChange={(e) => setRole(i, e.target.value as ColumnRole)}
                    className="rounded-xl border border-panel bg-[var(--color-input)] px-2 py-1.5 text-sm font-semibold text-ink"
                  >
                    {(Object.keys(ROLE_LABELS) as ColumnRole[]).map((r) => (
                      <option key={r} value={r}>
                        {ROLE_LABELS[r]}
                      </option>
                    ))}
                  </select>
                </label>
              ))}
            </div>
          </div>

          <div className="mt-6">
            <h3 className="font-bold text-ink">
              Preview {preview.length} card{preview.length === 1 ? '' : 's'}
              {preview.length === 0 ? '. Nothing to preview yet.' : ''}
            </h3>
            {preview.length > 0 && (
              <ul className="mt-3 grid max-h-56 gap-2 overflow-y-auto sm:grid-cols-2">
                {preview.slice(0, 48).map((c, i) => (
                  <li
                    key={`${c.front}-${i}`}
                    className="rounded-xl border border-panel bg-[var(--color-input)] px-3 py-2 text-sm"
                  >
                    <div className="font-bold text-ink">{c.front}</div>
                    <div className="text-muted">{c.back}</div>
                    {c.image_url ? (
                      <img
                        src={c.image_url}
                        alt=""
                        className="mt-2 max-h-16 rounded-lg object-cover"
                        onError={(e) => {
                          ;(e.target as HTMLImageElement).style.display = 'none'
                        }}
                      />
                    ) : null}
                    {c.notes ? (
                      <div className="mt-1 text-xs text-muted">Notes: {c.notes}</div>
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
            disabled={busy || preview.length === 0 || (creatingNew && !setTitle.trim())}
            onClick={() => void onImport()}
          >
            Import {preview.length ? `(${preview.length})` : ''}
          </ClayButton>
        </div>
      </div>
    </div>
  )
}
