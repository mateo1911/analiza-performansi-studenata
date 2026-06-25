import { useState, useEffect } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'
import {
  getDistributions,
  getCorrelation,
  getPassFail,
  getComparison,
  getFeatures,
} from '../api'

// Retro paleta (ista kao u index.css) - recharts trazi boje kao props.
const COLORS = {
  blue: '#6d8aa3',
  blueDark: '#46627a',
  blueLight: '#b9cad8',
  pass: '#6f9b6f',
  fail: '#c06a4f',
  ink: '#2c3a45',
  muted: '#968c75',
  card: '#faf6ec',
  line: '#ddd3bd',
}

// Boja za heatmapu korelacije: sto je vrijednost veca, to tamnija plava.
function corrColor(v) {
  // v je 0..1; interpoliramo izmedu svijetle i tamne plave
  const light = [221, 230, 237] // #dde6ed
  const dark = [70, 98, 122]    // #46627a
  const mix = light.map((c, i) => Math.round(c + (dark[i] - c) * v))
  return `rgb(${mix[0]}, ${mix[1]}, ${mix[2]})`
}

// Kratki nazivi ocjena za grafove
const SHORT = {
  'math score': 'Matematika',
  'reading score': 'Citanje',
  'writing score': 'Pisanje',
}

export default function Card2Charts() {
  const [distributions, setDistributions] = useState(null)
  const [correlation, setCorrelation] = useState(null)
  const [passFail, setPassFail] = useState(null)
  const [features, setFeatures] = useState([])
  const [groupCol, setGroupCol] = useState('parental level of education')
  const [comparison, setComparison] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([
      getDistributions(10),
      getCorrelation(),
      getPassFail(),
      getFeatures(),
    ])
      .then(([d, c, pf, f]) => {
        setDistributions(d)
        setCorrelation(c)
        setPassFail(pf)
        setFeatures(f.categorical_features)
      })
      .catch((e) => setError(e.message))
  }, [])

  useEffect(() => {
    getComparison(groupCol)
      .then(setComparison)
      .catch((e) => setError(e.message))
  }, [groupCol])

  if (error) return <div className="error">Greska: {error}</div>
  if (!distributions) return <div className="loading">Ucitavam grafove…</div>

  // Pretvori histogram backend formata u format koji recharts voli.
  // bin_edges: [0,10,20,...]; counts: [2,5,...] -> [{bin:'0-10', count:2}, ...]
  function toBarData(dist) {
    return dist.counts.map((c, i) => ({
      bin: `${Math.round(dist.bin_edges[i])}-${Math.round(dist.bin_edges[i + 1])}`,
      count: c,
    }))
  }

  const pieData = [
    { name: 'Prosli', value: passFail.passed, color: COLORS.pass },
    { name: 'Pali', value: passFail.failed, color: COLORS.fail },
  ]

  return (
    <div>
      {/* --- Histogrami distribucija ocjena --- */}
      <div className="card">
        <div className="card-title">Distribucija ocjena po predmetu</div>
        <div className="row">
          {Object.entries(distributions).map(([col, dist]) => (
            <div className="col" key={col}>
              <h3 style={{ marginBottom: 8, color: COLORS.blueDark }}>
                {SHORT[col] || col}
              </h3>
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={toBarData(dist)}>
                  <XAxis
                    dataKey="bin"
                    tick={{ fontSize: 10, fill: COLORS.muted }}
                    interval={1}
                  />
                  <YAxis tick={{ fontSize: 10, fill: COLORS.muted }} />
                  <Tooltip
                    contentStyle={{
                      background: COLORS.card,
                      border: `1px solid ${COLORS.line}`,
                      borderRadius: 8,
                      fontSize: 12,
                    }}
                  />
                  <Bar dataKey="count" fill={COLORS.blue} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ))}
        </div>
      </div>

      <div className="row">
        {/* --- Korelacijska heatmapa --- */}
        <div className="col">
          <div className="card">
            <div className="card-title">Korelacija ocjena</div>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ textAlign: 'center' }}>
                <thead>
                  <tr>
                    <th></th>
                    {correlation.labels.map((l) => (
                      <th key={l} style={{ textAlign: 'center' }}>
                        {SHORT[l]?.slice(0, 4) || l}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {correlation.matrix.map((row, i) => (
                    <tr key={i}>
                      <td style={{ fontWeight: 600 }}>
                        {SHORT[correlation.labels[i]]?.slice(0, 4)}
                      </td>
                      {row.map((v, j) => (
                        <td
                          key={j}
                          className="num"
                          style={{
                            background: corrColor(v),
                            color: v > 0.6 ? '#fff' : COLORS.ink,
                            fontWeight: 600,
                            borderRadius: 6,
                          }}
                        >
                          {v.toFixed(2)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p style={{ fontSize: 12, color: COLORS.muted, marginTop: 12 }}>
              Tamnije = jaca povezanost. Citanje i pisanje su gotovo savrseno
              povezani (0.95).
            </p>
          </div>
        </div>

        {/* --- Pie prolaz/pad --- */}
        <div className="col">
          <div className="card">
            <div className="card-title">Omjer prolaz / pad</div>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={pieData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={2}
                >
                  {pieData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: COLORS.card,
                    border: `1px solid ${COLORS.line}`,
                    borderRadius: 8,
                    fontSize: 12,
                  }}
                />
                <Legend wrapperStyle={{ fontSize: 13 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* --- Usporedba prosjeka po grupi --- */}
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

        {comparison && (
          <ResponsiveContainer width="100%" height={260}>
            <BarChart
              data={comparison.labels.map((l, i) => ({
                label: l,
                value: comparison.values[i],
              }))}
              margin={{ bottom: 40 }}
            >
              <XAxis
                dataKey="label"
                tick={{ fontSize: 11, fill: COLORS.muted }}
                angle={-20}
                textAnchor="end"
                height={60}
              />
              <YAxis tick={{ fontSize: 11, fill: COLORS.muted }} domain={[0, 100]} />
              <Tooltip
                contentStyle={{
                  background: COLORS.card,
                  border: `1px solid ${COLORS.line}`,
                  borderRadius: 8,
                  fontSize: 12,
                }}
              />
              <Bar dataKey="value" fill={COLORS.blue} radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  )
}