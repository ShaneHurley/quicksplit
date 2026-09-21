import { api } from '../../lib/apiClient'
import type { Card } from '../decks/types'
import type { ReviewResponse, SessionStats } from './types'

export async function startSession(
  profileId: string,
  setId: string,
): Promise<{ session: SessionStats; queue: Card[]; queue_length: number }> {
  const { data } = await api.post('/study/sessions', {
    profile_id: profileId,
    set_id: setId,
  })
  return data
}

export async function submitReview(input: {
  session_id: string
  profile_id: string
  card_id: string
  grade: number
  duration_ms: number
  time_to_flip_ms?: number | null
}): Promise<ReviewResponse> {
  const { data } = await api.post<ReviewResponse>('/study/reviews', {
    ...input,
    client_timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    device_class: window.innerWidth < 768 ? 'mobile' : 'desktop',
  })
  return data
}

export async function endSession(sessionId: string): Promise<SessionStats> {
  const { data } = await api.post<SessionStats>(`/study/sessions/${sessionId}/end`)
  return data
}
