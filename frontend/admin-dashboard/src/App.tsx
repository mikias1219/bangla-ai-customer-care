import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Box,
  AppBar,
  Toolbar,
  Typography,
  Button,
  Container,
  Paper,
  TextField,
  Alert,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Divider,
  Avatar,
  Menu,
  MenuItem,
  IconButton,
  Badge,
  Card,
  CardContent,
  Grid,
  Chip
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  Payment as PaymentIcon,
  Message as MessageIcon,
  Business as BusinessIcon,
  Analytics as AnalyticsIcon,
  Logout as LogoutIcon,
  Menu as MenuIcon,
  Facebook,
  Instagram,
  Twitter,
  WhatsApp,
  AttachMoney,
  TrendingUp,
  AccountBalance
} from '@mui/icons-material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { adminApi, Client } from './lib/api';
import ClientDetails from './pages/ClientDetails';
import CreateClient from './pages/CreateClient';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function LoginPage({ onLogin }: { onLogin: (token: string) => void }) {
  const [token, setToken] = useState('');
  const [error, setError] = useState('');

  const handleLogin = () => {
    if (token === 'admin_token_2024') { // Simple token check
      adminApi.login(token);
      onLogin(token);
    } else {
      setError('Invalid admin token');
    }
  };

  return (
    <Container maxWidth="sm">
      <Paper elevation={3} sx={{ p: 4, mt: 8 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Admin Login
        </Typography>
        <Typography variant="body1" sx={{ mb: 3 }} align="center" color="text.secondary">
          Enter your admin token to access the dashboard
        </Typography>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        <TextField
          fullWidth
          label="Admin Token"
          type="password"
          value={token}
          onChange={(e) => setToken(e.target.value)}
          sx={{ mb: 2 }}
        />
        <Button
          fullWidth
          variant="contained"
          size="large"
          onClick={handleLogin}
        >
          Login
        </Button>
      </Paper>
    </Container>
  );
}

// Sidebar navigation items
const drawerWidth = 280;

interface SidebarItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  badge?: number;
}

const sidebarItems: SidebarItem[] = [
  { id: 'dashboard', label: 'Dashboard', icon: <DashboardIcon /> },
  { id: 'clients', label: 'Client Management', icon: <PeopleIcon /> },
  { id: 'payments', label: 'Payments & Billing', icon: <PaymentIcon /> },
  { id: 'social-media', label: 'Social Media', icon: <MessageIcon /> },
  { id: 'analytics', label: 'Analytics', icon: <AnalyticsIcon /> },
  { id: 'business', label: 'Business Setup', icon: <BusinessIcon /> },
];

function Dashboard({ onLogout }: { onLogout: () => void }) {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [showCreateClient, setShowCreateClient] = useState(false);
  const [activeSection, setActiveSection] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  useEffect(() => {
    loadClients();
  }, []);

  const loadClients = async () => {
    try {
      const response = await adminApi.getClients();
      setClients(response.data);
    } catch (error) {
      console.error('Failed to load clients:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClientUpdate = async (clientId: number, updates: Partial<Client>) => {
    try {
      await adminApi.updateClient(clientId, updates);
      await loadClients();
    } catch (error) {
      console.error('Failed to update client:', error);
    }
  };

  const totalRevenue = clients.reduce((sum, client) => sum + (client.ai_reply_balance || 0), 0);
  const activeClients = clients.filter(client => client.status === 'active').length;
  const totalCustomers = clients.reduce((sum, client) => sum + (client.current_month_customers || 0), 0);

  const renderDashboardContent = () => {
    switch (activeSection) {
      case 'dashboard':
        return (
          <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            {/* Overview Cards */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Box>
                        <Typography color="textSecondary" gutterBottom>
                          Total Clients
                        </Typography>
                        <Typography variant="h4" component="div">
                          {clients.length}
                        </Typography>
                      </Box>
                      <PeopleIcon sx={{ fontSize: 40, color: 'primary.main' }} />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Box>
                        <Typography color="textSecondary" gutterBottom>
                          Active Clients
                        </Typography>
                        <Typography variant="h4" component="div">
                          {activeClients}
                        </Typography>
                      </Box>
                      <BusinessIcon sx={{ fontSize: 40, color: 'success.main' }} />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Box>
                        <Typography color="textSecondary" gutterBottom>
                          Total Revenue
                        </Typography>
                        <Typography variant="h4" component="div">
                          ৳{totalRevenue.toLocaleString()}
                        </Typography>
                      </Box>
                      <AttachMoney sx={{ fontSize: 40, color: 'warning.main' }} />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Box>
                        <Typography color="textSecondary" gutterBottom>
                          Total Customers
                        </Typography>
                        <Typography variant="h4" component="div">
                          {totalCustomers}
                        </Typography>
                      </Box>
                      <TrendingUp sx={{ fontSize: 40, color: 'info.main' }} />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            {/* Recent Clients */}
            <Paper sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Recent Clients
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<PeopleIcon />}
                  onClick={() => setShowCreateClient(true)}
                >
                  Add New Client
                </Button>
              </Box>
              <Box sx={{ height: 400 }}>
                <DataGrid
                  rows={clients.slice(0, 10)}
                  columns={[
                    { field: 'business_name', headerName: 'Business Name', width: 200 },
                    { field: 'business_type', headerName: 'Type', width: 120 },
                    {
                      field: 'status',
                      headerName: 'Status',
                      width: 100,
                      renderCell: (params) => (
                        <Chip
                          label={params.value}
                          color={params.value === 'active' ? 'success' : 'default'}
                          size="small"
                        />
                      )
                    },
                    {
                      field: 'subscription_plan',
                      headerName: 'Plan',
                      width: 120,
                      renderCell: (params) => (
                        <Chip
                          label={params.value}
                          color="primary"
                          size="small"
                          variant="outlined"
                        />
                      )
                    },
                    {
                      field: 'ai_reply_balance',
                      headerName: 'AI Balance',
                      width: 120,
                      renderCell: (params) => (
                        <Typography>৳{params.value?.toLocaleString() || 0}</Typography>
                      )
                    },
                  ]}
                  loading={loading}
                  onRowClick={(params) => setSelectedClient(params.row as Client)}
                  sx={{ border: 0 }}
                />
              </Box>
            </Paper>
          </Container>
        );

      case 'clients':
        const columns: GridColDef[] = [
          { field: 'id', headerName: 'ID', width: 70 },
          { field: 'business_name', headerName: 'Business Name', width: 200 },
          { field: 'business_email', headerName: 'Email', width: 200 },
          { field: 'business_type', headerName: 'Type', width: 120 },
          {
            field: 'subscription_plan',
            headerName: 'Plan',
            width: 120,
            renderCell: (params) => (
              <Chip
                label={params.value}
                color="primary"
                size="small"
                variant="outlined"
              />
            )
          },
          {
            field: 'status',
            headerName: 'Status',
            width: 100,
            renderCell: (params) => (
              <Chip
                label={params.value}
                color={params.value === 'active' ? 'success' : 'default'}
                size="small"
              />
            )
          },
          {
            field: 'monthly_customers_limit',
            headerName: 'Monthly Limit',
            width: 120,
            type: 'number'
          },
          {
            field: 'current_month_customers',
            headerName: 'Current',
            width: 100,
            type: 'number'
          },
          {
            field: 'ai_reply_balance',
            headerName: 'AI Balance',
            width: 100,
            renderCell: (params) => (
              <Typography>৳{params.value?.toLocaleString() || 0}</Typography>
            )
          },
          {
            field: 'created_at',
            headerName: 'Created',
            width: 150,
            valueFormatter: (params: any) => new Date(params.value as string).toLocaleDateString()
          },
        ];

        return (
          <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Paper sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h5">
                  Client Management ({clients.length} clients)
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<PeopleIcon />}
                  onClick={() => setShowCreateClient(true)}
                >
                  Add New Client
                </Button>
              </Box>
              <Box sx={{ height: 600 }}>
                <DataGrid
                  rows={clients}
                  columns={columns}
                  loading={loading}
                  initialState={{
                    pagination: {
                      paginationModel: { page: 0, pageSize: 10 },
                    },
                  }}
                  pageSizeOptions={[10, 25, 50]}
                  onRowClick={(params) => setSelectedClient(params.row as Client)}
                  sx={{ border: 0 }}
                />
              </Box>
            </Paper>
          </Container>
        );

      case 'payments':
        return (
          <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h5" gutterBottom>
              Payment & Billing Management
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={8}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Recent Payments
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Payment management interface coming soon...
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} md={4}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Revenue Summary
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <AccountBalance sx={{ mr: 1, color: 'success.main' }} />
                    <Typography variant="h4">৳{totalRevenue.toLocaleString()}</Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    Total AI credits sold
                  </Typography>
                </Paper>
              </Grid>
            </Grid>
          </Container>
        );

      case 'social-media':
        return (
          <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h5" gutterBottom>
              Social Media Integration
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <Facebook sx={{ mr: 1, color: '#1877F2' }} />
                    Facebook Integration
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Connect Facebook pages for automated AI responses to customer messages.
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Chip label="Auto Reply" color="primary" size="small" />
                    <Chip label="Language Detection" color="secondary" size="small" />
                    <Chip label="Voice Messages" color="info" size="small" />
                  </Box>
                </Paper>
              </Grid>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <Instagram sx={{ mr: 1, color: '#E4405F' }} />
                    Instagram Integration
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Handle Instagram DMs with intelligent AI responses in customer's language.
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Chip label="DM Automation" color="primary" size="small" />
                    <Chip label="Story Responses" color="secondary" size="small" />
                    <Chip label="Multi-language" color="info" size="small" />
                  </Box>
                </Paper>
              </Grid>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <WhatsApp sx={{ mr: 1, color: '#25D366' }} />
                    WhatsApp Business
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Professional WhatsApp Business API integration for customer support.
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Chip label="Business API" color="primary" size="small" />
                    <Chip label="24/7 Support" color="secondary" size="small" />
                    <Chip label="Voice & Text" color="info" size="small" />
                  </Box>
                </Paper>
              </Grid>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <Twitter sx={{ mr: 1, color: '#1DA1F2' }} />
                    Twitter/X Integration
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Automated responses to mentions and DMs on Twitter/X platform.
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Chip label="Mention Replies" color="primary" size="small" />
                    <Chip label="DM Handling" color="secondary" size="small" />
                    <Chip label="Hashtag Monitoring" color="info" size="small" />
                  </Box>
                </Paper>
              </Grid>
            </Grid>
          </Container>
        );

      case 'analytics':
        return (
          <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h5" gutterBottom>
              Analytics & Insights
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Usage Analytics
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Detailed analytics dashboard coming soon...
                  </Typography>
                </Paper>
              </Grid>
            </Grid>
          </Container>
        );

      case 'business':
        return (
          <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h5" gutterBottom>
              Business Setup & Configuration
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Business Configuration
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Business setup and configuration interface coming soon...
                  </Typography>
                </Paper>
              </Grid>
            </Grid>
          </Container>
        );

      default:
        return null;
    }
  };

  if (selectedClient) {
    return (
      <ClientDetails
        client={selectedClient}
        onBack={() => setSelectedClient(null)}
        onUpdate={handleClientUpdate}
      />
    );
  }

  if (showCreateClient) {
    return (
      <CreateClient
        onBack={() => setShowCreateClient(false)}
        onCreated={loadClients}
      />
    );
  }

  return (
    <Box sx={{ display: 'flex' }}>
      {/* App Bar */}
      <AppBar position="fixed" sx={{ zIndex: theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Bangla AI Admin Dashboard
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Badge badgeContent={clients.filter(c => c.status === 'trial').length} color="warning">
              <Button color="inherit" size="small">
                Trials
              </Button>
            </Badge>
            <IconButton
              color="inherit"
              onClick={(e) => setAnchorEl(e.currentTarget)}
            >
              <Avatar sx={{ width: 32, height: 32 }}>A</Avatar>
            </IconButton>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={() => setAnchorEl(null)}
            >
              <MenuItem onClick={onLogout}>
                <ListItemIcon>
                  <LogoutIcon fontSize="small" />
                </ListItemIcon>
                Logout
              </MenuItem>
            </Menu>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Sidebar */}
      <Drawer
        variant="persistent"
        anchor="left"
        open={sidebarOpen}
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            top: '64px',
            height: 'calc(100% - 64px)',
          },
        }}
      >
        <List>
          {sidebarItems.map((item) => (
            <ListItem key={item.id} disablePadding>
              <ListItemButton
                selected={activeSection === item.id}
                onClick={() => setActiveSection(item.id)}
              >
                <ListItemIcon>
                  {item.badge ? (
                    <Badge badgeContent={item.badge} color="error">
                      {item.icon}
                    </Badge>
                  ) : (
                    item.icon
                  )}
                </ListItemIcon>
                <ListItemText primary={item.label} />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
        <Divider />
        <Box sx={{ p: 2 }}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Quick Stats
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2">Active Clients</Typography>
              <Typography variant="body2" fontWeight="bold">{activeClients}</Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2">Revenue</Typography>
              <Typography variant="body2" fontWeight="bold">৳{totalRevenue.toLocaleString()}</Typography>
            </Box>
          </Box>
        </Box>
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 0,
          marginLeft: sidebarOpen ? `${drawerWidth}px` : 0,
          transition: theme.transitions.create('margin', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        }}
      >
        <Toolbar /> {/* Spacer for AppBar */}
        {renderDashboardContent()}
      </Box>
    </Box>
  );
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    setIsAuthenticated(adminApi.isAuthenticated());
  }, []);

  const handleLogin = (_token: string) => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    adminApi.logout();
    setIsAuthenticated(false);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route
            path="/"
            element={
              isAuthenticated ? (
                <Dashboard onLogout={handleLogout} />
              ) : (
                <LoginPage onLogin={handleLogin} />
              )
            }
          />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
