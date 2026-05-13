import { useState, useCallback } from 'react'
import { analyzeResume } from '../services/api'

export function useResumeAnalyzer() {
  const [state, setState] = useState({
    status: 'idle',      // 'idle' | 'loading' | 'success' | 'error'
    result: null,
    error: null,
  })

  const analyze = useCallback(async ({ resumeText, jobDescription, resumeFile }) => {
    if (!jobDescription?.trim()) {
      setState(s => ({ ...s, status: 'error', error: 'Please enter a job description.' }))
      return
    }
    if (!resumeText?.trim() && !resumeFile) {
      setState(s => ({ ...s, status: 'error', error: 'Please provide your resume.' }))
      return
    }

    setState({ status: 'loading', result: null, error: null })

    try {
      const data = await analyzeResume({ resumeText, jobDescription, resumeFile })
      setState({ status: 'success', result: data, error: null })
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        err.message ||
        'An unexpected error occurred. Please try again.'
      setState({ status: 'error', result: null, error: msg })
    }
  }, [])

  const reset = useCallback(() => {
    setState({ status: 'idle', result: null, error: null })
  }, [])

  return {
    ...state,
    analyze,
    reset,
    isLoading: state.status === 'loading',
    isSuccess: state.status === 'success',
    isError: state.status === 'error',
  }
}
