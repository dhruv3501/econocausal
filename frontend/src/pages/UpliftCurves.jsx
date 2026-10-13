import { useMockJson } from '../useMockJson.js'

export default function UpliftCurves() {
  const { data, error } = useMockJson('mock_uplift')

  return (
    <section>
      <h2>Uplift Curves</h2>
      <p className="muted">Coming next: Plotly Qini / uplift chart (14–15 Oct).</p>
      {error && <p className="error">Could not load mock data: {error}</p>}
      {!data && !error && <p>Loading mock uplift curve…</p>}
      {data && <p>Loaded a curve with {data.x.length} points.</p>}
    </section>
  )
}
