import { api } from '../../lib/apiClient'
import type { Profile } from './types'

export async function listProfiles(): Promise<Profile[]> {
  const { data } = await api.get<Profile[]>('/profiles')
  return data
}

export async function createProfile(input: {
  display_name: string
  accent_hue?: string
  theme?: 'dark' | 'light'
  password?: string
}): Promise<Profile> {
  const { data } = await api.post<Profile>('/profiles', input)
  return data
}

export async function unlockProfile(id: string, password: string): Promise<Profile> {
  const { data } = await api.post<Profile>(`/profiles/${id}/unlock`, { password })
  return data
}

export async function updateProfile(
  id: string,
  input: Partial<{ display_name: string; accent_hue: string; theme: 'dark' | 'light'; password: string }>,
): Promise<Profile> {
  const { data } = await api.patch<Profile>(`/profiles/${id}`, input)
  return data
}
