import { useState, useRef, useCallback, useEffect } from 'react'
import axios from 'axios'
import Progress from './Progress'

const ACCEPTED_TYPES = ['video/mp4', 'video/quicktime', 'video/webm']

function Upload({ onResult }) {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)
  const [dragOver, setDragOver] = useState(false)
  const [step, setStep] = useState(0)
  const inputRef = useRef(null)
  const timerRef = useRef(null)

  useEffect(() => {
    if (uploading) {
      setStep(1)
      timerRef.current = setInterval(() => {
        setStep((s) => (s < 5 ? s + 1 : s))
      }, 4000)
    } else {
      clearInterval(timerRef.current)
    }
    return () => clearInterval(timerRef.current)
  }, [uploading])

  const handleFile = useCallback((selected) => {
    setError(null)
    if (!selected) return

    if (!ACCEPTED_TYPES.includes(selected.type)) {
      setError('Please select an MP4, MOV, or WebM video file.')
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
    setError(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await axios.post('/api/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setStep(6)
      onResult(res.data)
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Upload failed'
      setError(msg)
      setStep(0)
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

      {uploading && <Progress currentStep={step} />}

      {error && <p className="upload-error">{error}</p>}

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
          gap: 16px;
          width: 100%;
          max-width: 560px;
        }

        .drop-zone {
          width: 100%;
          min-height: 240px;
          border: 2px dashed #ccc;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: border-color 0.2s, background 0.2s;
          overflow: hidden;
        }

        .drop-zone:hover,
        .drop-zone--active {
          border-color: #555;
          background: #fafafa;
        }

        .drop-zone__prompt {
          text-align: center;
          color: #888;
          padding: 32px;
        }

        .drop-zone__icon {
          font-size: 2rem;
          margin-bottom: 8px;
        }

        .drop-zone__hint {
          font-size: 0.85rem;
          color: #aaa;
          margin-top: 4px;
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
          padding: 12px 32px;
          font-size: 1rem;
          font-weight: 600;
          border: none;
          border-radius: 8px;
          background: #1a1a1a;
          color: #fff;
          cursor: pointer;
          transition: opacity 0.2s;
        }

        .upload-btn:hover:not(:disabled) {
          opacity: 0.85;
        }

        .upload-btn:disabled {
          background: #999;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  )
}

export default Upload
