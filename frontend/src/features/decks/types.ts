export type Card = {
  id: string
  set_id: string
  card_type: string
  front: string
  back: string
  hint: string | null
  image_url?: string | null
  notes?: string | null
  position: number
  answer_mode?: string | null
  choices_json?: string | null
  correct_index?: number | null
}

export type FlashcardSet = {
  id: string
  title: string
  description: string
  accent: string
  owner_profile_id: string | null
  card_count: number
  created_at: string
  updated_at: string
  due_count: number
  cards?: Card[]
}

export type ImportPreviewCard = {
  front: string
  back: string
  image_url?: string | null
  notes?: string | null
}

export type ImportPayload = {
  raw_text: string
  field_sep: 'tab' | 'comma' | 'pipe' | 'custom'
  field_sep_custom?: string
  card_sep: 'newline' | 'semicolon' | 'blankline' | 'custom'
  card_sep_custom?: string
  skip_header?: boolean
  column_map?: Array<'front' | 'back' | 'image_url' | 'notes' | 'ignore'>
  new_set_title?: string
  new_set_description?: string
  owner_profile_id?: string
  accent?: string
}
