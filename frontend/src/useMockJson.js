import { useEffect, useState } from 'react'

// Loads /mock/<name>.json from the public folder.
export function useMockJson(name) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch(`/mock/${name}.json`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json()
      })
      .then(setData)
      .catch((e) => setError(e.message))
  }, [name])

  return { data, error }
}