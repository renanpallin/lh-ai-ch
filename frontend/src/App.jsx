import { useState, useEffect } from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import DocumentList from './components/DocumentList'
import DocumentDetail from './components/DocumentDetail'
import UploadForm from './components/UploadForm'
import SearchBar from './components/SearchBar'
import { getTags } from './api'

function App() {
  const [refreshKey, setRefreshKey] = useState(0)
  const [selectedTag, setSelectedTag] = useState(null)
  const [allTags, setAllTags] = useState([])

  useEffect(() => {
    loadTags()
  }, [refreshKey])

  async function loadTags() {
    try {
      const data = await getTags()
      setAllTags(data)
    } catch (err) {
      console.error('Failed to load tags:', err)
    }
  }

  function handleUploadSuccess() {
    setRefreshKey(prev => prev + 1)
  }

  return (
    <div className="app">
      <header className="header">
        <Link to="/" className="logo">
          <h1>DocProc</h1>
        </Link>
        <nav className="header-nav">
          {allTags.length > 0 && (
            <select
              className="tag-filter-select"
              value={selectedTag || ''}
              onChange={(e) => setSelectedTag(e.target.value || null)}
            >
              <option value="">All tags</option>
              {allTags.map(tag => (
                <option key={tag} value={tag}>{tag}</option>
              ))}
            </select>
          )}
          <SearchBar selectedTag={selectedTag} />
        </nav>
      </header>
      <main className="main">
        <Routes>
          <Route path="/" element={
            <>
              <UploadForm onUploadSuccess={handleUploadSuccess} />
              <DocumentList
                refreshKey={refreshKey}
                selectedTag={selectedTag}
                onTagSelect={setSelectedTag}
              />
            </>
          } />
          <Route path="/documents/:id" element={<DocumentDetail />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
