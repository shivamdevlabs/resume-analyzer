import { useState } from 'react'
import { downloadResumePDF } from '../services/api'
import { Spinner } from './Loader'
import './DownloadButton.css'

/**
 * Downloads resume text as a .txt file in the browser,
 * ready to be upgraded to PDF once the backend is connected.
 */
export default function DownloadButton({ resumeText, resumeId }) {
  const [state, setState] = useState('idle') // 'idle' | 'loading' | 'done'

  async function handleDownload() {
    if (!resumeText) return
    setState('loading')

    try {
      // If backend is available, try fetching a PDF
      if (resumeText) {
        try {
          const blob = await downloadResumePDF(resumeText)
          triggerDownload(blob, `careercraft_resume.pdf`, 'application/pdf')
          setState('done')
          return
        } catch (apiErr) {
          console.warn('PDF download failed, falling back to TXT', apiErr)
        }
      }

      // Fallback: download as .txt
      await new Promise(r => setTimeout(r, 600)) // UX delay
      const blob = new Blob([resumeText], { type: 'text/plain;charset=utf-8' })
      triggerDownload(blob, 'careercraft_optimized_resume.txt', 'text/plain')
      setState('done')
    } catch (err) {
      console.error('Download failed:', err)
      setState('idle')
    } finally {
      setTimeout(() => setState('idle'), 3000)
    }
  }

  return (
    <button
      type="button"
      className={`btn btn--success download-btn${state === 'done' ? ' download-btn--done' : ''}`}
      onClick={handleDownload}
      disabled={state === 'loading' || !resumeText}
      id="download-resume-btn"
      aria-label="Download your optimized resume"
      aria-live="polite"
    >
      {state === 'loading' && (
        <>
          <Spinner size={18} color="#0a1a0f" />
          Preparing…
        </>
      )}
      {state === 'done' && (
        <>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
          Downloaded!
        </>
      )}
      {state === 'idle' && (
        <>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
          Download Resume
        </>
      )}
    </button>
  )
}

function triggerDownload(blob, filename, type) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
