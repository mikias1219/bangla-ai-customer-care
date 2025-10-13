import type { Page } from '../App'

export function Nav({ current, onNavigate }: { current: Page; onNavigate: (p: Page) => void }) {
  const link = (id: Page, label: string) => (
    <button
      onClick={() => onNavigate(id)}
      style={{
        width: '100%',
        textAlign: 'left',
        padding: '10px 12px',
        background: current === id ? '#3b82f6' : 'transparent',
        color: current === id ? '#fff' : '#374151',
        border: 'none',
        cursor: 'pointer',
        borderRadius: 6,
        marginBottom: 4,
        fontWeight: current === id ? 600 : 400
      }}
    >
      {label}
    </button>
  )
  
  const section = (title: string) => (
    <div style={{ fontSize: 11, textTransform: 'uppercase', fontWeight: 700, color: '#9ca3af', margin: '16px 12px 8px', letterSpacing: '0.05em' }}>
      {title}
    </div>
  )
  
  return (
    <aside style={{ width: 240, borderRight: '1px solid #e5e7eb', padding: 12, background: '#fff' }}>
      <h3 style={{ margin: '8px 8px 20px', fontSize: 18, fontWeight: 700 }}>🇧🇩 Bangla AI</h3>
      {section('Inbox')}
      {link('inbox', 'Unified Inbox')}
      {section('Dashboard')}
      {link('overview', 'Overview')}
      {link('test', 'Test Console')}
      {section('NLU Management')}
      {link('intents', 'Intents')}
      {link('entities', 'Entities')}
      {link('templates', 'Templates')}
      {section('Data')}
      {link('conversations', 'Conversations')}
    </aside>
  )
}
