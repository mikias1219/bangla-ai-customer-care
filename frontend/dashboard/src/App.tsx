import { useState } from 'react'
import { Nav } from './components/Nav'
import { Overview } from './pages/Overview'
import { TestConsole } from './pages/TestConsole'
import { Intents } from './pages/Intents'
import { Entities } from './pages/Entities'
import { Conversations } from './pages/Conversations'
import { Templates } from './pages/Templates'
import { Inbox } from './pages/Inbox'
import { Products } from './pages/Products'
import { Orders } from './pages/Orders'
import { Customers } from './pages/Customers'

export type Page = 'overview' | 'test' | 'intents' | 'entities' | 'conversations' | 'templates' | 'inbox' | 'products' | 'orders' | 'customers'

import { Box, Container } from '@mui/material'

export default function App() {
  const [page, setPage] = useState<Page>('inbox') // Start with inbox as it's the main messaging interface

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      <Nav current={page} onNavigate={setPage} />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          overflow: 'auto',
          ml: '280px', // Account for drawer width
        }}
      >
        <Container maxWidth="xl" sx={{ py: 3 }}>
          {page === 'overview' && <Overview />}
          {page === 'test' && <TestConsole />}
          {page === 'intents' && <Intents />}
          {page === 'entities' && <Entities />}
          {page === 'conversations' && <Conversations />}
          {page === 'templates' && <Templates />}
          {page === 'inbox' && <Inbox />}
          {page === 'products' && <Products />}
          {page === 'orders' && <Orders />}
          {page === 'customers' && <Customers />}
        </Container>
      </Box>
    </Box>
  )
}
