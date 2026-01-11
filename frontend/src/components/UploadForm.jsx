import { useState, useRef } from 'react'
import { uploadDocument } from '../api'

function UploadForm() {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)
  const fileInputRef = useRef(null)

  function handleFileChange(e) {
    const selectedFile = e.target.files?.[0]

    if (!selectedFile) {
      setFile(null)
      return
    }

    if (!selectedFile.name.toLowerCase().endsWith('.pdf')) {
      setError('Only PDF files are allowed')
      setFile(null)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
      return
    }

    setError(null)
    setFile(selectedFile)
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!file) return

    try {
      setUploading(true)
      setError(null)
      await uploadDocument(file)
      setFile(null)
      e.target.reset()
      window.location.reload()
    } catch (err) {
      setError('Failed to upload document')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="upload-form">
      <h2>Upload Document</h2>
      {error && <div className="error">{error}</div>}
      <form onSubmit={handleSubmit}>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,application/pdf"
          onChange={handleFileChange}
          disabled={uploading}
        />
        <button type="submit" disabled={!file || uploading}>
          {uploading ? 'Uploading...' : 'Upload'}
        </button>
      </form>
    </div>
  )
}

export default UploadForm
