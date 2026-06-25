import { useState, useEffect } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
} from 'recharts'
import { getOptions, getMetrics, predict } from '../api'

const COLORS = {
  blue: '#6d8aa3',
  blueDark: '#46627a',
  pass: '#6f9b6f',
  fail: '#c06a4f',
  ink: '#2c3a45',
  muted: '#968c75',
  card: '#faf6ec',
  line: '#ddd3bd',
}

// Lijepsi nazivi znacajki za labele u formi
const FIELD_LABELS = {
  'gender': 'Spol',
  'race/ethnicity': 'Etnicka grupa',
  'parental level of education': 'Obrazovanje roditelja',
  'lunch': 'Rucak',
  'test preparation course': 'Priprema za test',
}

// Komponenta koja prikazuje rezultat jednog modela (PROLAZ/PAD + vjerojatnost)
function ResultBox({ title, result }) {
  const passed = result.passed
  const pct = (result.probability * 100).toFixed(1)
  return (
    <div
      style={{
        background: COLORS.ink,
        borderRadius: 14,
        padding: 18,
        color: '#f0e6d2',
        flex: 1,
        minWidth: 200,
      }}
    >
      <div style={{ fontSize: 12, color: '#c9b89e', marginBottom: 8 }}>{title}</div>
      <div
        className="mono"
        style={{
          fontSize: 30,
          fontWeight: 700,
          color: passed ? COLORS.pass : COLORS.fail,
          letterSpacing: 1,
        }}
      >
        {result.prediction}
      </div>
      <div style={{ fontSize: 13, color: '#e0c89e', marginTop: 2 }}>
        vjerojatnost prolaza: {pct}%
      </div>
      <div
        style={{
          background: '#3a4a55',
          borderRadius: 20,
          height: 8,
          marginTop: 12,
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            background: passed ? COLORS.pass : COLORS.fail,
            width: `${pct}%`,
            height: '100%',
          }}
        />
      </div>
    </div>
  )
}

export default function Card3Predict() {
  const [options, setOptions] = useState(null)
  const [metrics, setMetrics] = useState(null)
  const [form, setForm] = useState({})
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Ucitaj opcije za formu i metrike modela
  useEffect(() => {
    Promise.all([getOptions(), getMetrics()])
      .then(([opts, m]) => {
        setOptions(opts)
        setMetrics(m)
        // Postavi pocetne vrijednosti forme (prva opcija svake znacajke)
        const initial = {}
        Object.entries(opts).forEach(([k, vals]) => { initial[k] = vals[0] })
        setForm(initial)
      })
      .catch((e) => setError(e.message))
  }, [])

  function handleChange(feature, value) {
    setForm((prev) => ({ ...prev, [feature]: value }))
  }

  async function handlePredict() {
    setLoading(true)
    setError(null)
    try {
      const res = await predict(form)
      setResult(res)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  if (error && !options) return <div className="error">Greska: {error}</div>
  if (!options) return <div className="loading">Ucitavam modele…</div>

  return (
    <div>
      {/* --- Forma za unos + rezultat --- */}
      <div className="card">
        <div className="card-title">Predikcija uspjeha studenta</div>
        <div className="row">
          {/* Lijevo: forma */}
          <div className="col">
            {Object.entries(options).map(([feature, values]) => (
              <label className="field" key={feature}>
                <span className="field-label">
                  {FIELD_LABELS[feature] || feature}
                </span>
                <select
                  value={form[feature] || ''}
                  onChange={(e) => handleChange(feature, e.target.value)}
                >
                  {values.map((v) => (
                    <option key={v} value={v}>{v}</option>
                  ))}
                </select>
              </label>
            ))}
            <button className="btn" onClick={handlePredict} disabled={loading}>
              {loading ? 'Predviđam…' : 'Predvidi uspjeh'}
            </button>
          </div>

          {/* Desno: rezultat oba modela */}
          <div className="col">
            {error && <div className="error" style={{ marginBottom: 12 }}>{error}</div>}
            {result ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                <ResultBox
                  title="Random Forest (ML)"
                  result={result.random_forest}
                />
                <ResultBox
                  title="Neuronska mreza (DL)"
                  result={result.deep_learning}
                />
              </div>
            ) : (
              <p className="loading">
                Odaberi karakteristike studenta i klikni "Predvidi uspjeh".
              </p>
            )}
          </div>
        </div>
      </div>

      {/* --- Metrike modela --- */}
      {metrics && (
        <>
          <div className="card">
            <div className="card-title">Usporedba modela (tocnost)</div>
            <div className="metric-grid">
              <div className="metric">
                <div className="label">Random Forest (ML)</div>
                <div className="value blue">
                  {(metrics.random_forest.accuracy * 100).toFixed(1)}%
                </div>
              </div>
              <div className="metric">
                <div className="label">Neuronska mreza (DL)</div>
                <div className="value blue">
                  {(metrics.deep_learning.accuracy * 100).toFixed(1)}%
                </div>
              </div>
            </div>
            <p style={{ fontSize: 12, color: COLORS.muted, marginTop: 12 }}>
              Na ovako malom tablicnom skupu (1000 redaka) Random Forest obicno
              bude jednako dobar ili bolji od neuronske mreze — to je ocekivano.
            </p>
          </div>

          {/* --- Feature importance (Random Forest) --- */}
          <div className="card">
            <div className="card-title">
              Najvaznije znacajke (Random Forest)
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                layout="vertical"
                data={metrics.random_forest.top_features.slice(0, 8).map((f) => ({
                  feature: f.feature,
                  importance: +(f.importance * 100).toFixed(2),
                }))}
                margin={{ left: 20, right: 20 }}
              >
                <XAxis type="number" tick={{ fontSize: 11, fill: COLORS.muted }} />
                <YAxis
                  type="category"
                  dataKey="feature"
                  tick={{ fontSize: 10, fill: COLORS.ink }}
                  width={170}
                />
                <Tooltip
                  contentStyle={{
                    background: COLORS.card,
                    border: `1px solid ${COLORS.line}`,
                    borderRadius: 8,
                    fontSize: 12,
                  }}
                  formatter={(v) => [`${v}%`, 'vaznost']}
                />
                <Bar dataKey="importance" fill={COLORS.blue} radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
            <p style={{ fontSize: 12, color: COLORS.muted, marginTop: 8 }}>
              Rucak (socioekonomski status) i priprema za test najvise utjecu na
              predikciju — isti zakljucak kao u eksplorativnoj analizi.
            </p>
          </div>
        </>
      )}
    </div>
  )
}