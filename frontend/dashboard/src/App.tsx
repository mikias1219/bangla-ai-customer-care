import { useState } from 'react'
import { Nav } from './components/Nav'
import { Overview } from './pages/Overview'
import { TestConsole } from './pages/TestConsole'
import { Intents } from './pages/Intents'
import { Entities } from './pages/Entities'
import { Conversations } from './pages/Conversations'
import { Templates } from './pages/Templates'
import { Inbox } from './pages/Inbox'

export type Page = 'overview' | 'test' | 'intents' | 'entities' | 'conversations' | 'templates' | 'inbox'

export default function App() {
  const [page, setPage] = useState<Page>('overview')

  return (
    <div style={{ display: 'flex', minHeight: '100vh', fontFamily: 'system-ui, sans-serif', background: '#f9fafb' }}>
      <Nav current={page} onNavigate={setPage} />
      <main style={{ flex: 1, padding: '24px', maxWidth: 1400, margin: '0 auto', width: '100%' }}>
        {page === 'overview' && <Overview />}
        {page === 'test' && <TestConsole />}
        {page === 'intents' && <Intents />}
        {page === 'entities' && <Entities />}
        {page === 'conversations' && <Conversations />}
        {page === 'templates' && <Templates />}
        {page === 'inbox' && <Inbox />}
      </main>
    </div>
  )
}
