export type SessionStats = {
  id: string
  cards_reviewed: number
  again_count: number
  hard_count: number
  good_count: number
  easy_count: number
  mean_duration_ms: number
  interrupted: boolean
  ended_at?: string | null
}

export type { Card } from '../decks/types'

export type ReviewResponse = {
  performance: {
    id: string
    state: string
    due_at: string
    fail_streak: number
  }
  next_card: import('../decks/types').Card | null
  session_stats: SessionStats
  celebrated: boolean
}
