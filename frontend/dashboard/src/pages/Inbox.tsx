import { useEffect, useState } from 'react'
import { apiBase } from '../lib/api'

interface MessageItem { id: string; channel: 'messenger' | 'whatsapp' | 'instagram'; from: string; text: string; time: string }

export function Inbox() {
  const [tab, setTab] = useState<'messenger' | 'whatsapp' | 'instagram'>('messenger')
  const [messages, setMessages] = useState<MessageItem[]>([])
  const [input, setInput] = useState('')

  useEffect(() => {
    // Placeholder: in real app, fetch from /admin/conversations or channel-specific logs
    setMessages([])
  }, [tab])

  async function sendTest() {
    const endpoint = (tab === 'messenger' || tab === 'instagram')
      ? `${apiBase()}/channels/meta/webhook`
      : `${apiBase()}/channels/whatsapp/webhook`

    // Simulate an incoming message payload for quick testing via backend webhook
    let payload: any
    if (tab === 'whatsapp') {
      payload = {
        entry: [
          {
            changes: [
              {
                value: {
                  messaging_product: 'whatsapp',
                  messages: [
                    { from: 'test-user', id: 'msg1', text: { body: input }, type: 'text' }
                  ]
                }
              }
            ]
          }
        ]
      }
    } else if (tab === 'messenger') {
      payload = {
        entry: [
          {
            messaging: [
              { sender: { id: 'PSID_TEST' }, message: { text: input } }
            ]
          }
        ]
      }
    } else {
      payload = {
        entry: [
          {
            changes: [
              {
                value: {
                  messaging_product: 'instagram',
                  messages: [
                    { from: 'IGID_TEST', text: input }
                  ]
                }
              }
            ]
          }
        ]
      }
    }

    await fetch(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
    setInput('')
  }

  function Tab({ id, label }: { id: 'messenger' | 'whatsapp' | 'instagram'; label: string }) {
    const active = tab === id
    return (
      <button onClick={() => setTab(id)} style={{ padding: '8px 12px', border: '1px solid #e5e7eb', background: active ? '#3b82f6' : '#fff', color: active ? '#fff' : '#111827', borderRadius: 6, marginRight: 8 }}>
        {label}
      </button>
    )
  }

  return (
    <section>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>Inbox</h2>
        <div>
          <Tab id="messenger" label="Messenger" />
          <Tab id="whatsapp" label="WhatsApp" />
          <Tab id="instagram" label="Instagram" />
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '280px 1fr 320px', gap: 16 }}>
        {/* Sidebar: Conversations (placeholder) */}
        <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 8, height: 520, padding: 8 }}>
          <div style={{ fontSize: 12, color: '#6b7280', marginBottom: 8 }}>Conversations</div>
          <div style={{ color: '#9ca3af', fontSize: 13 }}>No conversations yet</div>
        </div>

        {/* Messages */}
        <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 8, height: 520, display: 'flex', flexDirection: 'column' }}>
          <div style={{ flex: 1, padding: 16, overflow: 'auto' }}>
            {messages.length === 0 && <div style={{ color: '#9ca3af', textAlign: 'center', marginTop: 120 }}>No messages yet. Send a test message below.</div>}
          </div>
          <div style={{ padding: 12, borderTop: '1px solid #e5e7eb', display: 'flex', gap: 8 }}>
            <input value={input} onChange={(e) => setInput(e.target.value)} placeholder={`Send a test message to ${tab}`} style={{ flex: 1, padding: 10, border: '1px solid #d1d5db', borderRadius: 6 }} />
            <button onClick={sendTest} style={{ padding: '10px 16px', background: '#3b82f6', color: '#fff', border: 'none', borderRadius: 6 }}>Send</button>
          </div>
        </div>

        {/* Customer pane */}
        <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 8, height: 520, padding: 16 }}>
          <div style={{ fontSize: 12, color: '#6b7280', marginBottom: 8 }}>Customer</div>
          <div style={{ color: '#9ca3af', fontSize: 13 }}>Select a conversation to view details</div>
        </div>
      </div>
    </section>
  )
}
