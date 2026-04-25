import { useState } from 'react'
import './App.css'

function App() {
  const [url, setUrl] = useState('')
  const [service, setService] = useState('')
  const [city, setCity] = useState('')
  const [userEmail, setUserEmail] = useState('')
  const [activeTab, setActiveTab] = useState('website') // 'website', 'youtube', or 'services'
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
    let payload = {}

    if (activeTab === 'website') {
      endpoint = 'summarize-website'
      payload = { url, email: 'user@example.com' }
    } else if (activeTab === 'youtube') {
      endpoint = 'summarize-youtube'
      payload = { url, email: 'user@example.com' }
    } else {
      endpoint = 'find-services'
      // Only send email if it's a valid non-empty string
      payload = { 
        service, 
        city, 
        email: userEmail.trim() === '' ? null : userEmail 
      }
    }

    try {
      const response = await fetch(`${apiUrl}/${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      const result = await response.json()

      if (response.ok) {
        setReportData(result.data)
        setStatus({
          type: 'success',
          message: activeTab === 'services' ? 'Services found and analyzed!' : 'Summary generated successfully!',
        })
      } else {
        // Handle cases where detail might be an object/array (FastAPI validation errors)
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
          className={`tab-btn ${activeTab === 'services' ? 'active' : ''}`}
          onClick={() => { setActiveTab('services'); setReportData(null); setStatus(null); }}
        >
          📍 Services
        </button>
      </div>

      <form onSubmit={handleSubmit}>
        {activeTab !== 'services' ? (
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
            <div className="input-group">
              <label htmlFor="email">Your Email (optional)</label>
              <input
                id="email"
                type="email"
                placeholder="your@email.com"
                value={userEmail}
                onChange={(e) => setUserEmail(e.target.value)}
              />
            </div>
          </>
        )}

        <button type="submit" className="submit-btn" disabled={loading}>
          {loading ? (
            <>
              <div className="loader"></div>
              {activeTab === 'website' ? 'Analyzing Content...' : activeTab === 'youtube' ? 'Transcribing Video...' : 'Searching Services...'}
            </>
          ) : (
            activeTab === 'website' ? 'Summarize Website' : activeTab === 'youtube' ? 'Summarize Video' : 'Find Best Services'
          )}
        </button>
      </form>

      {status && status.type === 'error' && (
        <div className={`status-message ${status.type}`}>
          {status.message}
        </div>
      )}

      {reportData && activeTab !== 'services' && (
        <div className="report-view">
          <div className="report-header">
            <h2>{reportData.title}</h2>
          </div>
          
          <div className="report-section">
            <h3>{activeTab === 'website' ? 'Summary' : 'Video Summary'}</h3>
            <p>{reportData.summary}</p>
          </div>

          <div className="report-grid">
            <div className="report-card">
              <h3>Key Insights</h3>
              <ul>
                {reportData.insights.map((item, i) => <li key={i}>{item}</li>)}
              </ul>
            </div>
            
            <div className="report-card">
              <h3>Use Cases</h3>
              <ul>
                {reportData.use_cases.map((item, i) => <li key={i}>{item}</li>)}
              </ul>
            </div>
          </div>

          <div className="report-footer">
            <div className="tags">
              {reportData.keywords.map((tag, i) => <span key={i} className="tag">#{tag}</span>)}
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
              <p><strong>Trust Score:</strong> {reportData.best_choice.trust_score}/100</p>
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
              {reportData.insights.map((insight, i) => <span key={i} className="tag insight-tag">{insight}</span>)}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
