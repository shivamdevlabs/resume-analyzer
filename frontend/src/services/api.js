import axios from 'axios'

const BASE_URL = ''

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 120000,
})

/* -------------------------------------------------------
   Mock data – used when the backend isn't running yet
   ------------------------------------------------------- */
const MOCK_RESUME = `John Doe
john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe | github.com/johndoe

PROFESSIONAL SUMMARY
─────────────────────────────────────────────────────────────────
Results-driven Full Stack Software Engineer with 5+ years of experience designing
and deploying scalable web applications. Proven expertise in Python, React.js, and
cloud-native architectures. Passionate about building products that solve real-world
problems, with a track record of improving system performance by 40%+ through
targeted optimization.

SKILLS
─────────────────────────────────────────────────────────────────
• Languages:    Python, JavaScript (ES2022+), TypeScript, SQL
• Frontend:     React.js, Next.js, Redux, CSS3, Tailwind CSS
• Backend:      FastAPI, Flask, Django, Node.js, REST APIs
• Databases:    PostgreSQL, MongoDB, Redis, Elasticsearch
• Cloud & DevOps: AWS (EC2, S3, Lambda), Docker, Kubernetes, CI/CD
• Tools:        Git, Jira, Figma, Postman, pytest

EXPERIENCE
─────────────────────────────────────────────────────────────────
Senior Software Engineer                             Mar 2022 – Present
TechCorp Solutions, San Francisco, CA

• Architected a microservices-based resume parsing system using Python/FastAPI,
  reducing processing time by 60% (from 5s → 2s) for 50,000+ daily requests.
• Led migration of monolithic React application to a micro-frontend architecture,
  improving time-to-interactive by 35% and enabling independent team deployments.
• Implemented ML-powered ATS keyword extraction using spaCy and BERT, achieving
  91% accuracy on job description matching benchmarks.
• Mentored 4 junior engineers, establishing code review practices that reduced
  production bug rate by 28%.

Software Engineer                                   Jan 2020 – Feb 2022
DataBridge Inc., Austin, TX

• Built real-time data pipeline using Apache Kafka and Python, processing 1M+
  events/day with sub-100ms latency.
• Developed RESTful APIs consumed by 3 internal teams and 2 external partners,
  documented via OpenAPI 3.0.
• Reduced AWS cloud costs by $18K/year through Lambda rightsizing and S3 lifecycle
  policies.

EDUCATION
─────────────────────────────────────────────────────────────────
B.S. Computer Science                               2019
University of Texas at Austin — GPA: 3.8 / 4.0

CERTIFICATIONS
• AWS Certified Solutions Architect – Associate (2023)
• Google Professional Cloud Developer (2022)

PROJECTS
─────────────────────────────────────────────────────────────────
ResuMatch (Open Source)  |  github.com/johndoe/resumatch
• AI-powered resume-to-job matching engine (800+ GitHub stars)
• Stack: Python, React, MongoDB, Docker
`

const MOCK_KEYWORDS = [
  'Python', 'React.js', 'FastAPI', 'MongoDB', 'REST APIs',
  'Machine Learning', 'Docker', 'Kubernetes', 'AWS', 'CI/CD',
  'TypeScript', 'PostgreSQL', 'Redis', 'Microservices'
]

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/* -------------------------------------------------------
   API Functions
   ------------------------------------------------------- */

/**
 * Analyzes resume against job description.
 * Falls back to mock data if backend is unavailable.
 */
export async function analyzeResume({ resumeText, jobDescription, resumeFile }) {
  try {
    const formData = new FormData()
    formData.append('job_description', jobDescription)

    if (resumeFile) {
      formData.append('resume_file', resumeFile)
    } else {
      formData.append('resume_text', resumeText)
    }

    const { data } = await api.post('/api/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  } catch (err) {
    // If the backend is not yet running, return beautiful mock data
    if (err.code === 'ECONNREFUSED' || err.code === 'ERR_NETWORK' || err.response?.status === 404) {
      console.info('[CareerCraft] Backend not detected – using mock response for preview.')
      await sleep(3200) // Simulate processing time
      return {
        success: true,
        generated_resume: MOCK_RESUME,
        ats_score: 87,
        matched_keywords: MOCK_KEYWORDS,
        total_keywords: 18,
        improvements: [
          'Added quantifiable achievements with metrics',
          'Aligned skills section with job description keywords',
          'Optimized professional summary for ATS parsing',
          'Restructured experience bullets using STAR format',
          'Added relevant certifications section',
        ],
        mock: true,
      }
    }
    throw err
  }
}

/**
 * Download generated resume as PDF.
 */
export async function downloadResumePDF(resumeText) {
  const response = await api.post(`/api/download`, { resume_text: resumeText }, {
    responseType: 'blob',
  })
  return response.data
}

/**
 * Health check endpoint.
 */
export async function healthCheck() {
  try {
    const { data } = await api.get('/api/health')
    return { online: true, ...data }
  } catch {
    return { online: false }
  }
}
