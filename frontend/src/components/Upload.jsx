import { useState, useRef, useCallback } from 'react'
import axios from 'axios'

const ACCEPTED_TYPES = ['video/mp4', 'video/quicktime', 'video/webm']

function Upload({ onStart, onResult, onError }) {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [localError, setLocalError] = useState(null)
  const [dragOver, setDragOver] = useState(false)
  const inputRef = useRef(null)

  const handleFile = useCallback((selected) => {
    setLocalError(null)
    if (!selected) return

    if (!ACCEPTED_TYPES.includes(selected.type)) {
      setLocalError('Please select an MP4, MOV, or WebM video file.')
      return
    }

    if (preview) URL.revokeObjectURL(preview)
    setFile(selected)
    setPreview(URL.createObjectURL(selected))
  }, [preview])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setDragOver(false)
    const dropped = e.dataTransfer.files[0]
    if (dropped) handleFile(dropped)
  }, [handleFile])

  const handleDragOver = useCallback((e) => {
    e.preventDefault()
    setDragOver(true)
  }, [])

  const handleDragLeave = useCallback(() => {
    setDragOver(false)
  }, [])

  const handleSubmit = async () => {
    if (!file) return
    setUploading(true)
    setLocalError(null)
    onStart()

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await axios.post('/api/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      onResult(res.data)
    } catch (err) {
      const data = err.response?.data
      const msg = data?.message || data?.detail || err.message || 'Upload failed'
      onError(msg)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="upload-container">
      <div
        className={`drop-zone ${dragOver ? 'drop-zone--active' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".mp4,.mov,.webm"
          style={{ display: 'none' }}
          onChange={(e) => handleFile(e.target.files[0])}
        />
        {preview ? (
          <video
            className="preview-video"
            src={preview}
            controls
            muted
          />
        ) : (
          <div className="drop-zone__prompt">
            <p className="drop-zone__icon">&#8593;</p>
            <p>Drag & drop a video here, or click to browse</p>
            <p className="drop-zone__hint">MP4, MOV, or WebM</p>
          </div>
        )}
      </div>

      {localError && <p className="upload-error">{localError}</p>}

      <button
        className="upload-btn"
        onClick={handleSubmit}
        disabled={!file || uploading}
      >
        {uploading ? 'Analyzing...' : 'Analyze Video'}
      </button>

      <style>{`
        .upload-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 20px;
          width: 100%;
          max-width: 560px;
        }

        .drop-zone {
          width: 100%;
          min-height: 260px;
          border: 2px dashed #bbb;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: border-color 0.2s, background 0.2s, box-shadow 0.2s;
          overflow: hidden;
          background: #fff;
        }

        .drop-zone:hover {
          border-color: #888;
          background: #f8f8f8;
        }

        .drop-zone--active {
          border-color: #1a1a1a;
          border-style: dashed;
          background: #f0f0f0;
          box-shadow: 0 0 0 4px rgba(26, 26, 26, 0.08);
        }

        .drop-zone__prompt {
          text-align: center;
          color: #666;
          padding: 40px 32px;
        }

        .drop-zone__icon {
          font-size: 2.4rem;
          margin-bottom: 12px;
          color: #999;
        }

        .drop-zone__prompt > p:nth-child(2) {
          font-size: 1rem;
          font-weight: 500;
        }

        .drop-zone__hint {
          font-size: 0.85rem;
          color: #aaa;
          margin-top: 6px;
        }

        .preview-video {
          width: 100%;
          max-height: 320px;
          border-radius: 10px;
        }

        .upload-error {
          color: #d32f2f;
          font-size: 0.9rem;
          text-align: center;
        }

        .upload-btn {
          padding: 12px 36px;
          font-size: 1rem;
          font-weight: 600;
          border: none;
          border-radius: 8px;
          background: #1a1a1a;
          color: #fff;
          cursor: pointer;
          transition: opacity 0.15s, transform 0.15s;
        }

        .upload-btn:hover:not(:disabled) {
          opacity: 0.88;
          transform: translateY(-1px);
        }

        .upload-btn:disabled {
          background: #bbb;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  )
}

export default Upload
