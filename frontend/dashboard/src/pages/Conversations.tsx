import { useEffect, useState } from 'react'
import { apiBase } from '../lib/api'

interface Conversation {
  id: number
  conversation_id: string
  channel: string
  customer_id: string | null
  status: string
  started_at: string
  ended_at: string | null
}

export function Conversations() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${apiBase()}/admin/conversations`)
      .then((r) => r.json())
      .then((data) => {
        setConversations(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return <div>Loading conversations...</div>

  return (
    <section>
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ margin: 0 }}>Conversations</h2>
        <p style={{ color: '#6b7280', marginTop: 4 }}>View all customer conversations across channels</p>
      </div>
      {conversations.length === 0 ? (
        <div style={{ background: '#fff', borderRadius: 8, border: '1px solid #e5e7eb', padding: 48, textAlign: 'center' }}>
          <p style={{ color: '#9ca3af' }}>No conversations yet. Start a conversation via the test console or connect a channel.</p>
        </div>
      ) : (
        <div style={{ background: '#fff', borderRadius: 8, border: '1px solid #e5e7eb', overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
                <th style={{ textAlign: 'left', padding: 12, fontWeight: 600 }}>ID</th>
                <th style={{ textAlign: 'left', padding: 12, fontWeight: 600 }}>Channel</th>
                <th style={{ textAlign: 'left', padding: 12, fontWeight: 600 }}>Customer</th>
                <th style={{ textAlign: 'left', padding: 12, fontWeight: 600 }}>Status</th>
                <th style={{ textAlign: 'left', padding: 12, fontWeight: 600 }}>Started</th>
                <th style={{ textAlign: 'left', padding: 12, fontWeight: 600 }}>Duration</th>
              </tr>
            </thead>
            <tbody>
              {conversations.map((conv) => (
                <tr key={conv.id} style={{ borderBottom: '1px solid #f3f4f6', cursor: 'pointer' }} onClick={() => alert(`View conversation ${conv.conversation_id}`)}>
                  <td style={{ padding: 12, fontFamily: 'monospace', fontSize: 12 }}>{conv.conversation_id.substring(0, 8)}</td>
                  <td style={{ padding: 12 }}>
                    <span style={{ padding: '4px 8px', borderRadius: 4, fontSize: 12, background: '#dbeafe', color: '#1e40af' }}>
                      {conv.channel}
                    </span>
                  </td>
                  <td style={{ padding: 12, color: '#6b7280' }}>{conv.customer_id || 'Anonymous'}</td>
                  <td style={{ padding: 12 }}>
                    <span style={{ 
                      padding: '4px 8px', 
                      borderRadius: 4, 
                      fontSize: 12,
                      background: conv.status === 'completed' ? '#d1fae5' : conv.status === 'escalated' ? '#fef3c7' : '#e0e7ff',
                      color: conv.status === 'completed' ? '#065f46' : conv.status === 'escalated' ? '#92400e' : '#3730a3'
                    }}>
                      {conv.status}
                    </span>
                  </td>
                  <td style={{ padding: 12, fontSize: 13, color: '#6b7280' }}>{new Date(conv.started_at).toLocaleString()}</td>
                  <td style={{ padding: 12, fontSize: 13, color: '#6b7280' }}>
                    {conv.ended_at ? `${Math.round((new Date(conv.ended_at).getTime() - new Date(conv.started_at).getTime()) / 60000)}m` : 'Active'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}

