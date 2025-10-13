import { useEffect, useState } from 'react'
import { apiBase } from '../lib/api'

interface Template {
  id: number
  key: string
  lang: string
  body: string
  variables: string[] | null
  version: number
}

export function Templates() {
  const [templates, setTemplates] = useState<Template[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${apiBase()}/admin/templates`)
      .then((r) => r.json())
      .then((data) => {
        setTemplates(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return <div>Loading templates...</div>

  return (
    <section>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <h2 style={{ margin: 0 }}>Response Templates</h2>
          <p style={{ color: '#6b7280', marginTop: 4 }}>Bangla response templates with variable substitution</p>
        </div>
        <button style={{ padding: '8px 16px', background: '#3b82f6', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer' }}>
          + Add Template
        </button>
      </div>
      <div style={{ display: 'grid', gap: 16 }}>
        {templates.map((template) => (
          <div key={template.id} style={{ background: '#fff', borderRadius: 8, border: '1px solid #e5e7eb', padding: 16 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: 12 }}>
              <div>
                <div style={{ fontWeight: 600, marginBottom: 4 }}>{template.key}</div>
                <div style={{ fontSize: 12, color: '#9ca3af' }}>
                  {template.lang} • v{template.version}
                  {template.variables && template.variables.length > 0 && (
                    <span> • Variables: {template.variables.join(', ')}</span>
                  )}
                </div>
              </div>
              <button style={{ padding: '4px 8px', fontSize: 12, background: 'transparent', border: '1px solid #d1d5db', borderRadius: 4, cursor: 'pointer' }}>
                Edit
              </button>
            </div>
            <div style={{ 
              padding: 12, 
              background: '#f9fafb', 
              borderRadius: 6, 
              fontFamily: 'system-ui', 
              fontSize: 14,
              color: '#374151',
              lineHeight: 1.6
            }}>
              {template.body}
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

