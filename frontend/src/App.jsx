import { useState } from 'react'
import Upload from './components/Upload'
import './App.css'

function App() {
  const [result, setResult] = useState(null)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '24px', padding: '48px 20px' }}>
      <h1 style={{ fontSize: '3rem', fontWeight: 700, margin: 0 }}>Cadence</h1>
      {result ? (
        <pre style={{ textAlign: 'left', maxWidth: 560, width: '100%', overflow: 'auto' }}>
          {JSON.stringify(result, null, 2)}
        </pre>
      ) : (
        <Upload onResult={setResult} />
      )}
    </div>
  )
}

export default App
