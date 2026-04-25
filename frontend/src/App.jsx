import { useState } from 'react'
import './App.css'

function App() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [reportData, setReportData] = useState(null)
  const [status, setStatus] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setStatus(null)
    setReportData(null)

    let apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5001'
    
    // Safety Fix: Remove trailing slash if present
    apiUrl = apiUrl.replace(/\/$/, '')

    try {
      const response = await fetch(`${apiUrl}/summarize-website`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url, email: 'user@example.com' }),
      })

      const result = await response.json()

      if (response.ok) {
        setReportData(result.data)
        setStatus({
          type: 'success',
          message: 'Summary generated successfully!',
        })
      } else {
        throw new Error(result.detail || 'Something went wrong')
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

  return (
    <div className="app-container">
      <div className="header">
        <h1>AI Summarizer</h1>
        <p>Instant expert summaries from any URL.</p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <label htmlFor="url">Website URL</label>
          <input
            id="url"
            type="url"
            placeholder="https://example.com"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            required
          />
        </div>

        <button type="submit" className="submit-btn" disabled={loading}>
          {loading ? (
            <>
              <div className="loader"></div>
              Analyzing Content...
            </>
          ) : (
            'Generate Summary'
          )}
        </button>
      </form>

      {status && status.type === 'error' && (
        <div className={`status-message ${status.type}`}>
          {status.message}
        </div>
      )}

      {reportData && (
        <div className="report-view">
          <div className="report-header">
            <h2>{reportData.title}</h2>
          </div>
          
          <div className="report-section">
            <h3>Summary</h3>
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
    </div>
  )
}

export default App
