import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
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
  Alert
} from '@mui/material';
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

function Dashboard({ onLogout }: { onLogout: () => void }) {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [showCreateClient, setShowCreateClient] = useState(false);

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

  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'business_name', headerName: 'Business Name', width: 200 },
    { field: 'business_email', headerName: 'Email', width: 200 },
    { field: 'business_type', headerName: 'Type', width: 120 },
    { field: 'subscription_plan', headerName: 'Plan', width: 120 },
    { field: 'status', headerName: 'Status', width: 100 },
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
      type: 'number',
      valueFormatter: (params) => `৳${params.value}`
    },
    {
      field: 'created_at',
      headerName: 'Created',
      width: 150,
      valueFormatter: (params) => new Date(params.value).toLocaleDateString()
    },
  ];

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
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Bangla AI Admin Dashboard
          </Typography>
          <Button color="inherit" onClick={() => setShowCreateClient(true)}>
            Add Client
          </Button>
          <Button color="inherit" onClick={onLogout}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Paper sx={{ p: 2, height: 600 }}>
          <Typography variant="h5" gutterBottom>
            Clients ({clients.length})
          </Typography>
          <DataGrid
            rows={clients}
            columns={columns}
            loading={loading}
            pageSize={10}
            rowsPerPageOptions={[10, 25, 50]}
            onRowClick={(params) => setSelectedClient(params.row as Client)}
            sx={{ border: 0 }}
          />
        </Paper>
      </Container>
    </Box>
  );
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    setIsAuthenticated(adminApi.isAuthenticated());
  }, []);

  const handleLogin = (token: string) => {
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
