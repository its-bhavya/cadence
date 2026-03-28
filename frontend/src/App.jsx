import { useState } from 'react'
import Upload from './components/Upload'
import Progress from './components/Progress'
import Results from './components/Results'
import './App.css'

function App() {
  const [mode, setMode] = useState('idle') // idle | loading | done
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [step, setStep] = useState(0)

  const handleUploadStart = () => {
    setError(null)
    setMode('loading')
    setStep(1)
  }

  const handleResult = (data) => {
    setStep(6)
    setResult(data)
    setMode('done')
  }

  const handleError = (msg) => {
    setError(msg)
    setStep(0)
    setMode('idle')
  }

  const handleReset = () => {
    setResult(null)
    setError(null)
    setStep(0)
    setMode('idle')
  }

  return (
    <>
      <header className="app-header">
        <span className="app-header__title" onClick={handleReset}>Cadence</span>
      </header>

      {error && (
        <div className="app-error-banner">
          <span>{error}</span>
          <button className="app-error-dismiss" onClick={() => setError(null)}>&#10005;</button>
        </div>
      )}

      <main className="app-main">
        {mode === 'idle' && (
          <Upload
            onStart={handleUploadStart}
            onResult={handleResult}
            onError={handleError}
          />
        )}

        {mode === 'loading' && (
          <Progress currentStep={step} onStepChange={setStep} loading />
        )}

        {mode === 'done' && result && (
          <>
            <Results data={result} />
            <button className="app-reset-btn" onClick={handleReset}>
              Analyze Another Video
            </button>
          </>
        )}
      </main>

      <style>{`
        .app-header {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          height: 56px;
          display: flex;
          align-items: center;
          padding: 0 24px;
          background: #fff;
          border-bottom: 1px solid #eee;
          z-index: 100;
        }

        .app-header__title {
          font-size: 1.3rem;
          font-weight: 700;
          color: #1a1a1a;
          cursor: pointer;
        }

        .app-main {
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 80px 20px 48px;
          gap: 24px;
          min-height: 100vh;
        }

        .app-error-banner {
          position: fixed;
          top: 56px;
          left: 0;
          right: 0;
          background: #fef2f2;
          color: #dc2626;
          padding: 10px 24px;
          font-size: 0.9rem;
          display: flex;
          justify-content: space-between;
          align-items: center;
          z-index: 99;
          border-bottom: 1px solid #fecaca;
        }

        .app-error-dismiss {
          background: none;
          border: none;
          color: #dc2626;
          cursor: pointer;
          font-size: 1rem;
          padding: 4px 8px;
        }

        .app-reset-btn {
          margin-top: 8px;
          padding: 10px 24px;
          font-size: 0.95rem;
          font-weight: 600;
          border: 2px solid #1a1a1a;
          border-radius: 8px;
          background: #fff;
          color: #1a1a1a;
          cursor: pointer;
          transition: background 0.2s;
        }

        .app-reset-btn:hover {
          background: #f5f5f5;
        }
      `}</style>
    </>
  )
}

export default App
