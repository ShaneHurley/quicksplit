import { api } from '../../lib/apiClient'
import type { Card, FlashcardSet, ImportPayload, ImportPreviewCard } from './types'

export async function listSets(profileId?: string): Promise<FlashcardSet[]> {
  const { data } = await api.get<FlashcardSet[]>('/sets', {
    params: profileId ? { profile_id: profileId } : undefined,
  })
  return data
}

export async function getSet(setId: string, profileId?: string): Promise<FlashcardSet> {
  const { data } = await api.get<FlashcardSet>(`/sets/${setId}`, {
    params: profileId ? { profile_id: profileId } : undefined,
  })
  return data
}

export async function createSet(input: {
  title: string
  description?: string
  accent?: string
  owner_profile_id?: string
}): Promise<FlashcardSet> {
  const { data } = await api.post<FlashcardSet>('/sets', input)
  return data
}

export async function addCard(
  setId: string,
  input: {
    front: string
    back: string
    card_type?: 'text' | 'mc'
    image_url?: string
    notes?: string
  },
): Promise<Card> {
  const { data } = await api.post<Card>(`/sets/${setId}/cards`, {
    card_type: 'text',
    ...input,
  })
  return data
}

export async function deleteCard(cardId: string): Promise<void> {
  await api.delete(`/cards/${cardId}`)
}

export async function deleteSet(setId: string): Promise<void> {
  await api.delete(`/sets/${setId}`)
}

export async function previewImport(
  setId: string,
  payload: ImportPayload,
): Promise<{ imported_count: number; cards: ImportPreviewCard[] }> {
  const { data } = await api.post(`/sets/${setId}/import`, {
    ...payload,
    preview_only: true,
  })
  return data
}

export async function importCards(
  setId: string,
  payload: ImportPayload,
): Promise<{ imported_count: number; cards: ImportPreviewCard[] }> {
  const { data } = await api.post(`/sets/${setId}/import`, {
    ...payload,
    preview_only: false,
  })
  return data
}
