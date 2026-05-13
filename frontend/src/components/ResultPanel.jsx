import { useState, useEffect, useRef } from 'react'
import DownloadButton from './DownloadButton'
import './ResultPanel.css'

/* -------------------------------------------------------
   ATS Score Gauge
   ------------------------------------------------------- */
function ATSGauge({ score }) {
  const [animated, setAnimated] = useState(0)
  const radius = 80
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (animated / 100) * circumference

  useEffect(() => {
    const timeout = setTimeout(() => {
      let start = null
      const duration = 1200
      function step(timestamp) {
        if (!start) start = timestamp
        const progress = Math.min((timestamp - start) / duration, 1)
        const eased = 1 - Math.pow(1 - progress, 3) // ease-out-cubic
        setAnimated(Math.round(eased * score))
        if (progress < 1) requestAnimationFrame(step)
      }
      requestAnimationFrame(step)
    }, 300)
    return () => clearTimeout(timeout)
  }, [score])

  const color =
    score >= 80 ? 'var(--color-accent)' :
    score >= 60 ? 'var(--color-warning)' :
    'var(--color-secondary)'

  const label =
    score >= 80 ? 'Excellent' :
    score >= 60 ? 'Good' :
    score >= 40 ? 'Fair' : 'Needs Work'

  return (
    <div className="ats-gauge" aria-label={`ATS score: ${score} out of 100, rated ${label}`}>
      <svg width="200" height="200" viewBox="0 0 200 200" aria-hidden="true">
        {/* Background track */}
        <circle
          cx="100" cy="100" r={radius}
          fill="none"
          stroke="var(--color-surface-3)"
          strokeWidth="10"
        />
        {/* Glow filter */}
        <defs>
          <filter id="scoreGlow">
            <feGaussianBlur stdDeviation="4" result="blur"/>
            <feMerge>
              <feMergeNode in="blur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        {/* Score arc */}
        <circle
          cx="100" cy="100" r={radius}
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          transform="rotate(-90 100 100)"
          filter="url(#scoreGlow)"
          style={{ transition: 'stroke-dashoffset 0.05s linear, stroke 0.5s ease' }}
        />
        {/* Score number */}
        <text
          x="100" y="96"
          textAnchor="middle"
          fontSize="36"
          fontWeight="800"
          fontFamily="Inter, sans-serif"
          fill={color}
        >
          {animated}
        </text>
        <text
          x="100" y="118"
          textAnchor="middle"
          fontSize="13"
          fontWeight="600"
          fontFamily="Inter, sans-serif"
          fill="var(--color-text-muted)"
        >
          {label}
        </text>
      </svg>
      <p className="ats-gauge__label">ATS Score</p>
    </div>
  )
}

/* -------------------------------------------------------
   Keyword chips
   ------------------------------------------------------- */
function KeywordChips({ keywords }) {
  if (!keywords?.length) return null
  return (
    <div className="keyword-chips" aria-label="Matched ATS keywords">
      {keywords.map(kw => (
        <span key={kw} className="keyword-chip">
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
          {kw}
        </span>
      ))}
    </div>
  )
}

/* -------------------------------------------------------
   Improvement list
   ------------------------------------------------------- */
function Improvements({ items }) {
  if (!items?.length) return null
  return (
    <div className="improvements" aria-label="Improvements made">
      <h4 className="improvements__title">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
          <polyline points="17 6 23 6 23 12"/>
        </svg>
        Improvements Made
      </h4>
      <ul className="improvements__list">
        {items.map((item, i) => (
          <li key={i} className="improvements__item" style={{ animationDelay: `${i * 0.08}s` }}>
            <span className="improvements__bullet" aria-hidden="true">✦</span>
            {item}
          </li>
        ))}
      </ul>
    </div>
  )
}

/* -------------------------------------------------------
   Main Result Panel
   ------------------------------------------------------- */
export default function ResultPanel({ result, onReset }) {
  const textRef = useRef(null)
  const [copied, setCopied] = useState(false)

  async function handleCopy() {
    if (!result?.generated_resume) return
    try {
      await navigator.clipboard.writeText(result.generated_resume)
      setCopied(true)
      setTimeout(() => setCopied(false), 2500)
    } catch {
      /* clipboard api not available */
    }
  }

  return (
    <div className="result-panel animate-fade-in-up">
      {/* Mock badge */}
      {result.mock && (
        <div className="result-panel__mock-badge" role="note">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          Demo mode – connect backend for real AI results
        </div>
      )}

      {/* ---- Score section ---- */}
      <div className="result-panel__score-section card card--no-hover">
        <ATSGauge score={result.ats_score ?? 0} />
        <div className="result-panel__score-stats">
          <div className="result-panel__stat">
            <span className="result-panel__stat-value">{result.matched_keywords?.length ?? 0}</span>
            <span className="result-panel__stat-label">Keywords Matched</span>
          </div>
          <div className="result-panel__stat-divider" />
          <div className="result-panel__stat">
            <span className="result-panel__stat-value">{result.total_keywords ?? 0}</span>
            <span className="result-panel__stat-label">Total Keywords</span>
          </div>
          <div className="result-panel__stat-divider" />
          <div className="result-panel__stat">
            <span className="result-panel__stat-value">
              {result.total_keywords
                ? Math.round((result.matched_keywords?.length / result.total_keywords) * 100)
                : 0}%
            </span>
            <span className="result-panel__stat-label">Match Rate</span>
          </div>
        </div>
      </div>

      {/* ---- Keywords ---- */}
      <div className="result-panel__section">
        <h3 className="result-panel__section-title">
          🎯 Matched ATS Keywords
        </h3>
        <KeywordChips keywords={result.matched_keywords} />
      </div>

      {/* ---- Improvements ---- */}
      <Improvements items={result.improvements} />

      {/* ---- Generated Resume ---- */}
      <div className="result-panel__section result-panel__resume-section">
        <div className="result-panel__resume-header">
          <h3 className="result-panel__section-title">
            ✨ Your ATS-Optimized Resume
          </h3>
          <div className="result-panel__resume-actions">
            <button
              type="button"
              className={`btn btn--ghost btn--sm${copied ? ' btn--success' : ''}`}
              onClick={handleCopy}
              id="copy-resume-btn"
              aria-live="polite"
            >
              {copied ? (
                <>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                  Copied!
                </>
              ) : (
                <>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                  </svg>
                  Copy
                </>
              )}
            </button>
          </div>
        </div>

        <pre className="result-panel__resume-text" ref={textRef} tabIndex={0} aria-label="Generated resume text">
          {result.generated_resume}
        </pre>
      </div>

      {/* ---- Download & Reset ---- */}
      <div className="result-panel__footer">
        <DownloadButton
          resumeText={result.generated_resume}
          resumeId={result.analysis_id}
        />
        <button
          type="button"
          className="btn btn--outline"
          onClick={onReset}
          id="analyze-another-btn"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <polyline points="1 4 1 10 7 10"/>
            <path d="M3.51 15a9 9 0 1 0 .49-3.34"/>
          </svg>
          Analyze Another
        </button>
      </div>
    </div>
  )
}
