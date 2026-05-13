import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Spinner } from './Loader'
import './ResumeForm.css'

const MAX_JD_CHARS = 5000
const ACCEPTED_TYPES = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'text/plain': ['.txt'],
}

export default function ResumeForm({ onSubmit, isLoading }) {
  const [resumeTab, setResumeTab] = useState('paste') // 'paste' | 'upload'
  const [resumeText, setResumeText] = useState('')
  const [resumeFile, setResumeFile] = useState(null)
  const [jobDescription, setJobDescription] = useState('')
  const [errors, setErrors] = useState({})

  /* ---- Dropzone ---- */
  const onDrop = useCallback((accepted, rejected) => {
    if (rejected.length) {
      setErrors(e => ({ ...e, file: 'Only PDF, DOCX, or TXT files are supported.' }))
      return
    }
    if (accepted.length) {
      setResumeFile(accepted[0])
      setErrors(e => ({ ...e, file: null }))
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_TYPES,
    maxFiles: 1,
    maxSize: 5 * 1024 * 1024, // 5 MB
    disabled: isLoading,
  })

  /* ---- Validation ---- */
  function validate() {
    const errs = {}
    if (resumeTab === 'paste' && !resumeText.trim()) {
      errs.resume = 'Please paste your resume text.'
    }
    if (resumeTab === 'upload' && !resumeFile) {
      errs.file = 'Please upload a resume file.'
    }
    if (!jobDescription.trim()) {
      errs.jd = 'Please enter the job description.'
    } else if (jobDescription.trim().length < 50) {
      errs.jd = 'Job description seems too short. Please paste the full JD.'
    }
    setErrors(errs)
    return Object.keys(errs).length === 0
  }

  /* ---- Submit ---- */
  function handleSubmit(e) {
    e.preventDefault()
    if (!validate()) return
    onSubmit({ resumeText, jobDescription, resumeFile })
  }

  function removeFile() {
    setResumeFile(null)
  }

  const jdLength = jobDescription.length
  const jdWarning = jdLength > MAX_JD_CHARS * 0.9

  return (
    <form className="resume-form card card--no-hover" onSubmit={handleSubmit} noValidate id="resume-form">
      <div className="resume-form__header">
        <h2 className="resume-form__title">
          <span className="resume-form__title-icon" aria-hidden="true">📝</span>
          Your Information
        </h2>
        <p className="resume-form__subtitle">
          Provide your resume and the target job description
        </p>
      </div>

      {/* ---- Resume Input Section ---- */}
      <div className="form-group">
        <label className="form-label">
          Your Resume
          <span className="label-badge">Required</span>
        </label>

        {/* Tab switcher */}
        <div className="tab-nav" role="tablist" aria-label="Resume input method">
          <button
            type="button"
            role="tab"
            id="tab-paste"
            aria-controls="tabpanel-paste"
            aria-selected={resumeTab === 'paste'}
            className={`tab-btn${resumeTab === 'paste' ? ' tab-btn--active' : ''}`}
            onClick={() => { setResumeTab('paste'); setErrors(e => ({ ...e, resume: null, file: null })) }}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>
              <rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>
            </svg>
            Paste Text
          </button>
          <button
            type="button"
            role="tab"
            id="tab-upload"
            aria-controls="tabpanel-upload"
            aria-selected={resumeTab === 'upload'}
            className={`tab-btn${resumeTab === 'upload' ? ' tab-btn--active' : ''}`}
            onClick={() => { setResumeTab('upload'); setErrors(e => ({ ...e, resume: null, file: null })) }}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/>
              <line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
            Upload File
          </button>
        </div>

        {/* Paste Panel */}
        {resumeTab === 'paste' && (
          <div id="tabpanel-paste" role="tabpanel" aria-labelledby="tab-paste">
            <textarea
              id="resume-text"
              className={`form-textarea resume-form__resume-textarea${errors.resume ? ' form-textarea--error' : ''}`}
              value={resumeText}
              onChange={e => { setResumeText(e.target.value); setErrors(err => ({ ...err, resume: null })) }}
              placeholder="Paste your full resume here…&#10;&#10;Include your work experience, education, skills, and achievements."
              disabled={isLoading}
              aria-invalid={!!errors.resume}
              aria-describedby={errors.resume ? 'resume-error' : undefined}
            />
            {errors.resume && <p className="form-error" id="resume-error" role="alert">{errors.resume}</p>}
          </div>
        )}

        {/* Upload Panel */}
        {resumeTab === 'upload' && (
          <div id="tabpanel-upload" role="tabpanel" aria-labelledby="tab-upload">
            {!resumeFile ? (
              <div
                {...getRootProps()}
                className={`dropzone${isDragActive ? ' dropzone--active' : ''}${errors.file ? ' dropzone--error' : ''}`}
                id="dropzone"
              >
                <input {...getInputProps()} aria-label="Upload resume file" />
                <div className="dropzone__content">
                  <div className={`dropzone__icon${isDragActive ? ' dropzone__icon--active' : ''}`} aria-hidden="true">
                    {isDragActive ? '📂' : '📎'}
                  </div>
                  <p className="dropzone__title">
                    {isDragActive ? 'Drop it here!' : 'Drag & drop your resume'}
                  </p>
                  <p className="dropzone__subtitle">
                    or <span className="dropzone__browse">browse files</span>
                  </p>
                  <p className="dropzone__hint">PDF, DOCX, TXT · Max 5 MB</p>
                </div>
              </div>
            ) : (
              <div className="file-preview">
                <div className="file-preview__icon" aria-hidden="true">
                  {resumeFile.name.endsWith('.pdf') ? '📕' : resumeFile.name.endsWith('.docx') ? '📘' : '📄'}
                </div>
                <div className="file-preview__info">
                  <p className="file-preview__name">{resumeFile.name}</p>
                  <p className="file-preview__size">{(resumeFile.size / 1024).toFixed(1)} KB</p>
                </div>
                <button
                  type="button"
                  className="file-preview__remove"
                  onClick={removeFile}
                  aria-label={`Remove ${resumeFile.name}`}
                  disabled={isLoading}
                >
                  ✕
                </button>
              </div>
            )}
            {errors.file && <p className="form-error" role="alert">{errors.file}</p>}
          </div>
        )}
      </div>

      {/* ---- Job Description ---- */}
      <div className="form-group">
        <label className="form-label" htmlFor="job-description">
          Job Description
          <span className="label-badge">Required</span>
        </label>
        <textarea
          id="job-description"
          className={`form-textarea resume-form__jd-textarea${errors.jd ? ' form-textarea--error' : ''}`}
          value={jobDescription}
          onChange={e => { setJobDescription(e.target.value); setErrors(err => ({ ...err, jd: null })) }}
          placeholder="Paste the full job description here…&#10;&#10;Include responsibilities, qualifications, skills required, and any specific requirements."
          maxLength={MAX_JD_CHARS}
          disabled={isLoading}
          aria-invalid={!!errors.jd}
          aria-describedby={errors.jd ? 'jd-error' : 'jd-counter'}
        />
        <div className="resume-form__jd-footer">
          {errors.jd
            ? <p className="form-error" id="jd-error" role="alert">{errors.jd}</p>
            : <span />
          }
          <span id="jd-counter" className={`char-counter${jdWarning ? ' char-counter--warning' : ''}`}>
            {jdLength.toLocaleString()} / {MAX_JD_CHARS.toLocaleString()}
          </span>
        </div>
      </div>

      {/* ---- Submit ---- */}
      <button
        type="submit"
        className="btn btn--primary btn--lg resume-form__submit"
        disabled={isLoading}
        id="analyze-btn"
        aria-busy={isLoading}
      >
        {isLoading ? (
          <>
            <Spinner size={20} color="#fff" />
            Analyzing…
          </>
        ) : (
          <>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
            </svg>
            Analyze &amp; Generate Resume
          </>
        )}
      </button>

      {/* Tips */}
      <div className="resume-form__tips">
        <p className="resume-form__tips-title">💡 Tips for best results</p>
        <ul className="resume-form__tips-list">
          <li>Include your complete work history with dates</li>
          <li>Paste the entire job description, not just highlights</li>
          <li>Include your education and certifications</li>
        </ul>
      </div>
    </form>
  )
}
