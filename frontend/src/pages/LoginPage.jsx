import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../components/Toast'
import { Spinner } from '../components/Loader'
import './LoginPage.css'

export default function LoginPage() {
  const { login, register, isAuthenticated, loading } = useAuth()
  const { show } = useToast()
  const navigate = useNavigate()
  const location = useLocation()

  // Tab state: 'login' | 'signup'
  const [activeTab, setActiveTab] = useState('login')

  // Form states
  const [loginData, setLoginData] = useState({ identifier: '', password: '' })
  const [signUpData, setSignUpData] = useState({
    fullName: '',
    email: '',
    mobileNumber: '',
    password: '',
    confirmPassword: ''
  })

  // Submit states
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Redirect path
  const redirectPath = location.state?.from?.pathname || '/analyze'

  // If already authenticated, redirect immediately
  useEffect(() => {
    if (isAuthenticated && !loading) {
      navigate(redirectPath, { replace: true })
    }
  }, [isAuthenticated, loading, navigate, redirectPath])

  // Handle input changes
  const handleLoginChange = (e) => {
    const { name, value } = e.target
    setLoginData(prev => ({ ...prev, [name]: value }))
  }

  const handleSignUpChange = (e) => {
    const { name, value } = e.target
    setSignUpData(prev => ({ ...prev, [name]: value }))
  }

  // Handle Login Submit
  const handleLoginSubmit = async (e) => {
    e.preventDefault()
    if (!loginData.identifier.trim() || !loginData.password.trim()) {
      show({ message: 'Please enter both your credentials and password.', type: 'error' })
      return
    }

    setIsSubmitting(true)
    const result = await login(loginData.identifier, loginData.password)
    setIsSubmitting(false)

    if (result.success) {
      show({ message: 'Welcome back to CareerCraft!', type: 'success' })
      navigate(redirectPath, { replace: true })
    } else {
      show({ message: result.error, type: 'error' })
    }
  }

  // Handle Sign Up Submit
  const handleSignUpSubmit = async (e) => {
    e.preventDefault()
    const { fullName, email, mobileNumber, password, confirmPassword } = signUpData

    // Simple validation
    if (!fullName.trim() || !email.trim() || !mobileNumber.trim() || !password.trim()) {
      show({ message: 'Please fill out all fields.', type: 'error' })
      return
    }

    if (!email.includes('@')) {
      show({ message: 'Please enter a valid email address.', type: 'error' })
      return
    }

    if (password.length < 6) {
      show({ message: 'Password must be at least 6 characters long.', type: 'error' })
      return
    }

    if (password !== confirmPassword) {
      show({ message: 'Passwords do not match.', type: 'error' })
      return
    }

    setIsSubmitting(true)
    const result = await register(fullName, email, mobileNumber, password)
    setIsSubmitting(false)

    if (result.success) {
      show({ message: 'Account created successfully! Welcome to CareerCraft.', type: 'success' })
      navigate(redirectPath, { replace: true })
    } else {
      show({ message: result.error, type: 'error' })
    }
  }

  return (
    <div className="login-page">
      {/* Glow blobs for background aesthetic */}
      <div className="glow-blobs" aria-hidden="true">
        <div className="glow-blob glow-blob--1" />
        <div className="glow-blob glow-blob--2" />
      </div>

      <div className="container container--narrow login-page__container">
        <div className="login-card card animate-fade-in-up">
          {/* Header */}
          <div className="login-card__header">
            <h1 className="login-card__title">
              {activeTab === 'login' ? (
                <>Welcome to <span className="text-gradient">CareerCraft</span></>
              ) : (
                <>Create Your <span className="text-gradient">Account</span></>
              )}
            </h1>
            <p className="login-card__subtitle">
              {activeTab === 'login' 
                ? 'Sign in to optimize your resume and track job applications.'
                : 'Get started with free ATS optimization and market insights.'}
            </p>
          </div>

          {/* Toggle Tabs */}
          <div className="tab-nav login-card__tabs">
            <button
              type="button"
              className={`tab-btn${activeTab === 'login' ? ' tab-btn--active' : ''}`}
              onClick={() => setActiveTab('login')}
            >
              Sign In
            </button>
            <button
              type="button"
              className={`tab-btn${activeTab === 'signup' ? ' tab-btn--active' : ''}`}
              onClick={() => setActiveTab('signup')}
            >
              Sign Up
            </button>
          </div>

          {/* Form */}
          {activeTab === 'login' ? (
            <form onSubmit={handleLoginSubmit} className="login-card__form animate-fade-in">
              <div className="form-group">
                <label className="form-label" htmlFor="login-identifier">
                  Email, Username, or Mobile
                </label>
                <input
                  type="text"
                  id="login-identifier"
                  name="identifier"
                  className="form-input"
                  placeholder="e.g. shivam, shivam@example.com, or 1234567890"
                  value={loginData.identifier}
                  onChange={handleLoginChange}
                  disabled={isSubmitting}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="login-password">
                  Password
                </label>
                <input
                  type="password"
                  id="login-password"
                  name="password"
                  className="form-input"
                  placeholder="••••••••"
                  value={loginData.password}
                  onChange={handleLoginChange}
                  disabled={isSubmitting}
                  required
                />
              </div>

              <button
                type="submit"
                className="btn btn--primary login-card__submit"
                disabled={isSubmitting}
              >
                {isSubmitting ? <Spinner size={20} color="#fff" /> : 'Sign In'}
              </button>
            </form>
          ) : (
            <form onSubmit={handleSignUpSubmit} className="login-card__form animate-fade-in">
              <div className="form-group">
                <label className="form-label" htmlFor="signup-fullname">
                  Full Name
                </label>
                <input
                  type="text"
                  id="signup-fullname"
                  name="fullName"
                  className="form-input"
                  placeholder="John Doe"
                  value={signUpData.fullName}
                  onChange={handleSignUpChange}
                  disabled={isSubmitting}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="signup-email">
                  Email Address
                </label>
                <input
                  type="email"
                  id="signup-email"
                  name="email"
                  className="form-input"
                  placeholder="john.doe@example.com"
                  value={signUpData.email}
                  onChange={handleSignUpChange}
                  disabled={isSubmitting}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="signup-mobile">
                  Mobile Number
                </label>
                <input
                  type="tel"
                  id="signup-mobile"
                  name="mobileNumber"
                  className="form-input"
                  placeholder="e.g. +91 98765 43210"
                  value={signUpData.mobileNumber}
                  onChange={handleSignUpChange}
                  disabled={isSubmitting}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="signup-password">
                  Password
                </label>
                <input
                  type="password"
                  id="signup-password"
                  name="password"
                  className="form-input"
                  placeholder="Min. 6 characters"
                  value={signUpData.password}
                  onChange={handleSignUpChange}
                  disabled={isSubmitting}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="signup-confirmpassword">
                  Confirm Password
                </label>
                <input
                  type="password"
                  id="signup-confirmpassword"
                  name="confirmPassword"
                  className="form-input"
                  placeholder="••••••••"
                  value={signUpData.confirmPassword}
                  onChange={handleSignUpChange}
                  disabled={isSubmitting}
                  required
                />
              </div>

              <button
                type="submit"
                className="btn btn--primary login-card__submit"
                disabled={isSubmitting}
              >
                {isSubmitting ? <Spinner size={20} color="#fff" /> : 'Create Account'}
              </button>
            </form>
          )}

          {/* Footer toggle prompt */}
          <div className="login-card__footer-prompt">
            {activeTab === 'login' ? (
              <p>
                Don't have an account?{' '}
                <button type="button" onClick={() => setActiveTab('signup')} className="link-btn">
                  Sign up free
                </button>
              </p>
            ) : (
              <p>
                Already have an account?{' '}
                <button type="button" onClick={() => setActiveTab('login')} className="link-btn">
                  Sign in
                </button>
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
