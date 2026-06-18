import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getUserHistory } from '../services/api'
import { Spinner } from '../components/Loader'
import './DashboardPage.css'

export default function DashboardPage() {
  const { user } = useAuth()
  const [stats, setStats] = useState({
    totalOptimizations: 0,
    averageScore: 0,
    highestScore: 0,
    loading: true
  })

  useEffect(() => {
    async function loadStats() {
      try {
        const history = await getUserHistory()
        if (history && history.length > 0) {
          const scores = history.map(h => h.ats_score)
          const total = history.length
          const avg = Math.round(scores.reduce((a, b) => a + b, 0) / total)
          const highest = Math.max(...scores)

          setStats({
            totalOptimizations: total,
            averageScore: avg,
            highestScore: highest,
            loading: false
          })
        } else {
          setStats({
            totalOptimizations: 0,
            averageScore: 0,
            highestScore: 0,
            loading: false
          })
        }
      } catch (err) {
        console.error('Failed to load dashboard stats', err)
        setStats(prev => ({ ...prev, loading: false }))
      }
    }

    loadStats()
  }, [])

  return (
    <div className="dashboard-page">
      <div className="container">
        {/* Header */}
        <div className="dashboard-header animate-fade-in-up">
          <div>
            <span className="section-label">User Dashboard</span>
            <h1 className="dashboard-title">
              Welcome back, <span className="text-gradient">{user?.full_name || 'CareerCrafter'}</span>!
            </h1>
            <p className="dashboard-subtitle">
              Track your ATS performance, manage generated resumes, and check application analytics.
            </p>
          </div>
          <Link to="/analyze" className="btn btn--primary">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M12 5v14M5 12h14"/>
            </svg>
            Optimize New Resume
          </Link>
        </div>

        {/* Stats Grid */}
        {stats.loading ? (
          <div className="dashboard-loading">
            <Spinner size={48} />
          </div>
        ) : (
          <div className="stats-grid animate-fade-in-up delay-100">
            <div className="stat-card card">
              <span className="stat-card__icon" aria-hidden="true">🎯</span>
              <div className="stat-card__content">
                <span className="stat-card__value">{stats.totalOptimizations}</span>
                <span className="stat-card__label">Total Optimizations</span>
              </div>
            </div>

            <div className="stat-card card">
              <span className="stat-card__icon" aria-hidden="true">📈</span>
              <div className="stat-card__content">
                <span className="stat-card__value">
                  {stats.averageScore || '--'}
                  {stats.averageScore ? <span className="stat-card__suffix">/100</span> : ''}
                </span>
                <span className="stat-card__label">Average ATS Score</span>
              </div>
            </div>

            <div className="stat-card card">
              <span className="stat-card__icon" aria-hidden="true">🏆</span>
              <div className="stat-card__content">
                <span className="stat-card__value">
                  {stats.highestScore || '--'}
                  {stats.highestScore ? <span className="stat-card__suffix">/100</span> : ''}
                </span>
                <span className="stat-card__label">Highest Score Achieved</span>
              </div>
            </div>
          </div>
        )}

        {/* Info & Quick tips */}
        <div className="dashboard-row animate-fade-in-up delay-200">
          <div className="dashboard-col card card--no-hover">
            <h2 className="dashboard-sub-title">Your Optimization Plan</h2>
            <div className="plan-details">
              <div className="plan-badge">
                <span className="plan-badge__tier">Free Tier</span>
                <span className="plan-badge__status">Active</span>
              </div>
              <p className="plan-desc">
                You currently have access to our core Gemini-powered ATS Resume Analyzer, which includes direct keyword extraction, score calculation, and standard PDF generation.
              </p>
              <div className="plan-features">
                <div className="plan-feature-item">
                  <span className="check">✓</span> <span>Unlimited Standard Analyses</span>
                </div>
                <div className="plan-feature-item">
                  <span className="check">✓</span> <span>High-speed AI Processing</span>
                </div>
                <div className="plan-feature-item">
                  <span className="check">✓</span> <span>Stateless PDF Downloads</span>
                </div>
              </div>
            </div>
          </div>

          <div className="dashboard-col card card--no-hover">
            <h2 className="dashboard-sub-title">ATS Success Tips</h2>
            <ul className="tips-list">
              <li>
                <strong>Target High-Value Keywords:</strong> Always paste the specific job description for the position you're targeting. General optimizations are less effective.
              </li>
              <li>
                <strong>Quantify Achievements:</strong> Ensure your resume includes numeric metrics (e.g. "increased sales by 25%") to make your bullet points stand out.
              </li>
              <li>
                <strong>Use Standard Headings:</strong> ATS scanners look for standard sections like "Work Experience", "Education", and "Skills". Avoid creative section names.
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
