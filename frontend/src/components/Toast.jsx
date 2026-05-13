import { createContext, useContext, useState, useCallback, useRef } from 'react'
import './Toast.css'

/* -------------------------------------------------------
   Context
   ------------------------------------------------------- */
const ToastContext = createContext(null)

let idCounter = 0

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])
  const timers = useRef({})

  const remove = useCallback((id) => {
    setToasts(prev => prev.map(t => t.id === id ? { ...t, exiting: true } : t))
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id))
      clearTimeout(timers.current[id])
    }, 350)
  }, [])

  const show = useCallback(({ message, type = 'info', duration = 4000 }) => {
    const id = ++idCounter
    setToasts(prev => [...prev, { id, message, type, exiting: false }])
    timers.current[id] = setTimeout(() => remove(id), duration)
    return id
  }, [remove])

  return (
    <ToastContext.Provider value={{ show, remove }}>
      {children}
      <div className="toast-container" aria-live="polite" aria-label="Notifications">
        {toasts.map(toast => (
          <div
            key={toast.id}
            className={`toast toast--${toast.type}${toast.exiting ? ' toast--exit' : ''}`}
            role="alert"
          >
            <span className="toast__icon" aria-hidden="true">
              {toast.type === 'success' && '✓'}
              {toast.type === 'error' && '✕'}
              {toast.type === 'warning' && '⚠'}
              {toast.type === 'info' && 'ℹ'}
            </span>
            <span className="toast__message">{toast.message}</span>
            <button
              className="toast__close"
              onClick={() => remove(toast.id)}
              aria-label="Dismiss notification"
            >
              ×
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

/* -------------------------------------------------------
   Hook
   ------------------------------------------------------- */
export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used inside ToastProvider')
  return ctx
}
