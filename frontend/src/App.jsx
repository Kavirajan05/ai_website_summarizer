import { useState } from 'react'
import './App.css'

function App() {
  const [url, setUrl] = useState('')
  const [topic, setTopic] = useState('')
  const [service, setService] = useState('')
  const [city, setCity] = useState('')
  const [userEmail, setUserEmail] = useState('')
  const [docFile, setDocFile] = useState(null)
  const [resumeFile, setResumeFile] = useState(null)
  const [query, setQuery] = useState('')
  const [linkedinUrl, setLinkedinUrl] = useState('')
  const [manualMode, setManualMode] = useState(false)
  const [profileText, setProfileText] = useState('')
  const [adTitle, setAdTitle] = useState('')
  const [adDescription, setAdDescription] = useState('')
  const [adImage, setAdImage] = useState(null)
  const [activeTab, setActiveTab] = useState('website') // 'website', 'youtube', 'document', 'yt-report', 'services', 'resume', 'multimodel', 'linkedin', or 'ad-generator'
  const [loading, setLoading] = useState(false)
  const [reportData, setReportData] = useState(null)
  const [status, setStatus] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setStatus(null)
    setReportData(null)

    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5001'
    let endpoint = ''
    let body = null
    let headers = {}

    if (activeTab === 'website') {
      endpoint = 'summarize-website'
      headers = { 'Content-Type': 'application/json' }
      body = JSON.stringify({ url, email: userEmail.trim() || 'user@example.com' })
    } else if (activeTab === 'youtube') {
      endpoint = 'summarize-youtube'
      headers = { 'Content-Type': 'application/json' }
      body = JSON.stringify({ url, email: userEmail.trim() || 'user@example.com' })
    } else if (activeTab === 'services') {
      endpoint = 'find-services'
      headers = { 'Content-Type': 'application/json' }
      body = JSON.stringify({ 
        service, 
        city, 
        email: userEmail.trim() === '' ? null : userEmail 
      })
    } else if (activeTab === 'document') {
      endpoint = 'summarize-document'
      const formData = new FormData()
      formData.append('file', docFile)
      body = formData
    } else if (activeTab === 'yt-report') {
      endpoint = 'youtube-report'
      headers = { 'Content-Type': 'application/json' }
      body = JSON.stringify({ topic })
    } else if (activeTab === 'resume') {
      endpoint = 'analyze-resume'
      const formData = new FormData()
      formData.append('file', resumeFile)
      body = formData
    } else if (activeTab === 'multimodel') {
      endpoint = 'multimodel-summarize'
      headers = { 'Content-Type': 'application/json' }
      body = JSON.stringify({ query })
    } else if (activeTab === 'linkedin') {
      endpoint = 'analyze-linkedin'
      headers = { 'Content-Type': 'application/json' }
      body = JSON.stringify({ 
        url: manualMode ? "" : linkedinUrl,
        profile_text: manualMode ? profileText : ""
      })
    } else if (activeTab === 'ad-generator') {
      endpoint = 'generate-ad'
      const formData = new FormData()
      formData.append('title', adTitle)
      formData.append('description', adDescription)
      formData.append('image', adImage)
      body = formData
    }

    try {
      const response = await fetch(`${apiUrl}/${endpoint}`, {
        method: 'POST',
        headers: headers,
        body: body,
      })

      const result = await response.json()

      if (response.ok) {
        setReportData(result.data)
        setStatus({
          type: 'success',
          message: activeTab === 'services' ? 'Services found and analyzed!' : 
                   activeTab === 'document' ? 'Document summarized successfully!' : 
                   activeTab === 'yt-report' ? 'YouTube report generated!' : 
                   activeTab === 'resume' ? 'Resume analyzed successfully!' : 
                   activeTab === 'multimodel' ? 'Multi-model summary generated!' : 
                   activeTab === 'linkedin' ? 'LinkedIn profile analyzed!' : 
                   activeTab === 'ad-generator' ? 'Marketing ad generated!' : 'Summary generated successfully!',
        })
      } else {
        const errorMessage = result.detail 
          ? (typeof result.detail === 'string' ? result.detail : JSON.stringify(result.detail))
          : 'Something went wrong';
        throw new Error(errorMessage)
      }
    } catch (err) {
      setStatus({
        type: 'error',
        message: err.message,
      })
    } finally {
      setLoading(false)
    }
  }

  const getHeaderText = () => {
    if (activeTab === 'website') return 'Instant expert summaries from any URL.'
    if (activeTab === 'youtube') return 'Instant expert summaries from any YouTube Video.'
    if (activeTab === 'document') return 'Instant expert summaries from any PDF Document.'
    if (activeTab === 'yt-report') return 'Generate learning reports from YouTube topics.'
    if (activeTab === 'resume') return 'AI-powered ATS scoring and resume analysis.'
    if (activeTab === 'multimodel') return 'Query multiple LLMs (Qwen, LLaMA, Gemini) simultaneously.'
    if (activeTab === 'linkedin') return 'Analyze LinkedIn profiles to get tailored improvement suggestions.'
    if (activeTab === 'ad-generator') return 'Generate professional marketing ads from product images.'
    return 'Find and analyze the best local service providers.'
  }

  return (
    <div className="app-container">
      <div className="header">
        <h1>AI Automation Hub</h1>
        <p>{getHeaderText()}</p>
      </div>

      <div className="tabs">
        <button 
          className={`tab-btn ${activeTab === 'website' ? 'active' : ''}`}
          onClick={() => { setActiveTab('website'); setReportData(null); setStatus(null); }}
        >
          🌐 Website
        </button>
        <button 
          className={`tab-btn ${activeTab === 'youtube' ? 'active' : ''}`}
          onClick={() => { setActiveTab('youtube'); setReportData(null); setStatus(null); }}
        >
          🎬 YouTube
        </button>
        <button 
          className={`tab-btn ${activeTab === 'document' ? 'active' : ''}`}
          onClick={() => { setActiveTab('document'); setReportData(null); setStatus(null); }}
        >
          📄 Document
        </button>
        <button 
          className={`tab-btn ${activeTab === 'yt-report' ? 'active' : ''}`}
          onClick={() => { setActiveTab('yt-report'); setReportData(null); setStatus(null); }}
        >
          🎥 YT Report
        </button>
        <button 
          className={`tab-btn ${activeTab === 'services' ? 'active' : ''}`}
          onClick={() => { setActiveTab('services'); setReportData(null); setStatus(null); }}
        >
          📍 Services
        </button>
        <button 
          className={`tab-btn ${activeTab === 'resume' ? 'active' : ''}`}
          onClick={() => { setActiveTab('resume'); setReportData(null); setStatus(null); }}
        >
          💼 Resume
        </button>
        <button 
          className={`tab-btn ${activeTab === 'multimodel' ? 'active' : ''}`}
          onClick={() => { setActiveTab('multimodel'); setReportData(null); setStatus(null); }}
        >
          🤖 Multi-Model
        </button>
        <button 
          className={`tab-btn ${activeTab === 'linkedin' ? 'active' : ''}`}
          onClick={() => { setActiveTab('linkedin'); setReportData(null); setStatus(null); }}
        >
          🔗 LinkedIn
        </button>
        <button 
          className={`tab-btn ${activeTab === 'ad-generator' ? 'active' : ''}`}
          onClick={() => { setActiveTab('ad-generator'); setReportData(null); setStatus(null); }}
        >
          🎨 Ad Generator
        </button>
      </div>

      <form onSubmit={handleSubmit}>
        {activeTab === 'website' || activeTab === 'youtube' ? (
          <div className="input-group">
            <label htmlFor="url">
              {activeTab === 'website' ? 'Website URL' : 'YouTube Video URL'}
            </label>
            <input
              id="url"
              type="url"
              placeholder={activeTab === 'website' ? "https://example.com" : "https://youtube.com/watch?v=..."}
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              required
            />
          </div>
        ) : activeTab === 'document' ? (
          <div className="input-group">
            <label htmlFor="file">Upload PDF Document</label>
            <div className="file-upload-wrapper">
              <input
                id="file"
                type="file"
                accept=".pdf,application/pdf"
                onChange={(e) => setDocFile(e.target.files[0])}
                required
              />
            </div>
          </div>
        ) : activeTab === 'yt-report' ? (
          <div className="input-group">
            <label htmlFor="topic">Learning Topic</label>
            <input
              id="topic"
              type="text"
              placeholder="e.g. Quantum Physics, React Hooks"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              required
            />
          </div>
        ) : activeTab === 'resume' ? (
          <div className="input-group">
            <label htmlFor="resumeFile">Upload Resume (PDF/DOCX)</label>
            <div className="file-upload-wrapper">
              <input
                id="resumeFile"
                type="file"
                accept=".pdf,application/pdf,.docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                onChange={(e) => setResumeFile(e.target.files[0])}
                required
              />
            </div>
          </div>
        ) : activeTab === 'multimodel' ? (
          <div className="input-group">
            <label htmlFor="query">Ask Multiple AIs</label>
            <textarea
              id="query"
              placeholder="e.g. Compare React and Vue, or explain quantum physics..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              required
              rows={4}
              style={{ width: '100%', background: 'rgba(0, 0, 0, 0.2)', border: '1px solid var(--glass-border)', borderRadius: '12px', padding: '0.8rem 1rem', color: 'white', fontSize: '1rem', outline: 'none', resize: 'vertical' }}
            />
          </div>
        ) : activeTab === 'linkedin' ? (
          <div className="linkedin-container">
            <div className="input-group">
              <label htmlFor="profileText">Paste LinkedIn Profile Text Here</label>
              <p className="input-hint">Copy the 'About' and 'Experience' sections from LinkedIn and paste them below for a deep AI analysis.</p>
              <textarea
                id="profileText"
                placeholder="Paste profile content here..."
                value={profileText}
                onChange={(e) => setProfileText(e.target.value)}
                rows={12}
                required
              />
            </div>
          </div>
        ) : activeTab === 'ad-generator' ? (
          <>
            <div className="input-group">
              <label htmlFor="adTitle">Product Title</label>
              <input
                id="adTitle"
                type="text"
                placeholder="e.g. Premium Leather Watch"
                value={adTitle}
                onChange={(e) => setAdTitle(e.target.value)}
                required
              />
            </div>
            <div className="input-group">
              <label htmlFor="adDescription">Marketing Description</label>
              <textarea
                id="adDescription"
                placeholder="e.g. Handcrafted from top-grain Italian leather with a sapphire glass face..."
                value={adDescription}
                onChange={(e) => setAdDescription(e.target.value)}
                required
                rows={3}
                style={{ width: '100%', background: 'rgba(0, 0, 0, 0.2)', border: '1px solid var(--glass-border)', borderRadius: '12px', padding: '0.8rem 1rem', color: 'white', fontSize: '1rem', outline: 'none', resize: 'vertical' }}
              />
            </div>
            <div className="input-group">
              <label htmlFor="adImage">Product Photo</label>
              <div className="file-upload-wrapper">
                <input
                  id="adImage"
                  type="file"
                  accept="image/*"
                  onChange={(e) => setAdImage(e.target.files[0])}
                  required
                />
              </div>
            </div>
          </>
        ) : (
          <>
            <div className="input-group">
              <label htmlFor="service">Service Type</label>
              <input
                id="service"
                type="text"
                placeholder="e.g. Plumber, Dentist, Gym"
                value={service}
                onChange={(e) => setService(e.target.value)}
                required
              />
            </div>
            <div className="input-group">
              <label htmlFor="city">City / Location</label>
              <input
                id="city"
                type="text"
                placeholder="e.g. New York, London"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                required
              />
            </div>
          </>
        )}

        {activeTab !== 'document' && activeTab !== 'yt-report' && activeTab !== 'resume' && activeTab !== 'multimodel' && activeTab !== 'linkedin' && activeTab !== 'ad-generator' && (
          <div className="input-group">
            <label htmlFor="email">Your Email {activeTab === 'services' ? '(optional)' : '(for results)'}</label>
            <input
              id="email"
              type="email"
              placeholder="your@email.com"
              value={userEmail}
              onChange={(e) => setUserEmail(e.target.value)}
              required={activeTab !== 'services'}
            />
          </div>
        )}

        <button type="submit" className="submit-btn" disabled={loading}>
          {loading ? (
            <>
              <div className="loader"></div>
              {activeTab === 'website' ? 'Analyzing Content...' : 
               activeTab === 'youtube' ? 'Transcribing Video...' : 
               activeTab === 'document' ? 'Processing PDF...' : 
               activeTab === 'yt-report' ? 'Generating Report...' : 
               activeTab === 'resume' ? 'Analyzing Resume...' : 
               activeTab === 'multimodel' ? 'Querying Models...' : 
               activeTab === 'linkedin' ? 'Analyzing Profile...' : 
               activeTab === 'ad-generator' ? 'Generating Ad...' : 'Searching Services...'}
            </>
          ) : (
            activeTab === 'website' ? 'Summarize Website' : 
            activeTab === 'youtube' ? 'Summarize Video' : 
            activeTab === 'document' ? 'Summarize Document' : 
            activeTab === 'yt-report' ? 'Generate YT Report' : 
            activeTab === 'resume' ? 'Analyze Resume' : 
            activeTab === 'multimodel' ? 'Ask Multimodel AI' : 
            activeTab === 'linkedin' ? 'Analyze Profile' : 
            activeTab === 'ad-generator' ? 'Generate Marketing Ad' : 'Find Best Services'
          )}
        </button>
      </form>

      {status && status.type === 'error' && (
        <div className={`status-message ${status.type}`}>
          {status.message}
        </div>
      )}

      {reportData && activeTab === 'yt-report' && (
        <div className="report-view">
          <div className="report-header">
            <h2>AI Learning Report: {reportData.topic}</h2>
          </div>
          
          <div className="report-section">
            <h3>Ranked Recommendations</h3>
            <div className="recommendations-list">
              {reportData.ai_analysis.map((item, i) => (
                <div key={i} className="rec-item">
                  <div className="rec-main">
                    <h4>#{item.rank} {item.title}</h4>
                    <span className="tag">{item.channel}</span>
                  </div>
                  <p className="reasoning">{item.explanation}</p>
                  <div className="rec-links">
                    <a href={item.url} target="_blank" rel="noreferrer">🎬 Watch Video</a>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="report-section">
            <h3>Final Report Preview</h3>
            <pre className="report-preview-text">{reportData.final_report}</pre>
          </div>
        </div>
      )}

      {reportData && activeTab !== 'services' && activeTab !== 'yt-report' && activeTab !== 'resume' && activeTab !== 'multimodel' && activeTab !== 'linkedin' && activeTab !== 'ad-generator' && (
        <div className="report-view">
          <div className="report-header">
            <h2>{reportData.title}</h2>
          </div>
          
          <div className="report-section">
            <h3>{activeTab === 'website' ? 'Summary' : activeTab === 'youtube' ? 'Video Summary' : 'Document Summary'}</h3>
            <p>{reportData.summary}</p>
          </div>

          <div className="report-grid">
            <div className="report-card">
              <h3>Key Insights</h3>
              <ul>
                {reportData.insights && reportData.insights.map((item, i) => <li key={i}>{item}</li>)}
              </ul>
            </div>
            
            {reportData.use_cases && (
              <div className="report-card">
                <h3>Use Cases</h3>
                <ul>
                  {reportData.use_cases.map((item, i) => <li key={i}>{item}</li>)}
                </ul>
              </div>
            )}

            {!reportData.use_cases && reportData.keywords && (
              <div className="report-card">
                <h3>Main Keywords</h3>
                <ul>
                  {reportData.keywords.map((item, i) => <li key={i}>{item}</li>)}
                </ul>
              </div>
            )}
          </div>

          <div className="report-footer">
            <div className="tags">
              {reportData.keywords && reportData.keywords.map((tag, i) => <span key={i} className="tag">#{tag}</span>)}
            </div>
          </div>
        </div>
      )}

      {reportData && activeTab === 'services' && (
        <div className="report-view">
          <div className="report-header">
            <h2>Top {reportData.service} in {reportData.city}</h2>
          </div>

          {reportData.best_choice && reportData.best_choice.name && (
            <div className="report-section highlight">
              <h3>🏆 Best Choice: {reportData.best_choice.name}</h3>
              <p>{reportData.best_choice.reasoning}</p>
            </div>
          )}
          
          <div className="report-section">
            <h3>Market Overview</h3>
            <p>{reportData.summary}</p>
          </div>

          <div className="report-grid">
            <div className="report-card full-width">
              <h3>Top Recommendations</h3>
              <div className="recommendations-list">
                {reportData.top_recommendations.map((rec, i) => (
                  <div key={i} className="rec-item">
                    <div className="rec-main">
                      <h4>{rec.name}</h4>
                      <span className="rating">⭐ {rec.rating} ({rec.reviews_count} reviews)</span>
                    </div>
                    <p className="reasoning">{rec.reasoning}</p>
                    <div className="rec-links">
                      {rec.phone !== 'N/A' && <span>📞 {rec.phone}</span>}
                      {rec.website !== 'N/A' && <a href={rec.website} target="_blank" rel="noreferrer">🌐 Website</a>}
                      <a href={`https://www.google.com/maps/search/?api=1&query=${rec.name.replace(/ /g, '+')}`} target="_blank" rel="noreferrer">📍 Maps</a>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="report-footer">
            <h3>Key Insights</h3>
            <div className="tags">
              {reportData.insights && reportData.insights.map((insight, i) => <span key={i} className="tag insight-tag">{insight}</span>)}
            </div>
          </div>
        </div>
      )}

      {reportData && activeTab === 'resume' && (
        <div className="report-view">
          <div className="report-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
            <h2 style={{ marginBottom: 0 }}>Resume Analysis: {reportData.name}</h2>
            <div className="ats-score-badge">
              <span className="score-label">ATS Score</span>
              <span className={`score-value ${reportData.ats_score >= 80 ? 'high' : reportData.ats_score >= 60 ? 'medium' : 'low'}`}>
                {reportData.ats_score}/100
              </span>
            </div>
          </div>
          
          <div className="report-section highlight">
            <h3>Candidate Summary</h3>
            <p><strong>Email:</strong> {reportData.email}</p>
            <p><strong>Education:</strong> {reportData.education}</p>
            <p><strong>Experience:</strong> {reportData.experience}</p>
          </div>

          <div className="report-grid">
            <div className="report-card">
              <h3>Verified Skills</h3>
              <div className="tags">
                {reportData.skills && reportData.skills.map((skill, i) => (
                  <span key={i} className="tag">{skill}</span>
                ))}
              </div>
            </div>
            
            <div className="report-card">
              <h3>Missing Keywords (ATS)</h3>
              <div className="tags">
                {reportData.missing_skills && reportData.missing_skills.map((skill, i) => (
                  <span key={i} className="tag error-tag">{skill}</span>
                ))}
              </div>
            </div>
          </div>

          <div className="report-section">
            <h3>Improvement Suggestions</h3>
            <ul className="suggestions-list">
              {reportData.suggestions && reportData.suggestions.map((suggestion, i) => (
                <li key={i}>{suggestion}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {reportData && activeTab === 'multimodel' && reportData.final_summary && (
        <div className="report-view">
          <div className="report-header">
            <h2>{reportData.final_summary.title}</h2>
          </div>
          
          <div className="report-section highlight">
            <h3>Overview</h3>
            <p>{reportData.final_summary.overview}</p>
          </div>

          <div className="report-grid">
            <div className="report-card">
              <h3>Key Points</h3>
              <ul className="suggestions-list">
                {reportData.final_summary.key_points && reportData.final_summary.key_points.map((point, i) => (
                  <li key={i}>{point}</li>
                ))}
              </ul>
            </div>
            
            <div className="report-card">
              <h3>Model Latency</h3>
              <ul className="suggestions-list">
                <li><strong>Qwen:</strong> {reportData.meta?.latency?.openrouter_qwen || 'N/A'}</li>
                <li><strong>LLaMA:</strong> {reportData.meta?.latency?.groq_llama || 'N/A'}</li>
                <li><strong>Gemini:</strong> {reportData.meta?.latency?.gemini || 'N/A'}</li>
                <li><strong>Total Time:</strong> {reportData.meta?.latency?.total || 'N/A'}</li>
              </ul>
            </div>
          </div>

          <div className="report-grid">
             <div className="report-card">
              <h3>Strengths</h3>
              <ul className="suggestions-list">
                {reportData.final_summary.strengths && reportData.final_summary.strengths.map((s, i) => <li key={i}>{s}</li>)}
              </ul>
             </div>
             <div className="report-card">
              <h3>Challenges / Weaknesses</h3>
              <ul className="suggestions-list">
                {reportData.final_summary.challenges && reportData.final_summary.challenges.map((c, i) => <li key={i}>{c}</li>)}
              </ul>
             </div>
          </div>

          <div className="report-section">
            <h3>Conclusion</h3>
            <p>{reportData.final_summary.conclusion}</p>
          </div>
        </div>
      )}

      {reportData && activeTab === 'linkedin' && (
        <div className="report-view">
          <div className="report-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
            <h2 style={{ marginBottom: 0 }}>LinkedIn Profile Analysis</h2>
            <div className="ats-score-badge">
              <span className="score-label">Profile Score</span>
              <span className={`score-value ${reportData.score >= 80 ? 'high' : reportData.score >= 60 ? 'medium' : 'low'}`}>
                {reportData.score}/100
              </span>
            </div>
          </div>
          
          <div className="report-section highlight">
            <h3>Improved Headline</h3>
            <p><strong>{reportData.improved_headline}</strong></p>
          </div>

          <div className="report-section">
            <h3>Improved About Section</h3>
            <p style={{ whiteSpace: 'pre-wrap' }}>{reportData.improved_about}</p>
          </div>

          <div className="report-grid">
            <div className="report-card">
              <h3>Verified Strengths</h3>
              <div className="tags">
                {reportData.strengths && reportData.strengths.map((strength, i) => (
                  <span key={i} className="tag">{strength}</span>
                ))}
              </div>
            </div>
            
            <div className="report-card">
              <h3>Weaknesses</h3>
              <div className="tags">
                {reportData.weaknesses && reportData.weaknesses.map((weakness, i) => (
                  <span key={i} className="tag error-tag">{weakness}</span>
                ))}
              </div>
            </div>
          </div>

          <div className="report-section">
            <h3>Actionable Suggestions</h3>
            <ul className="suggestions-list">
              {reportData.suggestions && reportData.suggestions.map((suggestion, i) => (
                <li key={i}>{suggestion}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {reportData && activeTab === 'ad-generator' && (
        <div className="report-view">
          <div className="report-header">
            <h2>Marketing Ad: {reportData.title}</h2>
          </div>
          
          <div className="report-section highlight" style={{ textAlign: 'center' }}>
            <h3>Generated Image</h3>
            <div className="ad-image-container" style={{ margin: '1.5rem auto', maxWidth: '600px', borderRadius: '16px', overflow: 'hidden', boxShadow: '0 20px 40px rgba(0,0,0,0.4)' }}>
              <img src={reportData.image} alt={reportData.title} style={{ width: '100%', height: 'auto', display: 'block' }} />
            </div>
            <p className="reasoning">This image was professionally enhanced for marketing purposes using AI photography techniques.</p>
          </div>

          <div className="report-footer" style={{ display: 'flex', justifyContent: 'center' }}>
            <a href={reportData.image} download={`${reportData.title.replace(/ /g, '_')}_ad.png`} className="submit-btn" style={{ textDecoration: 'none', width: 'auto', padding: '0.8rem 2rem' }}>
              📥 Download Ad Image
            </a>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
