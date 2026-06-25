import { useState } from 'react'

import Card1Stats from './components/Card1Stats.jsx'
// Preostale kartice dodajemo u sljedecim commitovima.
// import Card2Charts from './components/Card2Charts.jsx'
// import Card3Predict from './components/Card3Predict.jsx'

// Definicija tri kartice (taba) prema profesorovoj uputi:
//  1 - eksplorativna analiza (brojcano/tablicno)
//  2 - eksplorativna analiza (grafovi)
//  3 - prediktivna analitika (ML + DL)
const TABS = [
  { id: 'stats', label: '01 · Statistike' },
  { id: 'charts', label: '02 · Grafovi' },
  { id: 'predict', label: '03 · Predikcija' },
]

export default function App() {
  const [activeTab, setActiveTab] = useState('stats')

  return (
    <div className="app">
      {/* Zaglavlje */}
      <header className="header">
        <div>
          <h1>Analiza performansi studenata</h1>
          <div className="subtitle">
            Learning Analytics · 1000 studenata · 3 predmeta
          </div>
        </div>
        <span className="live-badge">● ANALITIKA</span>
      </header>

      {/* Tab navigacija */}
      <nav className="tabs">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            className={`tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      {/* Sadrzaj aktivne kartice */}
      <main>
        {activeTab === 'stats' && <Card1Stats />}
        {activeTab === 'charts' && (
          <div className="card">
            <div className="card-title">Kartica 2 — grafovi (uskoro)</div>
            <p className="loading">Ovdje ce ici grafovi i uvidi.</p>
          </div>
        )}
        {activeTab === 'predict' && (
          <div className="card">
            <div className="card-title">Kartica 3 — predikcija (uskoro)</div>
            <p className="loading">Ovdje ce ici ML + DL predikcija.</p>
          </div>
        )}
      </main>
    </div>
  )
}