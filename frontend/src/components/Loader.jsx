import './Loader.css'

/* -------------------------------------------------------
   Skeleton block for arbitrary content
   ------------------------------------------------------- */
export function Skeleton({ width = '100%', height = '1rem', radius = '6px', className = '' }) {
  return (
    <div
      className={`skeleton ${className}`}
      style={{ width, height, borderRadius: radius }}
      aria-hidden="true"
    />
  )
}

/* -------------------------------------------------------
   Full result panel skeleton
   ------------------------------------------------------- */
export function ResultSkeleton() {
  return (
    <div className="result-skeleton" aria-label="Loading generated resume…" role="status">
      {/* ATS score area */}
      <div className="result-skeleton__header">
        <Skeleton width="120px" height="120px" radius="50%" />
        <div className="result-skeleton__score-text">
          <Skeleton width="140px" height="1.25rem" />
          <Skeleton width="100px" height="0.875rem" />
          <Skeleton width="160px" height="0.875rem" />
        </div>
      </div>

      <div className="result-skeleton__divider" />

      {/* Keywords */}
      <div className="result-skeleton__tags">
        {Array.from({ length: 8 }).map((_, i) => (
          <Skeleton key={i} width={`${60 + Math.random() * 60}px`} height="28px" radius="9999px" />
        ))}
      </div>

      <div className="result-skeleton__divider" />

      {/* Resume text lines */}
      <div className="result-skeleton__lines">
        <Skeleton width="55%" height="1.1rem" />
        <Skeleton width="100%" height="0.875rem" />
        <Skeleton width="95%" height="0.875rem" />
        <Skeleton width="90%" height="0.875rem" />
        <Skeleton width="80%" height="0.875rem" />
        <Skeleton width="100%" height="0.875rem" />
        <Skeleton width="70%" height="0.875rem" />
        <Skeleton width="55%" height="1.1rem" style={{ marginTop: '0.75rem' }} />
        <Skeleton width="100%" height="0.875rem" />
        <Skeleton width="88%" height="0.875rem" />
        <Skeleton width="92%" height="0.875rem" />
        <Skeleton width="76%" height="0.875rem" />
      </div>
    </div>
  )
}

/* -------------------------------------------------------
   Spinner loader
   ------------------------------------------------------- */
export function Spinner({ size = 24, color = 'var(--color-primary)' }) {
  return (
    <svg
      className="spinner"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <circle
        cx="12" cy="12" r="10"
        stroke={color}
        strokeOpacity="0.2"
        strokeWidth="2.5"
      />
      <path
        d="M12 2 a10 10 0 0 1 10 10"
        stroke={color}
        strokeWidth="2.5"
        strokeLinecap="round"
      />
    </svg>
  )
}

/* -------------------------------------------------------
   Full-page processing overlay
   ------------------------------------------------------- */
export function ProcessingOverlay({ stage = 1 }) {
  const stages = [
    { label: 'Parsing your resume…',         icon: '📄' },
    { label: 'Analyzing job description…',   icon: '🔍' },
    { label: 'Matching ATS keywords…',       icon: '🎯' },
    { label: 'Generating optimized resume…', icon: '✨' },
  ]

  const current = stages[Math.min(stage, stages.length - 1)]

  return (
    <div className="processing-overlay" role="status" aria-live="polite">
      <div className="processing-overlay__content">
        {/* Animated rings */}
        <div className="processing-rings" aria-hidden="true">
          <div className="processing-ring processing-ring--1" />
          <div className="processing-ring processing-ring--2" />
          <div className="processing-ring processing-ring--3" />
          <span className="processing-rings__icon">{current.icon}</span>
        </div>

        <p className="processing-overlay__label">{current.label}</p>

        {/* Progress dots */}
        <div className="processing-dots" aria-hidden="true">
          {stages.map((_, i) => (
            <span
              key={i}
              className={`processing-dot${i <= stage ? ' processing-dot--active' : ''}`}
            />
          ))}
        </div>

        <p className="processing-overlay__hint">
          This usually takes 15–30 seconds…
        </p>
      </div>
    </div>
  )
}
