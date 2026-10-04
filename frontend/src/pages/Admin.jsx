import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  fetchDocuments, uploadFiles, addUrl, deleteDocument, rebuildIndex, fetchStats, clearSession,
} from '../api.js'

const FORMAT_ICONS = { pdf: '📕', docx: '📘', txt: '📄', md: '📝', html: '🌐', url: '🌐' }

export default function Admin({ user, onLogout }) {
  const navigate = useNavigate()
  const [docs, setDocs] = useState([])
  const [stats, setStats] = useState(null)
  const [url, setUrl] = useState('')
  const [busy, setBusy] = useState(false)
  const [notice, setNotice] = useState(null)   // {kind: 'ok'|'err', text}
  const [uploadResults, setUploadResults] = useState(null)

  async function refresh() {
    try {
      setDocs(await fetchDocuments())
      setStats(await fetchStats())
    } catch (err) {
      setNotice({ kind: 'err', text: err.message })
    }
  }

  useEffect(() => { refresh() }, [])

  async function onFilesSelected(event) {
    const files = [...event.target.files]
    event.target.value = ''
    if (!files.length) return
    setBusy(true); setUploadResults(null); setNotice(null)
    try {
      const data = await uploadFiles(files)
      setUploadResults(data.results)
      await refresh()
    } catch (err) {
      setNotice({ kind: 'err', text: err.message })
      if (err.data?.detail?.results) setUploadResults(err.data.detail.results)
    } finally {
      setBusy(false)
    }
  }

  async function onAddUrl(event) {
    event.preventDefault()
    if (!url.trim()) return
    setBusy(true); setNotice(null); setUploadResults(null)
    try {
      const result = await addUrl(url.trim())
      setUploadResults([{ filename: result.filename, status: result.status, num_chunks: result.num_chunks, error: null }])
      setUrl('')
      await refresh()
    } catch (err) {
      setNotice({ kind: 'err', text: err.message })
    } finally {
      setBusy(false)
    }
  }

  async function onDelete(doc) {
    if (!window.confirm(`Delete "${doc.filename}" and its ${doc.num_chunks} vectors from the index?`)) return
    try {
      await deleteDocument(doc.id)
      setNotice({ kind: 'ok', text: `Deleted ${doc.filename}. The vector index shrinks instantly — no retraining.` })
      await refresh()
    } catch (err) {
      setNotice({ kind: 'err', text: err.message })
    }
  }

  async function onRebuild() {
    setBusy(true); setNotice(null)
    try {
      const result = await rebuildIndex()
      setNotice({ kind: 'ok', text: `Re-indexed ${result.chunks} chunks.` })
      await refresh()
    } catch (err) {
      setNotice({ kind: 'err', text: err.message })
    } finally {
      setBusy(false)
    }
  }

  function logout() {
    clearSession()
    onLogout()
  }

  return (
    <div className="admin-layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <span>🛡</span>
          <div><strong>Admin Panel</strong><small>Knowledge base control</small></div>
        </div>
        <button className="btn primary full" onClick={() => navigate('/chat')}>💬 Back to Chat</button>
        <div className="sidebar-footer">
          <div className="user-row">
            <span className="avatar">{user?.username?.[0]?.toUpperCase()}</span>
            <div className="user-meta"><strong>{user?.username}</strong><small>{user?.role}</small></div>
            <button className="btn ghost small-btn" onClick={logout}>Logout</button>
          </div>
        </div>
      </aside>

      <main className="admin-main">
        <header className="admin-header">
          <h1>Knowledge Base Management</h1>
          <p className="muted">Upload documents or web pages — new content is embedded instantly, no retraining needed.</p>
        </header>

        {stats && (
          <section className="stats-grid">
            <div className="stat-card"><span className="stat-num">{stats.documents}</span><span>Documents</span></div>
            <div className="stat-card"><span className="stat-num">{stats.chunks}</span><span>Vector chunks</span></div>
            <div className="stat-card"><span className="stat-num">{stats.users}</span><span>Users</span></div>
            <div className="stat-card"><span className="stat-num">{stats.chat_sessions}</span><span>Chat sessions</span></div>
            <div className="stat-card"><span className="stat-num">{stats.answers_generated}</span><span>Answers generated</span></div>
            <div className="stat-card"><span className="stat-num">{stats.llm_model || stats.llm_provider || '—'}</span><span>LLM</span></div>
          </section>
        )}

        <section className="panel">
          <h2>📥 Add knowledge</h2>
          <label className="dropzone">
            <input
              type="file"
              multiple
              accept=".pdf,.txt,.md,.docx,.html,.htm"
              onChange={onFilesSelected}
              disabled={busy}
            />
            <span className="dropzone-icon">📤</span>
            <strong>Click to choose files</strong>
            <span className="muted">PDF · TXT · MD · DOCX · HTML — up to 25 MB each</span>
          </label>

          <form className="url-row" onSubmit={onAddUrl}>
            <input
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/page — ingest a web page"
              disabled={busy}
            />
            <button className="btn primary" disabled={busy || !url.trim()}>Add URL</button>
          </form>

          {uploadResults && (
            <ul className="upload-results">
              {uploadResults.map((r, i) => (
                <li key={i} className={r.status === 'ready' ? 'ok' : 'err'}>
                  {r.status === 'ready'
                    ? `✅ ${r.filename} — ${r.num_chunks} chunks embedded`
                    : `❌ ${r.filename} — ${r.error}`}
                </li>
              ))}
            </ul>
          )}
          {notice && <div className={notice.kind === 'ok' ? 'notice ok' : 'notice err'}>{notice.text}</div>}
        </section>

        <section className="panel">
          <div className="panel-head">
            <h2>📚 Documents in the knowledge base</h2>
            <button className="btn ghost" onClick={onRebuild} disabled={busy}>🔄 Re-index all</button>
          </div>
          <table className="doc-table">
            <thead>
              <tr><th>File</th><th>Type</th><th>Chunks</th><th>Size</th><th>Uploaded by</th><th>Date</th><th></th></tr>
            </thead>
            <tbody>
              {docs.length === 0 && (
                <tr><td colSpan={7} className="muted">No documents yet — upload something above.</td></tr>
              )}
              {docs.map((d) => (
                <tr key={d.id}>
                  <td>{FORMAT_ICONS[d.doc_type] || '📄'} {d.filename}{d.status !== 'ready' && <em className="muted"> ({d.status})</em>}</td>
                  <td><span className="type-badge">{d.doc_type}</span></td>
                  <td>{d.num_chunks}</td>
                  <td>{d.size_bytes > 1024 ? `${(d.size_bytes / 1024).toFixed(1)} KB` : `${d.size_bytes} B`}</td>
                  <td>{d.uploaded_by}</td>
                  <td>{String(d.created_at).slice(0, 16)}</td>
                  <td><button className="btn danger small-btn" onClick={() => onDelete(d)}>Delete</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </main>
    </div>
  )
}
