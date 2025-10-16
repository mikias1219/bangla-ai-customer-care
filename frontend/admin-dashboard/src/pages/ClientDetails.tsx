import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  Grid,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Divider,
  Tabs,
  Tab,
  CircularProgress
} from '@mui/material';
import { Client, ClientUser, adminApi } from '../lib/api';

interface ClientDetailsProps {
  client: Client;
  onBack: () => void;
  onUpdate: (clientId: number, updates: Partial<Client>) => void;
}

function ClientDetails({ client, onBack, onUpdate }: ClientDetailsProps) {
  const [users, setUsers] = useState<ClientUser[]>([]);
  const [editing, setEditing] = useState(false);
  const [showCreateUser, setShowCreateUser] = useState(false);
  const [formData, setFormData] = useState<Partial<Client>>(client);
  const [userFormData, setUserFormData] = useState({
    username: '',
    email: '',
    password: '',
    full_name: '',
    role: 'admin'
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [activeTab, setActiveTab] = useState(0);

  // Agent testing state
  const [testMessage, setTestMessage] = useState('');
  const [agentResponse, setAgentResponse] = useState<any>(null);
  const [testingAgent, setTestingAgent] = useState(false);

  useEffect(() => {
    loadClientUsers();
  }, [client.id]);

  const loadClientUsers = async () => {
    try {
      const response = await adminApi.getClientUsers(client.id);
      setUsers(response.data);
    } catch (error) {
      console.error('Failed to load client users:', error);
    }
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      await onUpdate(client.id, formData);
      setEditing(false);
      setMessage('Client updated successfully');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Failed to update client');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async () => {
    try {
      setLoading(true);
      await adminApi.createClientUser(client.id, userFormData);
      setShowCreateUser(false);
      setUserFormData({
        username: '',
        email: '',
        password: '',
        full_name: '',
        role: 'admin'
      });
      await loadClientUsers();
      setMessage('User created successfully');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Failed to create user');
    } finally {
      setLoading(false);
    }
  };

  const handleTestAgent = async () => {
    if (!testMessage.trim()) return;

    try {
      setTestingAgent(true);
      setAgentResponse(null);

      // Use the client's tenant ID to test the agent
      const response = await fetch(`http://bdchatpro.com/api/agent/test?tenant_id=${client.tenant_id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Note: In production, you'd need proper authentication
          // For now, this is a demo endpoint
        },
        body: JSON.stringify({
          message: testMessage,
          context: {
            client_name: client.business_name,
            client_type: client.business_type
          },
          language: client.language_preference
        })
      });

      if (response.ok) {
        const result = await response.json();
        setAgentResponse(result);
      } else {
        setAgentResponse({ error: 'Failed to test agent', status: response.status });
      }
    } catch (error) {
      setAgentResponse({ error: 'Network error', details: error.message });
    } finally {
      setTestingAgent(false);
    }
  };

  const handleProcessPayment = async (amount: number, paymentType: string) => {
    try {
      setLoading(true);
      await adminApi.processPayment(client.id, {
        amount,
        payment_type: paymentType,
        gateway: 'manual',
        description: `Manual ${paymentType} payment`
      });
      setMessage(`Payment processed successfully`);
      // Reload client data
      const response = await adminApi.getClient(client.id);
      onUpdate(client.id, response.data);
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Failed to process payment');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 2 }}>
        <Button variant="outlined" onClick={onBack}>
          ← Back to Clients
        </Button>
      </Box>

      {message && (
        <Alert severity={message.includes('success') ? 'success' : 'error'} sx={{ mb: 2 }}>
          {message}
        </Alert>
      )}

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Client Info" />
          <Tab label="Users" />
          <Tab label="Agent Testing" />
        </Tabs>
      </Box>

      {activeTab === 0 && (
        <Grid container spacing={3}>
          {/* Client Info */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h5">
                  {editing ? 'Edit Client' : client.business_name}
                </Typography>
              <Box>
                {!editing ? (
                  <Button variant="outlined" onClick={() => setEditing(true)}>
                    Edit
                  </Button>
                ) : (
                  <>
                    <Button variant="outlined" onClick={() => setEditing(false)} sx={{ mr: 1 }}>
                      Cancel
                    </Button>
                    <Button variant="contained" onClick={handleSave} disabled={loading}>
                      Save
                    </Button>
                  </>
                )}
              </Box>
            </Box>

            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Business Name"
                  value={formData.business_name || ''}
                  onChange={(e) => setFormData({...formData, business_name: e.target.value})}
                  disabled={!editing}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Business Email"
                  value={formData.business_email || ''}
                  onChange={(e) => setFormData({...formData, business_email: e.target.value})}
                  disabled={!editing}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Business Phone"
                  value={formData.business_phone || ''}
                  onChange={(e) => setFormData({...formData, business_phone: e.target.value})}
                  disabled={!editing}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth disabled={!editing}>
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={formData.status || ''}
                    onChange={(e) => setFormData({...formData, status: e.target.value})}
                  >
                    <MenuItem value="trial">Trial</MenuItem>
                    <MenuItem value="active">Active</MenuItem>
                    <MenuItem value="inactive">Inactive</MenuItem>
                    <MenuItem value="suspended">Suspended</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth disabled={!editing}>
                  <InputLabel>Subscription Plan</InputLabel>
                  <Select
                    value={formData.subscription_plan || ''}
                    onChange={(e) => setFormData({...formData, subscription_plan: e.target.value})}
                  >
                    <MenuItem value="pay_as_you_go">Pay as You Go</MenuItem>
                    <MenuItem value="basic">Basic (৳3,999/month)</MenuItem>
                    <MenuItem value="standard">Standard (৳7,499/month)</MenuItem>
                    <MenuItem value="premium">Premium (৳17,999/month)</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Monthly Customer Limit"
                  type="number"
                  value={formData.monthly_customers_limit || ''}
                  onChange={(e) => setFormData({...formData, monthly_customers_limit: parseInt(e.target.value)})}
                  disabled={!editing}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Business Address"
                  multiline
                  rows={2}
                  value={formData.business_address || ''}
                  onChange={(e) => setFormData({...formData, business_address: e.target.value})}
                  disabled={!editing}
                />
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Stats & Actions */}
          <Grid item xs={12} md={4}>
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Account Status
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Chip
                  label={client.status.toUpperCase()}
                  color={client.status === 'active' ? 'success' : 'default'}
                  sx={{ mr: 1 }}
                />
                <Chip
                  label={client.subscription_plan.toUpperCase()}
                  variant="outlined"
                />
              </Box>
              <Typography variant="body2" color="text.secondary">
                AI Balance: ৳{client.ai_reply_balance?.toFixed(2) || '0.00'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Monthly Usage: {client.current_month_customers || 0} / {client.monthly_customers_limit || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Tenant ID: {client.tenant_id}
              </Typography>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => handleProcessPayment(1000, 'topup')}
                  disabled={loading}
                >
                  Add ৳1000 Balance
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => setShowCreateUser(true)}
                >
                  Create User Account
                </Button>
              </Box>
            </CardContent>
          </Card>
          </Grid>
        </Grid>
      )}

      {activeTab === 1 && (
        <Grid container spacing={3}>
          {/* Users */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Users ({users.length})
                </Typography>
                <Button variant="outlined" onClick={() => setShowCreateUser(true)}>
                  Add User
                </Button>
              </Box>
              <List>
                {users.map((user, index) => (
                  <React.Fragment key={user.id}>
                    <ListItem>
                      <ListItemText
                        primary={`${user.full_name || user.username} (${user.email})`}
                        secondary={`Role: ${user.role} | Status: ${user.is_active ? 'Active' : 'Inactive'} | Last Login: ${user.last_login_at ? new Date(user.last_login_at).toLocaleDateString() : 'Never'}`}
                      />
                    </ListItem>
                    {index < users.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </Paper>
          </Grid>
        </Grid>
      )}

      {activeTab === 2 && (
        <Grid container spacing={3}>
          {/* Agent Testing */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                AI Agent Testing for {client.business_name}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Test your AI agent's responses. This is free for all clients to ensure their agents work correctly.
              </Typography>

              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Test Message"
                    multiline
                    rows={3}
                    value={testMessage}
                    onChange={(e) => setTestMessage(e.target.value)}
                    placeholder="Enter a customer message to test your AI agent..."
                    sx={{ mb: 2 }}
                  />
                  <Button
                    variant="contained"
                    onClick={handleTestAgent}
                    disabled={testingAgent || !testMessage.trim()}
                    startIcon={testingAgent ? <CircularProgress size={20} /> : null}
                  >
                    {testingAgent ? 'Testing...' : 'Test Agent'}
                  </Button>
                </Grid>

                {agentResponse && (
                  <Grid item xs={12}>
                    <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                      <Typography variant="h6" gutterBottom>
                        Agent Response
                      </Typography>

                      {agentResponse.error ? (
                        <Alert severity="error">
                          {agentResponse.error}
                          {agentResponse.details && <><br />Details: {agentResponse.details}</>}
                        </Alert>
                      ) : (
                        <Box>
                          <Typography variant="body1" sx={{ mb: 2 }}>
                            {agentResponse.response}
                          </Typography>

                          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                            {agentResponse.intent && (
                              <Chip
                                label={`Intent: ${agentResponse.intent}`}
                                size="small"
                                color="primary"
                              />
                            )}
                            {agentResponse.confidence && (
                              <Chip
                                label={`Confidence: ${(agentResponse.confidence * 100).toFixed(1)}%`}
                                size="small"
                                color="secondary"
                              />
                            )}
                            {agentResponse.tokens_used && (
                              <Chip
                                label={`Tokens: ${agentResponse.tokens_used}`}
                                size="small"
                                variant="outlined"
                              />
                            )}
                          </Box>

                          {agentResponse.entities && Object.keys(agentResponse.entities).length > 0 && (
                            <Box sx={{ mt: 2 }}>
                              <Typography variant="subtitle2" gutterBottom>
                                Extracted Entities:
                              </Typography>
                              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                {Object.entries(agentResponse.entities).map(([key, value]) => (
                                  <Chip
                                    key={key}
                                    label={`${key}: ${value}`}
                                    size="small"
                                    variant="outlined"
                                  />
                                ))}
                              </Box>
                            </Box>
                          )}
                        </Box>
                      )}
                    </Paper>
                  </Grid>
                )}
              </Grid>
            </Paper>
          </Grid>
        </Grid>
      )}
      </Grid>

      {/* Create User Dialog */}
      <Dialog open={showCreateUser} onClose={() => setShowCreateUser(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create User Account</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Username"
                value={userFormData.username}
                onChange={(e) => setUserFormData({...userFormData, username: e.target.value})}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={userFormData.email}
                onChange={(e) => setUserFormData({...userFormData, email: e.target.value})}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Password"
                type="password"
                value={userFormData.password}
                onChange={(e) => setUserFormData({...userFormData, password: e.target.value})}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Role</InputLabel>
                <Select
                  value={userFormData.role}
                  onChange={(e) => setUserFormData({...userFormData, role: e.target.value})}
                >
                  <MenuItem value="admin">Admin</MenuItem>
                  <MenuItem value="manager">Manager</MenuItem>
                  <MenuItem value="agent">Agent</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Full Name"
                value={userFormData.full_name}
                onChange={(e) => setUserFormData({...userFormData, full_name: e.target.value})}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowCreateUser(false)}>Cancel</Button>
          <Button onClick={handleCreateUser} variant="contained" disabled={loading}>
            Create User
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}

export default ClientDetails;
