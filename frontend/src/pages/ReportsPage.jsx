import { useState, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { getAnalysisDetails } from '../services/api'
import ResultPanel from '../components/ResultPanel'
import { Spinner } from '../components/Loader'
import { useToast } from '../components/Toast'
import './ReportsPage.css'

export default function ReportsPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const { show } = useToast()
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)

  const queryParams = new URLSearchParams(location.search)
  const analysisId = queryParams.get('id')

  useEffect(() => {
    if (!analysisId) {
      show({ message: 'No report ID provided.', type: 'error' })
      navigate('/history')
      return
    }

    async function loadReport() {
      try {
        const data = await getAnalysisDetails(analysisId)
        setReport(data)
      } catch (err) {
        show({ message: 'Failed to retrieve report details.', type: 'error' })
        navigate('/history')
      } finally {
        setLoading(false)
      }
    }

    loadReport()
  }, [analysisId, navigate, show])

  const handleBack = () => {
    navigate('/history')
  }

  return (
    <div className="reports-page">
      <div className="container">
        {/* Header */}
        <div className="reports-header animate-fade-in-up">
          <div>
            <span className="section-label">Report details</span>
            <h1 className="reports-title">Analysis Report</h1>
            <p className="reports-subtitle">
              ID: {analysisId}
            </p>
          </div>
          <button onClick={handleBack} className="btn btn--outline">
            ← Back to History
          </button>
        </div>

        {/* Content */}
        {loading ? (
          <div className="reports-loading">
            <Spinner size={48} />
          </div>
        ) : report ? (
          <div className="reports-content animate-fade-in-up delay-100">
            <ResultPanel result={report} onReset={handleBack} />
          </div>
        ) : null}
      </div>
    </div>
  )
}
