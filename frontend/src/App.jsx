import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import LandingPage from './pages/LandingPage'
import AnalyzePage from './pages/AnalyzePage'
import { ToastProvider } from './components/Toast'

function App() {
  return (
    <ToastProvider>
      <div className="app-wrapper">
        <Navbar />
        <main className="app-main">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/analyze" element={<AnalyzePage />} />
          </Routes>
        </main>
      </div>
    </ToastProvider>
  )
}

export default App
