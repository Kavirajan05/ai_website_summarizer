import { useState } from 'react'
import './App.css'

function App() {
  const [url, setUrl] = useState('')
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState(null) // { type: 'success' | 'error', message: string }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setStatus(null)

    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5001'

    try {
      const response = await fetch(`${apiUrl}/summarize-website`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url, email }),
      })

      const data = await response.json()

      if (response.ok) {
        setStatus({
          type: 'success',
          message: data.message || 'Summarization started! Check your email soon.',
        })
        setUrl('')
      } else {
        throw new Error(data.detail || 'Something went wrong')
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
        <p>Expert summaries delivered straight to your inbox.</p>
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

        <div className="input-group">
          <label htmlFor="email">Delivery Email</label>
          <input
            id="email"
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <button type="submit" className="submit-btn" disabled={loading}>
          {loading ? (
            <>
              <div className="loader"></div>
              Processing...
            </>
          ) : (
            'Generate Summary'
          )}
        </button>
      </form>

      {status && (
        <div className={`status-message ${status.type}`}>
          {status.message}
        </div>
      )}
    </div>
  )
}

export default App
