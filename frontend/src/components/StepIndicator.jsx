import './StepIndicator.css'

const STEPS = [
  {
    id: 1,
    label: 'Provide Input',
    description: 'Resume + Job Description',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
        <line x1="16" y1="13" x2="8" y2="13"/>
        <line x1="16" y1="17" x2="8" y2="17"/>
        <polyline points="10 9 9 9 8 9"/>
      </svg>
    ),
  },
  {
    id: 2,
    label: 'AI Generation',
    description: 'Tailoring to ATS standards',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
      </svg>
    ),
  },
  {
    id: 3,
    label: 'Download',
    description: 'Get your optimized resume',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
        <polyline points="7 10 12 15 17 10"/>
        <line x1="12" y1="15" x2="12" y2="3"/>
      </svg>
    ),
  },
]

/**
 * @param {{ currentStep: 1 | 2 | 3 }} props
 */
export default function StepIndicator({ currentStep }) {
  return (
    <div className="step-indicator" role="list" aria-label="Progress steps">
      {STEPS.map((step, idx) => {
        const status =
          step.id < currentStep ? 'done' :
          step.id === currentStep ? 'active' : 'pending'

        return (
          <div key={step.id} className="step-indicator__item" role="listitem">
            {/* Connector line */}
            {idx > 0 && (
              <div className={`step-indicator__line step-indicator__line--${step.id <= currentStep ? 'filled' : 'empty'}`} aria-hidden="true" />
            )}

            <div className={`step-indicator__step step-indicator__step--${status}`}>
              {/* Circle */}
              <div className="step-indicator__circle" aria-current={status === 'active' ? 'step' : undefined}>
                {status === 'done' ? (
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                ) : (
                  <span className="step-indicator__icon">{step.icon}</span>
                )}
              </div>

              {/* Labels */}
              <div className="step-indicator__labels">
                <span className="step-indicator__label">{step.label}</span>
                <span className="step-indicator__desc">{step.description}</span>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
