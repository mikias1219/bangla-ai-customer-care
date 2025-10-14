import type { Page } from '../App'
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Box,
  Typography,
  Avatar,
  Chip,
  useTheme
} from '@mui/material'
import {
  Inbox as InboxIcon,
  BarChart as ChartBarIcon,
  Build as WrenchScrewdriverIcon,
  ShoppingCart as ShoppingBagIcon,
  Receipt as ClipboardDocumentListIcon,
  People as UsersIcon,
  Chat as ChatBubbleLeftRightIcon,
  Label as TagIcon,
  Description as DocumentTextIcon,
  TableChart as TableCellsIcon
} from '@mui/icons-material'

const DRAWER_WIDTH = 280

export function Nav({ current, onNavigate }: { current: Page; onNavigate: (p: Page) => void }) {
  const theme = useTheme()

  const menuItems = [
    { id: 'inbox' as Page, label: 'Unified Inbox', icon: <InboxIcon />, section: 'Inbox' },
    { id: 'overview' as Page, label: 'Overview', icon: <ChartBarIcon />, section: 'Dashboard' },
    { id: 'test' as Page, label: 'Test Console', icon: <WrenchScrewdriverIcon />, section: 'Dashboard' },
    { id: 'products' as Page, label: 'Products', icon: <ShoppingBagIcon />, section: 'E-Commerce' },
    { id: 'orders' as Page, label: 'Orders', icon: <ClipboardDocumentListIcon />, section: 'E-Commerce' },
    { id: 'customers' as Page, label: 'Customers', icon: <UsersIcon />, section: 'E-Commerce' },
    { id: 'intents' as Page, label: 'Intents', icon: <ChatBubbleLeftRightIcon />, section: 'AI Training' },
    { id: 'entities' as Page, label: 'Entities', icon: <TagIcon />, section: 'AI Training' },
    { id: 'templates' as Page, label: 'Templates', icon: <DocumentTextIcon />, section: 'AI Training' },
    { id: 'conversations' as Page, label: 'Conversations', icon: <TableCellsIcon />, section: 'Data' }
  ]

  const sections = ['Inbox', 'Dashboard', 'E-Commerce', 'AI Training', 'Data']

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: DRAWER_WIDTH,
          boxSizing: 'border-box',
          borderRight: `1px solid ${theme.palette.divider}`,
          background: theme.palette.background.paper,
        },
      }}
    >
      {/* Header */}
      <Box sx={{ p: 3, borderBottom: `1px solid ${theme.palette.divider}` }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Avatar
            sx={{
              bgcolor: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
              width: 40,
              height: 40
            }}
          >
            🇧🇩
          </Avatar>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 'bold', color: theme.palette.text.primary, mb: 0.5 }}>
              Bangla AI
            </Typography>
            <Typography variant="caption" sx={{ color: theme.palette.text.secondary }}>
              Customer Service
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Navigation */}
      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
        {sections.map((sectionName) => {
          const sectionItems = menuItems.filter(item => item.section === sectionName)

          return (
            <Box key={sectionName} sx={{ mb: 3 }}>
              <Typography
                variant="overline"
                sx={{
                  px: 1.5,
                  py: 1,
                  color: theme.palette.text.secondary,
                  fontWeight: 'bold',
                  letterSpacing: '0.08em'
                }}
              >
                {sectionName}
              </Typography>
              <List dense>
                {sectionItems.map((item) => (
                  <ListItem key={item.id} disablePadding>
                    <ListItemButton
                      selected={current === item.id}
                      onClick={() => onNavigate(item.id)}
                      sx={{
                        borderRadius: 2,
                        mx: 1,
                        mb: 0.5,
                        '&.Mui-selected': {
                          bgcolor: theme.palette.primary.light,
                          color: theme.palette.primary.main,
                          borderRight: `3px solid ${theme.palette.primary.main}`,
                          '&:hover': {
                            bgcolor: theme.palette.primary.light,
                          },
                        },
                      }}
                    >
                      <ListItemIcon sx={{ minWidth: 40 }}>
                        {item.icon}
                      </ListItemIcon>
                      <ListItemText
                        primary={item.label}
                        primaryTypographyProps={{
                          fontWeight: current === item.id ? 600 : 400,
                          fontSize: '0.9rem'
                        }}
                      />
                    </ListItemButton>
                  </ListItem>
                ))}
              </List>
            </Box>
          )
        })}
      </Box>

      {/* Footer */}
      <Divider />
      <Box sx={{ p: 2 }}>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 2,
            p: 2,
            bgcolor: theme.palette.grey[50],
            borderRadius: 2,
          }}
        >
          <Box
            sx={{
              width: 32,
              height: 32,
              bgcolor: theme.palette.success.light,
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Box
              sx={{
                width: 12,
                height: 12,
                bgcolor: theme.palette.success.main,
                borderRadius: '50%',
                animation: 'pulse 2s infinite',
              }}
            />
          </Box>
          <Box>
            <Typography variant="body2" sx={{ fontWeight: 600, color: theme.palette.text.primary, lineHeight: 1.2 }}>
              AI Online
            </Typography>
            <Typography variant="caption" sx={{ color: theme.palette.text.secondary, lineHeight: 1.2 }}>
              Ready to help
            </Typography>
          </Box>
        </Box>
      </Box>
    </Drawer>
  )
}
