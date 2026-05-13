import { Link } from "react-router-dom";
import "./LandingPage.css";

/* -------------------------------------------------------
   Particle blobs (purely decorative)
   ------------------------------------------------------- */
function GlowBlobs() {
  return (
    <div className="glow-blobs" aria-hidden="true">
      <div className="glow-blob glow-blob--1" />
      <div className="glow-blob glow-blob--2" />
      <div className="glow-blob glow-blob--3" />
    </div>
  );
}

/* -------------------------------------------------------
   Animated stat counter
   ------------------------------------------------------- */
function StatCard({ value, label, suffix = "" }) {
  return (
    <div className="hero-stat">
      <span className="hero-stat__value">
        {value}
        <span className="hero-stat__suffix">{suffix}</span>
      </span>
      <span className="hero-stat__label">{label}</span>
    </div>
  );
}

/* -------------------------------------------------------
   Feature card
   ------------------------------------------------------- */
function FeatureCard({ icon, title, description, delay = 0 }) {
  return (
    <div
      className="feature-card card animate-fade-in-up"
      style={{ animationDelay: `${delay}s` }}
    >
      <div className="feature-card__icon" aria-hidden="true">
        {icon}
      </div>
      <h3 className="feature-card__title">{title}</h3>
      <p className="feature-card__desc">{description}</p>
    </div>
  );
}

/* -------------------------------------------------------
   Step card
   ------------------------------------------------------- */
function StepCard({ number, title, description, delay = 0 }) {
  return (
    <div
      className="step-card animate-fade-in-up"
      style={{ animationDelay: `${delay}s` }}
    >
      <div className="step-card__number" aria-hidden="true">
        {number}
      </div>
      <h3 className="step-card__title">{title}</h3>
      <p className="step-card__desc">{description}</p>
    </div>
  );
}

/* -------------------------------------------------------
   Testimonial card
   ------------------------------------------------------- */
function TestimonialCard({ quote, author, role, score, delay = 0 }) {
  return (
    <div
      className="testimonial-card card animate-fade-in-up"
      style={{ animationDelay: `${delay}s` }}
    >
      <div className="testimonial-card__score">
        <svg width="40" height="40" viewBox="0 0 40 40" aria-hidden="true">
          <circle
            cx="20"
            cy="20"
            r="17"
            fill="none"
            stroke="var(--color-surface-3)"
            strokeWidth="3"
          />
          <circle
            cx="20"
            cy="20"
            r="17"
            fill="none"
            stroke="var(--color-accent)"
            strokeWidth="3"
            strokeLinecap="round"
            strokeDasharray={`${(score / 100) * 107} 107`}
            transform="rotate(-90 20 20)"
          />
          <text
            x="20"
            y="25"
            textAnchor="middle"
            fontSize="11"
            fontWeight="800"
            fontFamily="Inter, sans-serif"
            fill="var(--color-accent)"
          >
            {score}
          </text>
        </svg>
      </div>
      <p className="testimonial-card__quote">"{quote}"</p>
      <div className="testimonial-card__author">
        <span className="testimonial-card__name">{author}</span>
        <span className="testimonial-card__role">{role}</span>
      </div>
    </div>
  );
}

/* -------------------------------------------------------
   Landing Page
   ------------------------------------------------------- */
