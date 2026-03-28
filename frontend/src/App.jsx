import { useState } from 'react'
import Upload from './components/Upload'
import Results from './components/Results'
import './App.css'

function App() {
  const [result, setResult] = useState(null)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '24px', padding: '48px 20px' }}>
      <h1 style={{ fontSize: '3rem', fontWeight: 700, margin: 0 }}>Cadence</h1>
      {result ? (
        <Results data={result} />
      ) : (
        <Upload onResult={setResult} />
      )}
    </div>
  )
}

export default App
