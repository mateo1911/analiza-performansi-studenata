import { useState, useEffect } from 'react'
import {
  getStats,
  getDescribe,
  getFeatures,
  getGroupAverages,
} from '../api'

// Lijepsi nazivi stupaca za prikaz (CSV ima tehnicke nazive s razmacima).
const STAT_LABELS = {
  count: 'Broj',
  mean: 'Prosjek',
  std: 'Std. devijacija',
  min: 'Min',
  '25%': '25%',
  '50%': 'Medijan',
  '75%': '75%',
  max: 'Max',
}

export default function Card1Stats() {
  const [stats, setStats] = useState(null)
  const [describe, setDescribe] = useState(null)
  const [features, setFeatures] = useState([])
  const [groupCol, setGroupCol] = useState('lunch')
  const [groupRows, setGroupRows] = useState(null)
  const [error, setError] = useState(null)

  // Ucitaj osnovne podatke kod prvog prikaza kartice
  useEffect(() => {
    Promise.all([getStats(), getDescribe(), getFeatures()])
      .then(([s, d, f]) => {
        setStats(s)
        setDescribe(d.rows)
        setFeatures(f.categorical_features)
      })
      .catch((e) => setError(e.message))
  }, [])

  // Kad se promijeni odabrana grupa, dohvati prosjeke po toj grupi
  useEffect(() => {
    getGroupAverages(groupCol)
      .then((r) => setGroupRows(r.rows))
      .catch((e) => setError(e.message))
  }, [groupCol])

  if (error) return <div className="error">Greska: {error}</div>
  if (!stats) return <div className="loading">Ucitavam statistike…</div>

  return (
    <div>
      {/* --- Brojcani pregled (metric kartice) --- */}
      <div className="metric-grid" style={{ marginBottom: 18 }}>
        <div className="metric">
          <div className="label">Ukupno studenata</div>
          <div className="value">{stats.total_students}</div>
        </div>
        <div className="metric">
          <div className="label">Ukupni prosjek</div>
          <div className="value blue">{stats.overall_average}</div>
        </div>
        <div className="metric">
          <div className="label">Prolaznost</div>
          <div className="value pass">{stats.pass_rate}%</div>
        </div>
        <div className="metric">
          <div className="label">Prosli</div>
          <div className="value pass">{stats.passed_count}</div>
        </div>
        <div className="metric">
          <div className="label">Pali</div>
          <div className="value fail">{stats.failed_count}</div>
        </div>
      </div>

      {/* --- Prosjek po predmetu --- */}
      <div className="card">
        <div className="card-title">Prosjek po predmetu</div>
        <div className="metric-grid">
          {Object.entries(stats.subject_averages).map(([subj, val]) => (
            <div className="metric" key={subj}>
              <div className="label">{subj}</div>
              <div className="value blue">{val}</div>
            </div>
          ))}
        </div>
      </div>

      {/* --- Statisticka tablica (describe) --- */}
      <div className="card">
        <div className="card-title">Statisticki opis ocjena</div>
        {describe && (
          <table>
            <thead>
              <tr>
                <th>Statistika</th>
                <th>Matematika</th>
                <th>Citanje</th>
                <th>Pisanje</th>
                <th>Prosjek</th>
              </tr>
            </thead>
            <tbody>
              {describe.map((row) => (
                <tr key={row.statistic}>
                  <td>{STAT_LABELS[row.statistic] || row.statistic}</td>
                  <td className="num">{row['math score']}</td>
                  <td className="num">{row['reading score']}</td>
                  <td className="num">{row['writing score']}</td>
                  <td className="num">{row['average score']}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* --- Prosjek po grupi (s dropdownom) --- */}
      <div className="card">
        <div className="card-title">Prosjek po grupi</div>

        <label className="field" style={{ maxWidth: 320 }}>
          <span className="field-label">Grupiraj po znacajki</span>
          <select value={groupCol} onChange={(e) => setGroupCol(e.target.value)}>
            {features.map((f) => (
              <option key={f} value={f}>{f}</option>
            ))}
          </select>
        </label>

        {groupRows && (
          <table>
            <thead>
              <tr>
                <th>Grupa</th>
                <th>Broj</th>
                <th>Mat.</th>
                <th>Cit.</th>
                <th>Pis.</th>
                <th>Prosjek</th>
                <th>Prolaznost</th>
              </tr>
            </thead>
            <tbody>
              {groupRows.map((row) => (
                <tr key={row.group}>
                  <td>{row.group}</td>
                  <td className="num">{row.count}</td>
                  <td className="num">{row.math}</td>
                  <td className="num">{row.reading}</td>
                  <td className="num">{row.writing}</td>
                  <td className="num">{row.average}</td>
                  <td className="num">{row.pass_rate}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}