export default function LandingPage() {
  return (
    <div className="landing">
      <GlowBlobs />

      {/* ====== HERO ====== */}
      <section className="hero" aria-label="Hero">
        <div className="container hero__inner">
          <div className="hero__badge animate-fade-in-up">
            <span className="hero__badge-dot" aria-hidden="true" />
            AI-Powered Resume Optimization
          </div>

          <h1 className="hero__headline animate-fade-in-up delay-100">
            Land Your Dream Job
            <br />
            with an <span className="text-gradient">ATS-Optimized</span>
            <br />
            Resume
          </h1>

          <p className="hero__subtext animate-fade-in-up delay-200">
            CareerCraft uses advanced AI to analyze your resume against any job
            description and generates a tailored, keyword-rich resume that beats
            Applicant Tracking Systems — giving you the edge you deserve.
          </p>

          <div className="hero__ctas animate-fade-in-up delay-300">
            <Link
              to="/analyze"
              className="btn btn--primary btn--xl"
              id="hero-cta-primary"
            >
              <svg
                width="22"
                height="22"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
              </svg>
              Start Optimizing Free
            </Link>
            <a href="#how-it-works" className="btn btn--outline btn--xl">
              See How It Works
            </a>
          </div>

          {/* Stats */}
          <div className="hero__stats animate-fade-in-up delay-400">
            <StatCard value="3×" label="More Interview Calls" />
            <div className="hero__stats-divider" aria-hidden="true" />
            <StatCard value="87" label="Average ATS Score" suffix="+" />
            <div className="hero__stats-divider" aria-hidden="true" />
            <StatCard value="15" label="Seconds to Analyze" suffix="s" />
          </div>
        </div>

        {/* Floating resume mockup */}
        <div className="hero__mockup animate-float" aria-hidden="true">
          <div className="mockup-card">
            <div className="mockup-card__header">
              <div className="mockup-dot" />
              <div className="mockup-dot" />
              <div className="mockup-dot" />
              <span>careercraft_resume.pdf</span>
            </div>
            <div className="mockup-card__body">
              <div className="mockup-score">
                <svg width="70" height="70" viewBox="0 0 70 70">
                  <circle
                    cx="35"
                    cy="35"
                    r="28"
                    fill="none"
                    stroke="var(--color-surface-3)"
                    strokeWidth="5"
                  />
                  <circle
                    cx="35"
                    cy="35"
                    r="28"
                    fill="none"
                    stroke="var(--color-accent)"
                    strokeWidth="5"
                    strokeLinecap="round"
                    strokeDasharray="158 176"
                    transform="rotate(-90 35 35)"
                  />
                  <text
                    x="35"
                    y="40"
                    textAnchor="middle"
                    fontSize="16"
                    fontWeight="800"
                    fontFamily="Inter, sans-serif"
                    fill="var(--color-accent)"
                  >
                    87
                  </text>
                </svg>
                <span>ATS Score</span>
              </div>
              <div className="mockup-lines">
                <div className="mockup-line mockup-line--title" />
                <div className="mockup-line" style={{ width: "85%" }} />
                <div className="mockup-line" style={{ width: "70%" }} />
                <div className="mockup-line" style={{ width: "90%" }} />
                <div
                  className="mockup-line mockup-line--title"
                  style={{ marginTop: "12px" }}
                />
                <div className="mockup-line" />
                <div className="mockup-line" style={{ width: "75%" }} />
              </div>
            </div>
            <div className="mockup-card__keywords">
              {["Python", "React", "AWS", "API", "ML"].map((kw) => (
                <span key={kw} className="mockup-kw">
                  {kw}
                </span>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ====== HOW IT WORKS ====== */}
      <section
        className="how-it-works"
        id="how-it-works"
        aria-labelledby="how-title"
      >
        <div className="container">
          <div className="section-header">
            <p className="section-label">Process</p>
            <h2 className="section-title" id="how-title">
              Three Steps to Your
              <br />
              <span className="text-gradient">Perfect Resume</span>
            </h2>
            <p className="section-subtitle">
              Our AI-powered pipeline works in seconds, not hours.
            </p>
          </div>

          <div className="steps-grid">
            <StepCard
              number="01"
              title="Provide Your Information"
              description="Paste your existing resume and the job description you're targeting. Upload PDF, DOCX, or plain text — we handle them all."
              delay={0}
            />
            <StepCard
              number="02"
              title="AI Analyzes & Tailors"
              description="Our AI identifies missing keywords, restructures your experience with STAR format, and optimizes every section for ATS parsing."
              delay={0.1}
            />
            <StepCard
              number="03"
              title="Download & Apply"
              description="Get your ATS-optimized resume instantly. Download it and apply with confidence, knowing your resume is tailored for the role."
              delay={0.2}
            />
          </div>
        </div>
      </section>

      {/* ====== FEATURES ====== */}
      <section
        className="features"
        id="features"
        aria-labelledby="features-title"
      >
        <div className="container">
          <div className="section-header">
            <p className="section-label">Capabilities</p>
            <h2 className="section-title" id="features-title">
              Everything You Need to
              <br />
              <span className="text-gradient">Get Hired Faster</span>
            </h2>
          </div>

          <div className="features-grid">
            <FeatureCard
              icon="🎯"
              title="ATS Keyword Matching"
              description="Automatically identifies and inserts high-value keywords from the job description that ATS systems scan for."
              delay={0}
            />
            <FeatureCard
              icon="📊"
              title="Real-Time ATS Score"
              description="See your resume's ATS compatibility score before and after optimization, with a visual breakdown."
              delay={0.1}
            />
            <FeatureCard
              icon="✨"
              title="Smart Content Rewriting"
              description="AI rewrites bullet points using the STAR method and quantifies achievements to make them impactful."
              delay={0.2}
            />
            <FeatureCard
              icon="⚡"
              title="Lightning Fast"
              description="Get results in under 30 seconds. No sign-ups, no credit cards, no waiting — just results."
              delay={0.3}
            />
            <FeatureCard
              icon="📥"
              title="Instant Download"
              description="Download your optimized resume as a clean, formatted PDF ready to submit to employers."
              delay={0.4}
            />
            <FeatureCard
              icon="🔒"
              title="Privacy First"
              description="Your data is processed securely and never stored permanently. Your career data stays yours."
              delay={0.5}
            />
          </div>

          {/* ── Coming Soon ── */}
          <div className="coming-soon-section">
            <div className="coming-soon-header">
              <span className="coming-soon-badge">🚀 Roadmap</span>
              <h3 className="coming-soon-title">
                Exciting Features Coming Soon
              </h3>
              <p className="coming-soon-subtitle">
                We're working hard to bring you even more powerful tools.
                Stay tuned!
              </p>
            </div>

            <div className="coming-soon-grid">
              {[
                {
                  icon: "🔗",
                  title: "LinkedIn Profile Optimizer",
                  desc: "Tailor your LinkedIn summary, headline, and skills to match your target role and boost recruiter visibility.",
                  eta: "Q3 2025",
                },
                {
                  icon: "📝",
                  title: "Cover Letter Generator",
                  desc: "Generate a personalized, job-specific cover letter in seconds — perfectly aligned with your optimized resume.",
                  eta: "Q3 2025",
                },
                {
                  icon: "🎤",
                  title: "AI Mock Interview",
                  desc: "Practice role-specific interview questions with real-time AI feedback on your answers, tone, and confidence.",
                  eta: "Q4 2025",
                },
                {
                  icon: "📈",
                  title: "Job Market Insights",
                  desc: "See real-time salary ranges, in-demand skills, and hiring trends for your target role and location.",
                  eta: "Q4 2025",
                },
                {
                  icon: "🧠",
                  title: "Skills Gap Analysis",
                  desc: "Identify missing skills from your profile and get a personalized learning roadmap to close the gap fast.",
                  eta: "Q1 2026",
                },
                {
                  icon: "📬",
                  title: "Job Application Tracker",
                  desc: "Track every application, interview, and follow-up in one place — never lose track of an opportunity again.",
                  eta: "Q1 2026",
                },
              ].map((feature) => (
                <div className="coming-soon-card" key={feature.title}>
                  <div className="coming-soon-card__top">
                    <span className="coming-soon-card__icon">
                      {feature.icon}
                    </span>
                    <span className="coming-soon-card__eta">{feature.eta}</span>
                  </div>
                  <h4 className="coming-soon-card__title">{feature.title}</h4>
                  <p className="coming-soon-card__desc">{feature.desc}</p>
                  <div className="coming-soon-card__footer">
                    <span className="coming-soon-lock">🔒 Coming Soon</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="coming-soon-notify">
              <p>Want to be notified when these features launch?</p>
              <a
                href="https://www.instagram.com/shivamsrivastava.dev"
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn--outline"
              >
                Follow for Updates →
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* ====== TESTIMONIALS ====== */}
      <section className="testimonials" aria-labelledby="testimonials-title">
        <div className="container">
          <div className="section-header">
            <p className="section-label">Success Stories</p>
            <h2 className="section-title" id="testimonials-title">
              Trusted by Job Seekers
              <br />
              <span className="text-gradient">Worldwide</span>
            </h2>
          </div>

          <div className="testimonials-grid">
            <TestimonialCard
              quote="I went from zero callbacks to three interviews in one week. CareerCraft completely transformed my resume."
              author="Priya S."
              role="Software Engineer"
              score={91}
              delay={0}
            />
            <TestimonialCard
              quote="The ATS score feature showed me exactly what was missing. After optimizing, I landed a senior role at a FAANG company."
              author="Marcus L."
              role="Data Scientist"
              score={88}
              delay={0.1}
            />
            <TestimonialCard
              quote="As a recent graduate, I had no idea how ATS systems worked. This tool made me competitive against experienced candidates."
              author="Aisha K."
              role="Product Manager"
              score={85}
              delay={0.2}
            />
          </div>
        </div>
      </section>

      {/* ====== CTA BANNER ====== */}
      <section className="cta-banner" aria-label="Call to action">
        <div className="container">
          <div className="cta-banner__inner">
            <h2 className="cta-banner__title">Ready to Beat the ATS?</h2>
            <p className="cta-banner__subtitle">
              Join thousands of job seekers who have already optimized their
              resumes with CareerCraft.
            </p>
            <Link
              to="/analyze"
              className="btn btn--primary btn--xl"
              id="footer-cta-btn"
            >
              <svg
                width="22"
                height="22"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
              </svg>
              Optimize My Resume — Free
            </Link>
          </div>
        </div>
      </section>

      {/* ====== FOOTER ====== */}
      <footer className="landing-footer" role="contentinfo">
        <div className="container landing-footer__inner">
          <p className="landing-footer__brand">
            <span>Career</span>
            <span className="text-gradient">Craft</span>
          </p>
          <p className="landing-footer__copy">
            © {new Date().getFullYear()} CareerCraft. Built with ❤️{" "}
            <a
              href="https://www.instagram.com/shivamsrivastava.dev"
              target="_blank"
            >
              Shivam Srivastava
            </a>{" "}
            to help people land their dream jobs.
          </p>
        </div>
      </footer>
    </div>
  );
}
