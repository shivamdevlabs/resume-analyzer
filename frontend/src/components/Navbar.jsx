import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import './Navbar.css'

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)
  const location = useLocation()

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => {
    setMenuOpen(false)
  }, [location.pathname])

  return (
    <header className={`navbar${scrolled ? ' navbar--scrolled' : ''}`} id="navbar">
      <div className="container navbar__inner">
        {/* Logo */}
        <Link to="/" className="navbar__logo" aria-label="CareerCraft home">
          <span className="navbar__logo-icon" aria-hidden="true">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect width="32" height="32" rx="10" fill="url(#logoGrad)"/>
              <path d="M9 10h9M9 15h14M9 20h11" stroke="#fff" strokeWidth="2.2" strokeLinecap="round"/>
              <circle cx="24" cy="10" r="2.5" fill="#43E97B"/>
              <defs>
                <linearGradient id="logoGrad" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
                  <stop stopColor="#6C63FF"/>
                  <stop offset="1" stopColor="#FF6584"/>
                </linearGradient>
              </defs>
            </svg>
          </span>
          <span className="navbar__logo-text">
            Career<span className="text-gradient">Craft</span>
          </span>
        </Link>

        {/* Desktop nav */}
        <nav className="navbar__links" aria-label="Main navigation">
          <Link to="/" className={`navbar__link${location.pathname === '/' ? ' navbar__link--active' : ''}`}>Home</Link>
          <Link to="/analyze" className={`navbar__link${location.pathname === '/analyze' ? ' navbar__link--active' : ''}`}>Analyzer</Link>
          <a href="#features" className="navbar__link">Features</a>
          <a href="#how-it-works" className="navbar__link">How It Works</a>
        </nav>

        {/* CTA */}
        <div className="navbar__actions">
          <Link to="/analyze" className="btn btn--primary btn--sm">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>
              <polyline points="13 2 13 9 20 9"/>
            </svg>
            Analyze Resume
          </Link>

          {/* Hamburger */}
          <button
            className={`navbar__hamburger${menuOpen ? ' navbar__hamburger--open' : ''}`}
            onClick={() => setMenuOpen(v => !v)}
            aria-label="Toggle menu"
            aria-expanded={menuOpen}
          >
            <span/><span/><span/>
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      <div className={`navbar__mobile${menuOpen ? ' navbar__mobile--open' : ''}`} aria-hidden={!menuOpen}>
        <nav className="navbar__mobile-links">
          <Link to="/" className="navbar__mobile-link">Home</Link>
          <Link to="/analyze" className="navbar__mobile-link">Analyzer</Link>
          <a href="#features" className="navbar__mobile-link">Features</a>
          <a href="#how-it-works" className="navbar__mobile-link">How It Works</a>
          <Link to="/analyze" className="btn btn--primary" style={{marginTop: '0.5rem'}}>
            Analyze Resume
          </Link>
        </nav>
      </div>
    </header>
  )
}
