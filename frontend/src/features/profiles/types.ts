export type Profile = {
  id: string
  display_name: string
  avatar_emoji: string | null
  accent_hue: string
  theme: 'dark' | 'light' | string
  has_password: boolean
  created_at: string
  updated_at: string
}
