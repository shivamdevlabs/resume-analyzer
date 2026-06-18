import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { loginUser, registerUser, getProfile } from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  // Verify token on app mount or refresh
  const verifyToken = useCallback(async () => {
    const token = localStorage.getItem('careercraft_token')
    if (!token) {
      setUser(null)
      setIsAuthenticated(false)
      setLoading(false)
      return
    }

    try {
      const userData = await getProfile()
      setUser(userData)
      setIsAuthenticated(true)
    } catch (err) {
      console.warn('Session verification failed. Token expired or invalid.', err)
      localStorage.removeItem('careercraft_token')
      setUser(null)
      setIsAuthenticated(false)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    verifyToken()
  }, [verifyToken])

  // Login handler
  const login = async (identifier, password) => {
    setLoading(true)
    try {
      const data = await loginUser({ identifier, password })
      localStorage.setItem('careercraft_token', data.access_token)
      setUser(data.user)
      setIsAuthenticated(true)
      return { success: true }
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Login failed. Please check your credentials.'
      return { success: false, error: msg }
    } finally {
      setLoading(false)
    }
  }

  // Register handler
  const register = async (fullName, email, mobileNumber, password) => {
    setLoading(true)
    try {
      const data = await registerUser({
        full_name: fullName,
        email,
        mobile_number: mobileNumber,
        password
      })
      localStorage.setItem('careercraft_token', data.access_token)
      setUser(data.user)
      setIsAuthenticated(true)
      return { success: true }
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Registration failed.'
      return { success: false, error: msg }
    } finally {
      setLoading(false)
    }
  }

  // Logout handler
  const logout = useCallback(() => {
    localStorage.removeItem('careercraft_token')
    setUser(null)
    setIsAuthenticated(false)
  }, [])

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    register,
    logout,
    checkSession: verifyToken
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
