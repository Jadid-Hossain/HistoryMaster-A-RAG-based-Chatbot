import { useState } from 'react'
import { login, register, storeSession } from '../api.js'

export default function Login({ onLogin }) {
  const [mode, setMode] = useState('login')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(event) {
    event.preventDefault()
    setError('')
    if (mode === 'register' && password !== confirm) {
      setError('Passwords do not match.')
      return
    }
    setBusy(true)
    try {
      const data =
        mode === 'login'
          ? await login(username.trim(), password)
          : await register(username.trim(), password)
      storeSession(data.access_token, { username: data.username, role: data.role })
      onLogin({ username: data.username, role: data.role })
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-logo">
          <span className="logo-emoji">🤖</span>
          <h1>KnowBot</h1>
          <p className="tagline">RAG-powered Knowledge Base Chatbot</p>
        </div>

        <div className="mode-tabs">
          <button
            className={mode === 'login' ? 'tab active' : 'tab'}
            onClick={() => { setMode('login'); setError('') }}
          >
            Sign In
          </button>
          <button
            className={mode === 'register' ? 'tab active' : 'tab'}
            onClick={() => { setMode('register'); setError('') }}
          >
            Create Account
          </button>
        </div>

        <form onSubmit={submit} className="login-form">
          <label>
            Username
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="your.username"
              autoComplete="username"
              required
              minLength={3}
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              required
              minLength={6}
            />
          </label>
          {mode === 'register' && (
            <label>
              Confirm Password
              <input
                type="password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                placeholder="••••••••"
                autoComplete="new-password"
                required
                minLength={6}
              />
            </label>
          )}

          {error && <div className="form-error">⚠ {error}</div>}

          <button className="btn primary full" disabled={busy}>
            {busy ? 'Please wait…' : mode === 'login' ? 'Sign In' : 'Create Account & Sign In'}
          </button>
        </form>

        {mode === 'login' && (
          <div className="demo-hint">
            <strong>Demo accounts</strong>
            <span>👤 user / user123 &nbsp;·&nbsp; 🛡 admin / admin123</span>
          </div>
        )}
      </div>
      <p className="login-footer">Retrieval-Augmented Generation · Chroma Vector DB · Gemini LLM</p>
    </div>
  )
}
