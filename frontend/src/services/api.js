import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 120000,
})

// Attach Authorization header if JWT token is stored
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('careercraft_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

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

/**
 * Login user.
 */
export async function loginUser({ identifier, password }) {
  try {
    const { data } = await api.post('/api/auth/login', { identifier, password })
    return data
  } catch (err) {
    if (err.code === 'ECONNREFUSED' || err.code === 'ERR_NETWORK' || err.response?.status === 404) {
      console.info('[CareerCraft] Backend not detected – mocking successful login.')
      await sleep(1000)
      const mockEmail = identifier.includes('@') ? identifier : `${identifier}@example.com`
      const mockUser = {
        id: 'mock-user-123',
        full_name: 'Jane Doe',
        email: mockEmail,
        username: mockEmail.split('@')[0],
        mobile_number: '1234567890',
        created_at: new Date().toISOString()
      }
      return {
        access_token: 'mock-jwt-token-xyz',
        token_type: 'bearer',
        user: mockUser
      }
    }
    throw err
  }
}

/**
 * Register user.
 */
export async function registerUser({ full_name, email, mobile_number, password }) {
  try {
    const { data } = await api.post('/api/auth/register', { full_name, email, mobile_number, password })
    return data
  } catch (err) {
    if (err.code === 'ECONNREFUSED' || err.code === 'ERR_NETWORK' || err.response?.status === 404) {
      console.info('[CareerCraft] Backend not detected – mocking successful registration.')
      await sleep(1000)
      const mockEmail = email.toLowerCase().strip ? email.toLowerCase().trim() : email.toLowerCase()
      const mockUser = {
        id: 'mock-user-123',
        full_name,
        email: mockEmail,
        username: mockEmail.split('@')[0],
        mobile_number,
        created_at: new Date().toISOString()
      }
      return {
        access_token: 'mock-jwt-token-xyz',
        token_type: 'bearer',
        user: mockUser
      }
    }
    throw err
  }
}

/**
 * Get current user profile.
 */
export async function getProfile() {
  try {
    const { data } = await api.get('/api/auth/me')
    return data
  } catch (err) {
    if (err.code === 'ECONNREFUSED' || err.code === 'ERR_NETWORK' || err.response?.status === 404) {
      console.info('[CareerCraft] Backend not detected – mocking profile retrieval.')
      const mockToken = localStorage.getItem('careercraft_token')
      if (!mockToken) {
        throw new Error('Not authenticated')
      }
      return {
        id: 'mock-user-123',
        full_name: 'Jane Doe',
        email: 'jane.doe@example.com',
        username: 'jane.doe',
        mobile_number: '1234567890',
        created_at: new Date().toISOString()
      }
    }
    throw err
  }
}

/**
 * Get user's resume analysis history.
 */
export async function getUserHistory() {
  try {
    const { data } = await api.get('/api/auth/history')
    return data
  } catch (err) {
    if (err.code === 'ECONNREFUSED' || err.code === 'ERR_NETWORK' || err.response?.status === 404) {
      console.info('[CareerCraft] Backend not detected – mocking history retrieval.')
      await sleep(600)
      return [
        {
          analysis_id: 'mock-analysis-1',
          job_description_snippet: 'Senior Full Stack Software Engineer (React, Python, AWS)',
          ats_score: 91,
          matched_keywords_count: 12,
          total_keywords_count: 15,
          created_at: new Date(Date.now() - 3600000 * 24).toISOString() // 1 day ago
        },
        {
          analysis_id: 'mock-analysis-2',
          job_description_snippet: 'Frontend Developer (Tailwind CSS, React, TypeScript)',
          ats_score: 84,
          matched_keywords_count: 8,
          total_keywords_count: 11,
          created_at: new Date(Date.now() - 3600000 * 48).toISOString() // 2 days ago
        }
      ]
    }
    throw err
  }
}

/**
 * Download a saved resume analysis as PDF.
 */
export async function downloadSavedPDF(analysisId) {
  try {
    const response = await api.get(`/api/download/${analysisId}`, {
      responseType: 'blob',
    })
    return response.data
  } catch (err) {
    if (err.code === 'ECONNREFUSED' || err.code === 'ERR_NETWORK' || err.response?.status === 404) {
      console.info('[CareerCraft] Backend not detected – generating mock PDF download.')
      await sleep(1500)
      return new Blob(['Mock PDF Content for analysis: ' + analysisId], { type: 'application/pdf' })
    }
    throw err
  }
}

/**
 * Get detailed report of a saved resume analysis by ID.
 */
export async function getAnalysisDetails(analysisId) {
  try {
    const { data } = await api.get(`/api/analysis/${analysisId}`)
    return data
  } catch (err) {
    if (err.code === 'ECONNREFUSED' || err.code === 'ERR_NETWORK' || err.response?.status === 404) {
      console.info('[CareerCraft] Backend not detected – mocking analysis details.')
      await sleep(800)
      return {
        success: true,
        analysis_id: analysisId,
        generated_resume: MOCK_RESUME,
        ats_score: analysisId === 'mock-analysis-1' ? 91 : 84,
        matched_keywords: MOCK_KEYWORDS.slice(0, analysisId === 'mock-analysis-1' ? 12 : 8),
        total_keywords: analysisId === 'mock-analysis-1' ? 15 : 11,
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
