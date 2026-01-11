import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getDocuments } from '../api'

function DocumentList({ refreshKey, selectedTag, onTagSelect }) {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadDocuments()
  }, [refreshKey, selectedTag])

  async function loadDocuments() {
    try {
      setLoading(true)
      const data = await getDocuments(selectedTag)
      setDocuments(data)
    } catch (err) {
      setError('Failed to load documents')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading">Loading documents...</div>
  }

  if (error) {
    return <div className="error">{error}</div>
  }

  return (
    <div className="document-list">
      <div className="document-list-header">
        <h2>Documents</h2>
        {selectedTag && (
          <div className="active-filter-inline">
            Filtering by: <span className="tag">{selectedTag}</span>
            <button onClick={() => onTagSelect(null)} className="clear-filter">×</button>
          </div>
        )}
      </div>

      {documents.length === 0 ? (
        <div className="empty-state">
          {selectedTag
            ? `No documents with tag "${selectedTag}".`
            : 'No documents uploaded yet. Upload a PDF to get started.'
          }
        </div>
      ) : (
        documents.map(doc => (
          <div key={doc.id} className="document-item">
            <div className="document-info">
              <Link to={`/documents/${doc.id}`}>{doc.filename}</Link>
              <div className="document-meta">
                {doc.page_count} pages | {formatFileSize(doc.file_size)} | {doc.status}
              </div>
              {doc.tags && doc.tags.length > 0 && (
                <div className="document-tags">
                  {doc.tags.map(tag => (
                    <span
                      key={tag}
                      className="tag clickable"
                      onClick={() => onTagSelect(tag)}
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
            <div className="document-date">
              {new Date(doc.created_at).toLocaleDateString()}
            </div>
          </div>
        ))
      )}
    </div>
  )
}

function formatFileSize(bytes) {
  if (!bytes) return 'Unknown size'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

export default DocumentList
