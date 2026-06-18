import { useState, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import './Navbar.css'

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth()
  const [scrolled, setScrolled] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)
  const [dropdownOpen, setDropdownOpen] = useState(false)
  
  const location = useLocation()
  const navigate = useNavigate()

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => {
    setMenuOpen(false)
    setDropdownOpen(false)
  }, [location.pathname])

  // Close dropdown on clicking anywhere else
  useEffect(() => {
    if (!dropdownOpen) return
    const closeDropdown = () => setDropdownOpen(false)
    window.addEventListener('click', closeDropdown)
    return () => window.removeEventListener('click', closeDropdown)
  }, [dropdownOpen])

  const handleLogout = () => {
    logout()
    navigate('/')
  }

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
          {isAuthenticated ? (
            <>
              <Link to="/dashboard" className={`navbar__link${location.pathname === '/dashboard' ? ' navbar__link--active' : ''}`}>Dashboard</Link>
              <Link to="/history" className={`navbar__link${location.pathname === '/history' ? ' navbar__link--active' : ''}`}>History</Link>
            </>
          ) : (
            <>
              <a href="/#features" className="navbar__link">Features</a>
              <a href="/#how-it-works" className="navbar__link">How It Works</a>
            </>
          )}
          <Link to="/analyze" className={`navbar__link${location.pathname === '/analyze' ? ' navbar__link--active' : ''}`}>Analyzer</Link>
        </nav>

        {/* CTA */}
        <div className="navbar__actions">
          {isAuthenticated ? (
            <>
              {/* Analyze Resume Button */}
              <Link to="/analyze" className="btn btn--primary btn--sm navbar__cta-btn">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>
                  <polyline points="13 2 13 9 20 9"/>
                </svg>
                Analyze Resume
              </Link>
              
              {/* Profile Avatar / Dropdown */}
              <div className="navbar__user" onClick={(e) => e.stopPropagation()}>
                <button
                  className="navbar__avatar-btn"
                  onClick={() => setDropdownOpen(v => !v)}
                  aria-label="Toggle user menu"
                  aria-expanded={dropdownOpen}
                >
                  {user?.full_name ? user.full_name[0].toUpperCase() : 'U'}
                </button>
                {dropdownOpen && (
                  <div className="navbar__dropdown card">
                    <div className="navbar__dropdown-info">
                      <p className="navbar__dropdown-name">{user?.full_name}</p>
                      <p className="navbar__dropdown-email">{user?.email}</p>
                    </div>
                    <div className="navbar__dropdown-divider" />
                    <Link to="/dashboard" className="navbar__dropdown-link">
                      Dashboard
                    </Link>
                    <Link to="/history" className="navbar__dropdown-link">
                      History
                    </Link>
                    <div className="navbar__dropdown-divider" />
                    <button onClick={handleLogout} className="navbar__dropdown-link navbar__dropdown-link--logout">
                      Sign Out
                    </button>
                  </div>
                )}
              </div>
            </>
          ) : (
            /* Login Button (placed in same position, same style) */
            <Link to="/login" className="btn btn--primary btn--sm navbar__cta-btn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M15 12H3"/>
              </svg>
              Login
            </Link>
          )}

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
          {isAuthenticated ? (
            <>
              <Link to="/dashboard" className="navbar__mobile-link">Dashboard</Link>
              <Link to="/history" className="navbar__mobile-link">History</Link>
              <Link to="/analyze" className="navbar__mobile-link">Analyzer</Link>
              <button onClick={handleLogout} className="navbar__mobile-link navbar__mobile-link--logout" style={{textAlign: 'left', width: '100%'}}>
                Sign Out
              </button>
              <Link to="/analyze" className="btn btn--primary" style={{marginTop: '1rem'}}>
                Analyze Resume
              </Link>
            </>
          ) : (
            <>
              <a href="/#features" className="navbar__mobile-link">Features</a>
              <a href="/#how-it-works" className="navbar__mobile-link">How It Works</a>
              <Link to="/login" className="btn btn--primary" style={{marginTop: '1rem'}}>
                Login
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  )
}
