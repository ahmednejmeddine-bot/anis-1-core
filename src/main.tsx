import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import CommanderDashboard from '../dashboard/commander_dashboard'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <CommanderDashboard />
  </StrictMode>
)
