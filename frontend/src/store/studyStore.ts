import { create } from 'zustand'
import type { Card, SessionStats } from '../features/study/types'

type StudyState = {
  sessionId: string | null
  queue: Card[]
  current: Card | null
  stats: SessionStats | null
  reviewed: number
  setSession: (sessionId: string, queue: Card[], stats: SessionStats) => void
  setCurrent: (card: Card | null) => void
  applyQueue: (queue: Card[]) => void
  setStats: (stats: SessionStats) => void
  clear: () => void
}

export const useStudyStore = create<StudyState>((set) => ({
  sessionId: null,
  queue: [],
  current: null,
  stats: null,
  reviewed: 0,
  setSession: (sessionId, queue, stats) =>
    set({
      sessionId,
      queue,
      current: queue[0] ?? null,
      stats,
      reviewed: 0,
    }),
  setCurrent: (card) => set({ current: card }),
  applyQueue: (queue) => set({ queue, current: queue[0] ?? null }),
  setStats: (stats) => set({ stats, reviewed: stats.cards_reviewed }),
  clear: () =>
    set({ sessionId: null, queue: [], current: null, stats: null, reviewed: 0 }),
}))
