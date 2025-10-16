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

import { Box, Container, useTheme, useMediaQuery } from '@mui/material'

export default function App() {
  const [page, setPage] = useState<Page>('inbox') // Start with inbox as it's the main messaging interface
  const [drawerOpen, setDrawerOpen] = useState(false)
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))

  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen)
  }

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      <Nav
        current={page}
        onNavigate={setPage}
        open={drawerOpen}
        onToggle={handleDrawerToggle}
        isMobile={isMobile}
      />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          overflow: 'auto',
          ml: isMobile ? 0 : '280px', // No margin on mobile when drawer is overlay
          mt: isMobile ? '64px' : 0, // Account for mobile app bar height
          transition: theme.transitions.create(['margin', 'margin-top'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        }}
      >
        <Container
          maxWidth="xl"
          sx={{
            py: { xs: 1, sm: 2, md: 3 },
            px: { xs: 1, sm: 2, md: 3 }
          }}
        >
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
