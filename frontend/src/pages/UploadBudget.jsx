import { useMockJson } from '../useMockJson.js'

export default function UploadBudget() {
  const { data, error } = useMockJson('mock_ite')

  return (
    <section>
      <h2>Upload &amp; Budget</h2>
      <p className="muted">
        Coming next: CSV upload and budget input with validation.
      </p>
      {error && <p className="error">Could not load mock data: {error}</p>}
      {!data && !error && <p>Loading mock ITE scores…</p>}
      {data && (
        <>
          <p>Loaded {data.length} mock ITE rows. First 5:</p>
          <table>
            <thead>
              <tr><th>user_id</th><th>ite_10</th><th>ite_20</th></tr>
            </thead>
            <tbody>
              {data.slice(0, 5).map((r) => (
                <tr key={r.user_id}>
                  <td>{r.user_id}</td><td>{r.ite_10}</td><td>{r.ite_20}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </section>
  )
}