import { useEffect, useState } from 'react'
import { apiBase } from '../lib/api'

interface Intent {
  id: number
  name: string
  description: string
  status: string
  version: number
  examples_count: number
}

export function Intents() {
  const [intents, setIntents] = useState<Intent[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${apiBase()}/admin/intents`)
      .then((r) => r.json())
      .then((data) => {
        setIntents(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return <div>Loading intents...</div>

  return (
    <section>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h2 style={{ margin: 0 }}>Intents</h2>
        <button style={{ padding: '8px 16px', background: '#3b82f6', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer' }}>
          + Add Intent
        </button>
      </div>
      <div style={{ background: '#fff', borderRadius: 8, border: '1px solid #e5e7eb', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
              <th style={{ textAlign: 'left', padding: 12, fontWeight: 600 }}>Name</th>
              <th style={{ textAlign: 'left', padding: 12, fontWeight: 600 }}>Description</th>
              <th style={{ textAlign: 'left', padding: 12, fontWeight: 600 }}>Status</th>
              <th style={{ textAlign: 'left', padding: 12, fontWeight: 600 }}>Examples</th>
              <th style={{ textAlign: 'left', padding: 12, fontWeight: 600 }}>Version</th>
            </tr>
          </thead>
          <tbody>
            {intents.map((intent) => (
              <tr key={intent.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                <td style={{ padding: 12, fontWeight: 500 }}>{intent.name}</td>
                <td style={{ padding: 12, color: '#6b7280' }}>{intent.description}</td>
                <td style={{ padding: 12 }}>
                  <span style={{ 
                    padding: '4px 8px', 
                    borderRadius: 4, 
                    fontSize: 12, 
                    fontWeight: 500,
                    background: intent.status === 'active' ? '#d1fae5' : '#fee2e2',
                    color: intent.status === 'active' ? '#065f46' : '#991b1b'
                  }}>
                    {intent.status}
                  </span>
                </td>
                <td style={{ padding: 12 }}>{intent.examples_count}</td>
                <td style={{ padding: 12 }}>v{intent.version}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}

