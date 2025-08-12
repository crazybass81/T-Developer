import React, { useState, useEffect } from 'react'

interface AppState {
  loading: boolean
  data: any[]
  user: any | null
}

const App: React.FC = () => {
  const [state, setState] = useState<AppState>({
    loading: false,
    data: [],
    user: null
  })

  useEffect(() => {
    // 초기 데이터 로드
    loadInitialData()
  }, [])

  const loadInitialData = async () => {
    setState(prev => ({ ...prev, loading: true }))
    try {
      // 실제 데이터 로드 로직
      await new Promise(resolve => setTimeout(resolve, 1000))
      setState(prev => ({ 
        ...prev, 
        loading: false,
        data: []
      }))
    } catch (error) {
      console.error('Failed to load data:', error)
      setState(prev => ({ ...prev, loading: false }))
    }
  }

  return (
    <div className="container">
      <header className="header">
        <h1>Test Todo App with Agno</h1>
        <p>Production-ready React Application</p>
      </header>
      
      {state.loading ? (
        <div className="loading">Loading...</div>
      ) : (
        <main className="main-content">
          <section className="features">
            <h2>Features</h2>
            <ul>
              <li>dark-mode</li>
<li>search</li>
<li>filter</li>
<li>priority</li>
<li>statistics</li>
<li>todo</li>
            </ul>
          </section>
          
          <section className="actions">
            <button className="button" onClick={loadInitialData}>
              Refresh Data
            </button>
          </section>
        </main>
      )}
    </div>
  )
}

export default App