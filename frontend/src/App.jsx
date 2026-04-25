import { useState } from 'react'
import './App.css'

function App() {
  const [url, setUrl] = useState('')
  const [topic, setTopic] = useState('')
  const [service, setService] = useState('')
  const [city, setCity] = useState('')
  const [userEmail, setUserEmail] = useState('')
  const [docFile, setDocFile] = useState(null)
  const [activeTab, setActiveTab] = useState('website') // 'website', 'youtube', 'document', 'yt-report', or 'services'
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
                   activeTab === 'yt-report' ? 'YouTube report generated!' : 'Summary generated successfully!',
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

        {activeTab !== 'document' && activeTab !== 'yt-report' && (
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
               activeTab === 'yt-report' ? 'Generating Report...' : 'Searching Services...'}
            </>
          ) : (
            activeTab === 'website' ? 'Summarize Website' : 
            activeTab === 'youtube' ? 'Summarize Video' : 
            activeTab === 'document' ? 'Summarize Document' : 
            activeTab === 'yt-report' ? 'Generate YT Report' : 'Find Best Services'
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

      {reportData && activeTab !== 'services' && activeTab !== 'yt-report' && (
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
    </div>
  )
}

export default App
