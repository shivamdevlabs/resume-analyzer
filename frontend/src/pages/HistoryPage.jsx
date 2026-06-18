import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { getUserHistory, downloadSavedPDF } from '../services/api'
import { Spinner } from '../components/Loader'
import { useToast } from '../components/Toast'
import './HistoryPage.css'

export default function HistoryPage() {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [downloadingId, setDownloadingId] = useState(null)
  const { show } = useToast()
  const navigate = useNavigate()

  useEffect(() => {
    async function loadHistory() {
      try {
        const data = await getUserHistory()
        setHistory(data || [])
      } catch (err) {
        show({ message: 'Failed to load optimization history.', type: 'error' })
      } finally {
        setLoading(false)
      }
    }
    loadHistory()
  }, [show])

  // Handle PDF Download
  const handleDownload = async (analysisId) => {
    setDownloadingId(analysisId)
    show({ message: 'Generating PDF download...', type: 'info', duration: 2000 })
    try {
      const blob = await downloadSavedPDF(analysisId)
      const url = window.URL.createObjectURL(new Blob([blob], { type: 'application/pdf' }))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `ATS_Resume_${analysisId.slice(0, 8)}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      show({ message: 'Download started!', type: 'success' })
    } catch (err) {
      show({ message: 'Failed to download PDF. Please try again.', type: 'error' })
    } finally {
      setDownloadingId(null)
    }
  }

  const getScoreColorClass = (score) => {
    if (score >= 80) return 'score-badge--green'
    if (score >= 60) return 'score-badge--orange'
    return 'score-badge--red'
  }

  return (
    <div className="history-page">
      <div className="container">
        {/* Header */}
        <div className="history-header animate-fade-in-up">
          <div>
            <span className="section-label">Your Archive</span>
            <h1 className="history-title">Resume History</h1>
            <p className="history-subtitle">
              View, analyze, and download your previously optimized resumes.
            </p>
          </div>
          <Link to="/analyze" className="btn btn--outline">
            Optimize Another
          </Link>
        </div>

        {/* List Content */}
        {loading ? (
          <div className="history-loading">
            <Spinner size={48} />
          </div>
        ) : history.length === 0 ? (
          <div className="history-empty card card--no-hover animate-fade-in-up delay-100">
            <div className="history-empty__icon">📁</div>
            <h2>No Resumes Found</h2>
            <p>You haven't optimized any resumes yet. Paste your first resume and job description to get started.</p>
            <Link to="/analyze" className="btn btn--primary">
              Get Started Free
            </Link>
          </div>
        ) : (
          <div className="history-list animate-fade-in-up delay-100">
            {history.map((item, idx) => (
              <div className="history-item card card--no-hover" key={item.analysis_id}>
                <div className="history-item__left">
                  <div className={`score-badge ${getScoreColorClass(item.ats_score)}`}>
                    <span className="score-badge__value">{item.ats_score}</span>
                    <span className="score-badge__label">Score</span>
                  </div>

                  <div className="history-item__info">
                    <h3 className="history-item__job-snippet">
                      {item.job_description_snippet}
                    </h3>
                    <div className="history-item__meta">
                      <span className="meta-tag">
                        🎯 Keywords: {item.matched_keywords_count}/{item.total_keywords_count}
                      </span>
                      <span className="meta-divider">•</span>
                      <span className="meta-tag">
                        📅 {new Date(item.created_at).toLocaleDateString(undefined, {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="history-item__actions">
                  <button
                    onClick={() => navigate(`/reports?id=${item.analysis_id}`)}
                    className="btn btn--ghost btn--sm"
                  >
                    View Report
                  </button>
                  <button
                    onClick={() => handleDownload(item.analysis_id)}
                    className="btn btn--primary btn--sm"
                    disabled={downloadingId === item.analysis_id}
                  >
                    {downloadingId === item.analysis_id ? (
                      <Spinner size={16} color="#fff" />
                    ) : (
                      <>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4m4-5 5 5 5-5m-5 5V3"/>
                        </svg>
                        Download PDF
                      </>
                    )}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
