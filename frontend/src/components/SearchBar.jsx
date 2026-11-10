import { useState } from 'react'
import { Link } from 'react-router-dom'
import { searchDocuments } from '../api'

function SearchBar({ selectedTag }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [showResults, setShowResults] = useState(false)
  const [searching, setSearching] = useState(false)

  async function handleSearch(e) {
    e.preventDefault()
    if (!query.trim()) return

    try {
      setSearching(true)
      const data = await searchDocuments(query, selectedTag)
      setResults(data)
      setShowResults(true)
    } catch (err) {
      console.error('Search failed:', err)
    } finally {
      setSearching(false)
    }
  }

  return (
    <div className="search-container">
      <form className="search-bar" onSubmit={handleSearch}>
        {selectedTag && (
          <span className="search-tag-indicator" title={`Searching within tag: ${selectedTag}`}>
            #{selectedTag}
          </span>
        )}
        <input
          type="text"
          placeholder={selectedTag ? `Search in "${selectedTag}"...` : "Search documents..."}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => results.length > 0 && setShowResults(true)}
        />
        <button type="submit" disabled={searching}>
          {searching ? '...' : 'Search'}
        </button>
      </form>
      {showResults && (
        <div className="search-results">
          {results.length === 0 ? (
            <div className="result-item">No results found</div>
          ) : (
            results.map(result => (
              <div key={result.id} className="result-item">
                <Link
                  to={`/documents/${result.id}`}
                  onClick={() => setShowResults(false)}
                >
                  {result.filename}
                </Link>
                <div className="snippet">{result.snippet}</div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
}

export default SearchBar
