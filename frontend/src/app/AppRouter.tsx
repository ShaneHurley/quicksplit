import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { ThemeProvider } from './ThemeProvider'
import { ThemeToggle } from '../components/ui/ThemeToggle'
import { ProfilePickerPage } from '../features/profiles/ProfilePickerPage'
import { HomePage } from '../features/decks/HomePage'
import { SetDetailPage } from '../features/decks/SetDetailPage'
import { StudyPage } from '../features/study/StudyPage'
import { useProfileStore } from '../store/profileStore'

function RequireProfile({ children }: { children: React.ReactNode }) {
  const profile = useProfileStore((s) => s.activeProfile)
  if (!profile) return <Navigate to="/" replace />
  return children
}

export function AppRouter() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <ThemeToggle />
        <Routes>
          <Route path="/" element={<ProfilePickerPage />} />
          <Route
            path="/home"
            element={
              <RequireProfile>
                <HomePage />
              </RequireProfile>
            }
          />
          <Route
            path="/sets/:setId"
            element={
              <RequireProfile>
                <SetDetailPage />
              </RequireProfile>
            }
          />
          <Route
            path="/sets/:setId/study"
            element={
              <RequireProfile>
                <StudyPage />
              </RequireProfile>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  )
}
