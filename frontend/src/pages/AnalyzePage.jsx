import { useState, useEffect } from "react";
import StepIndicator from "../components/StepIndicator";
import ResumeForm from "../components/ResumeForm";
import ResultPanel from "../components/ResultPanel";
import { ProcessingOverlay } from "../components/Loader";
import { useResumeAnalyzer } from "../hooks/useResumeAnalyzer";
import { useToast } from "../components/Toast";
import "./AnalyzePage.css";

export default function AnalyzePage() {
  const { analyze, reset, isLoading, isSuccess, isError, result, error } =
    useResumeAnalyzer();
  const { show } = useToast();
  const [processingStage, setProcessingStage] = useState(0);

  /* Cycle processing stage labels while loading */
  useEffect(() => {
    if (!isLoading) {
      setProcessingStage(0);
      return;
    }
    const stages = [0, 1, 2, 3];
    let idx = 0;
    const interval = setInterval(() => {
      idx = (idx + 1) % stages.length;
      setProcessingStage(stages[idx]);
    }, 1800);
    return () => clearInterval(interval);
  }, [isLoading]);

  /* Show toast on error */
  useEffect(() => {
    if (isError && error) {
      show({ message: error, type: "error", duration: 6000 });
    }
  }, [isError, error, show]);

  /* Show toast on success */
  useEffect(() => {
    if (isSuccess && result) {
      const msg = result.mock
        ? "Demo result generated! Connect the backend for real AI analysis."
        : `Resume optimized! ATS Score: ${result.ats_score}/100`;
      show({
        message: msg,
        type: result.mock ? "warning" : "success",
        duration: 5000,
      });
    }
  }, [isSuccess, result, show]);

  const currentStep = isSuccess ? 3 : isLoading ? 2 : 1;

  async function handleSubmit(formData) {
    await analyze(formData);
    if (!isError) {
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  }

  return (
    <div className="analyze-page">
      <div className="container">
        {/* ---- Page header ---- */}
        <div className="analyze-page__header">
          <span className="section-label">AI Resume Optimizer</span>
          <h1 className="analyze-page__title">
            Craft Your <span className="text-gradient">ATS-Winning</span> Resume
          </h1>
          <p className="analyze-page__subtitle">
            Paste your resume and job description below. Our AI will generate a
            tailored, ATS-optimized resume in seconds.
          </p>
        </div>

        {/* ---- Step indicator ---- */}
        <StepIndicator currentStep={currentStep} />

        {/* ---- Main content ---- */}
        {isLoading ? (
          <ProcessingOverlay stage={processingStage} />
        ) : isSuccess && result ? (
          <div className="analyze-page__result animate-fade-in-up">
            <ResultPanel result={result} onReset={reset} />
          </div>
        ) : (
          <div className="analyze-page__form-layout">
            {/* Left: Form */}
            <div className="analyze-page__form-col">
              <ResumeForm onSubmit={handleSubmit} isLoading={isLoading} />
            </div>

            {/* Right: Info panel */}
            <aside
              className="analyze-page__info-col"
              aria-label="Tips and information"
            >
              <div className="info-panel card card--no-hover">
                <h2 className="info-panel__title">
                  <svg
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    aria-hidden="true"
                  >
                    <circle cx="12" cy="12" r="10" />
                    <line x1="12" y1="8" x2="12" y2="12" />
                    <line x1="12" y1="16" x2="12.01" y2="16" />
                  </svg>
                  How It Works
                </h2>
                <ol className="info-panel__steps">
                  <li className="info-panel__step">
                    <span className="info-panel__step-num">1</span>
                    <div>
                      <strong>Provide your resume</strong>
                      <p>
                        Paste your current resume text or upload a PDF/DOCX file
                      </p>
                    </div>
                  </li>
                  <li className="info-panel__step">
                    <span className="info-panel__step-num">2</span>
                    <div>
                      <strong>Add the job description</strong>
                      <p>Paste the full job description from the employer</p>
                    </div>
                  </li>
                  <li className="info-panel__step">
                    <span className="info-panel__step-num">3</span>
                    <div>
                      <strong>Get your optimized resume</strong>
                      <p>
                        Download a tailored, ATS-ready resume with improved
                        keywords
                      </p>
                    </div>
                  </li>
                </ol>
              </div>

              <div className="info-panel card card--no-hover">
                <h2 className="info-panel__title">
                  <svg
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    aria-hidden="true"
                  >
                    <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
                    <polyline points="17 6 23 6 23 12" />
                  </svg>
                  What We Optimize
                </h2>
                <ul className="info-panel__list">
                  {[
                    "ATS keyword alignment",
                    "Professional summary rewrite",
                    "STAR-format bullet points",
                    "Quantified achievements",
                    "Skills section relevance",
                    "Section ordering & structure",
                  ].map((item) => (
                    <li key={item} className="info-panel__list-item">
                      <svg
                        width="14"
                        height="14"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="var(--color-accent)"
                        strokeWidth="2.5"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        aria-hidden="true"
                      >
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="info-panel info-panel--highlight card card--no-hover">
                <div
                  className="info-panel__ats-score"
                  aria-label="Average ATS score improvement"
                >
                  <span className="info-panel__big-number">87</span>
                  <div>
                    <strong>Average ATS Score</strong>
                    <p>achieved by our users</p>
                  </div>
                </div>
              </div>
            </aside>
          </div>
        )}
      </div>
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
