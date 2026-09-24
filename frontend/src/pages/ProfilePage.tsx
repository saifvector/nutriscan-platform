import { Navigate } from 'react-router-dom'

/**
 * Legacy ProfilePage permanently replaced by PatientRecordsPage.
 * Clinical workflow redirects to /patients.
 */
export default function ProfilePage() {
  return <Navigate to="/patients" replace />
}
