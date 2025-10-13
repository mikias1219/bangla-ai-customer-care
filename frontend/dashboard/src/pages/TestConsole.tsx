import { useState } from 'react'
import { apiBase } from '../lib/api'

export function TestConsole() {
  const [text, setText] = useState('Amar order 123 kothay?')
  const [nlu, setNlu] = useState<any>(null)
  const [dm, setDm] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  async function run() {
    setLoading(true)
    setNlu(null)
    setDm(null)
    try {
      const nluRes = await fetch(`${apiBase()}/nlu/resolve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      }).then((r) => r.json())
      setNlu(nluRes)
      const dmRes = await fetch(`${apiBase()}/dm/decide`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ intent: nluRes.intent, entities: nluRes.entities, context: { channel: 'web' } })
      }).then((r) => r.json())
      setDm(dmRes)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section>
      <h2>Test Console</h2>
      <label>
        Utterance
        <input value={text} onChange={(e) => setText(e.target.value)} style={{ display: 'block', width: '100%', maxWidth: 520, padding: 8, marginTop: 6 }} />
      </label>
      <button onClick={run} disabled={loading} style={{ marginTop: 12 }}>
        {loading ? 'Running…' : 'Resolve + Decide'}
      </button>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginTop: 16 }}>
        <pre style={{ background: '#f7f7f7', padding: 12, borderRadius: 6, overflow: 'auto' }}>
{JSON.stringify(nlu, null, 2)}
        </pre>
        <pre style={{ background: '#f7f7f7', padding: 12, borderRadius: 6, overflow: 'auto' }}>
{JSON.stringify(dm, null, 2)}
        </pre>
      </div>
    </section>
  )
}
