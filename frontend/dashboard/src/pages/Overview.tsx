import { useEffect, useState } from 'react'
import { apiBase } from '../lib/api'

export function Overview() {
  const [status, setStatus] = useState<string>('loading…')
  useEffect(() => {
    fetch(`${apiBase()}/health`).then(async (r) => setStatus(`${r.status} ${r.statusText}`)).catch(() => setStatus('offline'))
  }, [])
  return (
    <section>
      <h2>Overview</h2>
      <p>Backend health: {status}</p>
    </section>
  )
}
