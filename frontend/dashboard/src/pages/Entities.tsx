import { useEffect, useState } from 'react'
import { apiBase } from '../lib/api'

interface Entity {
  id: number
  name: string
  entity_type: string
  pattern: string | null
  description: string | null
  version: number
}

export function Entities() {
  const [entities, setEntities] = useState<Entity[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${apiBase()}/admin/entities`)
      .then((r) => r.json())
      .then((data) => {
        setEntities(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return <div>Loading entities...</div>

  return (
    <section>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h2 style={{ margin: 0 }}>Entities</h2>
        <button style={{ padding: '8px 16px', background: '#3b82f6', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer' }}>
          + Add Entity
        </button>
      </div>
      <div style={{ background: '#fff', borderRadius: 8, border: '1px solid #e5e7eb', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
              <th style={{ textAlign: 'left', padding: 12, fontWeight: 600 }}>Name</th>
              <th style={{ textAlign: 'left', padding: 12, fontWeight: 600 }}>Type</th>
              <th style={{ textAlign: 'left', padding: 12, fontWeight: 600 }}>Pattern</th>
              <th style={{ textAlign: 'left', padding: 12, fontWeight: 600 }}>Description</th>
              <th style={{ textAlign: 'left', padding: 12, fontWeight: 600 }}>Version</th>
            </tr>
          </thead>
          <tbody>
            {entities.map((entity) => (
              <tr key={entity.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                <td style={{ padding: 12, fontWeight: 500 }}>{entity.name}</td>
                <td style={{ padding: 12 }}>
                  <span style={{ padding: '4px 8px', borderRadius: 4, fontSize: 12, background: '#e0e7ff', color: '#3730a3' }}>
                    {entity.entity_type}
                  </span>
                </td>
                <td style={{ padding: 12, fontFamily: 'monospace', fontSize: 12, color: '#6b7280' }}>
                  {entity.pattern ? entity.pattern.substring(0, 40) + '...' : '-'}
                </td>
                <td style={{ padding: 12, color: '#6b7280' }}>{entity.description || '-'}</td>
                <td style={{ padding: 12 }}>v{entity.version}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}

