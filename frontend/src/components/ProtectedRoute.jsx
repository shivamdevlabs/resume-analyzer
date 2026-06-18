import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Spinner } from './Loader'

export default function ProtectedRoute({ children }) {
  const location = useLocation()
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '80vh',
        background: 'var(--color-bg)',
        color: 'var(--color-text-muted)'
      }}>
        <Spinner size={48} />
      </div>
    )
  }

  if (!isAuthenticated) {
    // Redirect to login page, saving the page they tried to access
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  return children
}
