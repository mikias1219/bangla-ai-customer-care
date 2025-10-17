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
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Fab,
  IconButton,
  LinearProgress,
  FormControlLabel
} from '@mui/material';
import {
  Facebook,
  Instagram,
  WhatsApp,
  Twitter,
  ExpandMore,
  PlayArrow,
  MonetizationOn,
  Support,
  Analytics,
  CloudUpload,
  Message,
  VoiceChat,
  Payment,
  Mic,
  MicOff,
  VolumeUp
} from '@mui/icons-material';
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

  // Voice recording states
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const [recordedAudio, setRecordedAudio] = useState<Blob | null>(null);
  const [generateVoiceResponse, setGenerateVoiceResponse] = useState(false);

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

      // Use the admin endpoint to test the agent's response
      const response = await fetch(`http://bdchatpro.com/api/agent/admin/test/${client.tenant_id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('admin_token') || 'admin_token_2024'}`
        },
        body: JSON.stringify({
          message: testMessage,
          context: {
            business_type: client.business_type,
            client_name: client.business_name
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
    } catch (error: any) {
      setAgentResponse({ error: 'Network error', details: error.message });
    } finally {
      setTestingAgent(false);
    }
  };

  // Voice recording functions
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks: Blob[] = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };

      recorder.onstop = () => {
        const audioBlob = new Blob(chunks, { type: 'audio/wav' });
        setRecordedAudio(audioBlob);

        // Stop all tracks to free up the microphone
        stream.getTracks().forEach(track => track.stop());
      };

      setMediaRecorder(recorder);
      recorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Could not access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop();
      setIsRecording(false);
    }
  };

  const handleTestVoiceAgent = async () => {
    if (!recordedAudio) {
      alert('Please record audio first');
      return;
    }

    setTestingAgent(true);
    setAgentResponse(null);

    try {
      const formData = new FormData();
      formData.append('audio_data', recordedAudio, 'voice_message.wav');
      formData.append('tenant_id', client.tenant_id);
      formData.append('generate_voice_response', generateVoiceResponse.toString());
      formData.append('context', JSON.stringify({
        business_type: client.business_type,
        client_name: client.business_name
      }));

      const response = await fetch(`${(import.meta as any).env?.VITE_API_URL || 'http://bdchatpro.com/api'}/agent/voice/test`, {
        method: 'POST',
        body: formData,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('admin_token')}`
        }
      });

      if (response.ok) {
        const result = await response.json();
        setAgentResponse(result);
      } else {
        setAgentResponse({ error: 'Failed to test voice agent', status: response.status });
      }
    } catch (error: any) {
      setAgentResponse({ error: 'Network error', details: error.message });
    } finally {
      setTestingAgent(false);
    }
  };

  const playAudioResponse = () => {
    if (agentResponse?.audio_response_url) {
      const audio = new Audio(agentResponse.audio_response_url);
      audio.play();
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
        <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
          <Tab label="Client Info" />
          <Tab label="Users" />
          <Tab label="Agent Testing" />
          <Tab label="Usage Guide" />
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
                {/* Voice Recording Section */}
                <Grid item xs={12}>
                  <Card sx={{ mb: 3 }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                        <VoiceChat sx={{ mr: 1 }} />
                        Voice Message Testing
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        Test your AI agent with voice messages. Record audio and get AI responses with language detection.
                      </Typography>

                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                        {!isRecording ? (
                          <Fab
                            color="primary"
                            size="medium"
                            onClick={startRecording}
                            disabled={testingAgent}
                          >
                            <Mic />
                          </Fab>
                        ) : (
                          <Fab
                            color="error"
                            size="medium"
                            onClick={stopRecording}
                          >
                            <MicOff />
                          </Fab>
                        )}

                        <Box sx={{ flexGrow: 1 }}>
                          <Typography variant="body2" color="text.secondary">
                            {isRecording ? 'Recording... Click to stop' : recordedAudio ? 'Audio recorded - ready to test' : 'Click microphone to start recording'}
                          </Typography>
                          {isRecording && <LinearProgress sx={{ mt: 1 }} />}
                        </Box>

                        {recordedAudio && (
                          <IconButton
                            color="primary"
                            onClick={() => {
                              const audio = new Audio(URL.createObjectURL(recordedAudio));
                              audio.play();
                            }}
                          >
                            <PlayArrow />
                          </IconButton>
                        )}
                      </Box>

                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <FormControlLabel
                          control={
                            <input
                              type="checkbox"
                              checked={generateVoiceResponse}
                              onChange={(e) => setGenerateVoiceResponse(e.target.checked)}
                            />
                          }
                          label="Generate voice response"
                        />

                        <Button
                          variant="contained"
                          color="secondary"
                          onClick={handleTestVoiceAgent}
                          disabled={testingAgent || !recordedAudio}
                          startIcon={testingAgent ? <CircularProgress size={20} /> : <VoiceChat />}
                        >
                          {testingAgent ? 'Testing Voice...' : 'Test Voice Agent'}
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Text Message Section */}
                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }}>
                    <Typography variant="body2" color="text.secondary">OR</Typography>
                  </Divider>

                  <Typography variant="h6" gutterBottom>
                    Text Message Testing
                  </Typography>

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
                    startIcon={testingAgent ? <CircularProgress size={20} /> : <Message />}
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
                          {/* Show transcribed text for voice messages */}
                          {agentResponse.transcribed_text && (
                            <Box sx={{ mb: 2, p: 2, bgcolor: 'blue.50', borderRadius: 1 }}>
                              <Typography variant="subtitle2" color="primary" gutterBottom>
                                🎤 Transcribed Voice Message:
                              </Typography>
                              <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
                                "{agentResponse.transcribed_text}"
                              </Typography>
                            </Box>
                          )}

                          <Typography variant="body1" sx={{ mb: 2 }}>
                            {agentResponse.response}
                          </Typography>

                          {/* Voice response playback */}
                          {agentResponse.audio_response_url && (
                            <Box sx={{ mb: 2 }}>
                              <Button
                                variant="outlined"
                                startIcon={<VolumeUp />}
                                onClick={playAudioResponse}
                                size="small"
                              >
                                Play Voice Response
                              </Button>
                            </Box>
                          )}

                          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                            {agentResponse.detected_language && (
                              <Chip
                                label={`Language: ${agentResponse.detected_language === 'bn' ? 'Bengali' : agentResponse.detected_language === 'en' ? 'English' : agentResponse.detected_language === 'banglish' ? 'Banglish' : agentResponse.detected_language}`}
                                size="small"
                                color="info"
                              />
                            )}
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
                            {agentResponse.transcribed_text && (
                              <Chip
                                label="Voice Input"
                                size="small"
                                color="success"
                                icon={<VoiceChat />}
                              />
                            )}
                            {agentResponse.audio_response_url && (
                              <Chip
                                label="Voice Output"
                                size="small"
                                color="warning"
                                icon={<VolumeUp />}
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

      {activeTab === 3 && (
        <Box>
          <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
            How {client.business_name} Uses Bangla AI
          </Typography>

          {/* Quick Start Guide */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <PlayArrow sx={{ mr: 1 }} />
              Quick Start Guide
            </Typography>
            <Stepper orientation="vertical">
              <Step>
                <StepLabel>Connect Social Media Accounts</StepLabel>
                <StepContent>
                  <Typography>Configure Facebook, Instagram, WhatsApp, and Twitter accounts in the Social Media section.</Typography>
                </StepContent>
              </Step>
              <Step>
                <StepLabel>Set Up AI Configuration</StepLabel>
                <StepContent>
                  <Typography>Customize AI responses, language preferences, and business context for accurate replies.</Typography>
                </StepContent>
              </Step>
              <Step>
                <StepLabel>Test AI Agent</StepLabel>
                <StepContent>
                  <Typography>Use the Agent Testing tab to ensure responses work correctly in multiple languages.</Typography>
                </StepContent>
              </Step>
              <Step>
                <StepLabel>Go Live</StepLabel>
                <StepContent>
                  <Typography>Enable auto-replies and start receiving AI-powered customer responses instantly.</Typography>
                </StepContent>
              </Step>
            </Stepper>
          </Paper>

          {/* Features Overview */}
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Message sx={{ mr: 1, color: 'primary.main' }} />
                    <Typography variant="h6">Smart Auto-Replies</Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    AI automatically responds to customer messages on all social media platforms in the customer's language.
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Chip label="Bengali" size="small" color="primary" />
                    <Chip label="English" size="small" color="secondary" />
                    <Chip label="Banglish" size="small" color="info" />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <VoiceChat sx={{ mr: 1, color: 'success.main' }} />
                    <Typography variant="h6">Voice Message Support</Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Handle voice messages with automatic transcription and AI responses in customer's preferred language.
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Chip label="Speech-to-Text" size="small" color="success" />
                    <Chip label="Language Detection" size="small" color="warning" />
                    <Chip label="Voice Replies" size="small" color="error" />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Analytics sx={{ mr: 1, color: 'info.main' }} />
                    <Typography variant="h6">Analytics Dashboard</Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Track customer interactions, response times, and AI performance across all platforms.
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Chip label="Response Rate" size="small" color="info" />
                    <Chip label="Customer Satisfaction" size="small" color="primary" />
                    <Chip label="Usage Reports" size="small" color="secondary" />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Payment sx={{ mr: 1, color: 'warning.main' }} />
                    <Typography variant="h6">Flexible Billing</Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Pay-as-you-go pricing based on AI responses. Start with credits and upgrade as your business grows.
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Chip label="Pay-per-Response" size="small" color="warning" />
                    <Chip label="Auto Top-up" size="small" color="success" />
                    <Chip label="Usage Alerts" size="small" color="error" />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Social Media Integration */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <CloudUpload sx={{ mr: 1 }} />
              Social Media Platforms
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Connect your social media accounts to enable AI-powered customer service across all platforms.
            </Typography>

            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ textAlign: 'center', p: 2 }}>
                  <Facebook sx={{ fontSize: 40, color: '#1877F2', mb: 1 }} />
                  <Typography variant="subtitle2">Facebook</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Messenger & Comments
                  </Typography>
                  <Chip label="Connected" color="success" size="small" sx={{ mt: 1 }} />
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ textAlign: 'center', p: 2 }}>
                  <Instagram sx={{ fontSize: 40, color: '#E4405F', mb: 1 }} />
                  <Typography variant="subtitle2">Instagram</Typography>
                  <Typography variant="body2" color="text.secondary">
                    DMs & Stories
                  </Typography>
                  <Chip label="Setup Required" color="warning" size="small" sx={{ mt: 1 }} />
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ textAlign: 'center', p: 2 }}>
                  <WhatsApp sx={{ fontSize: 40, color: '#25D366', mb: 1 }} />
                  <Typography variant="subtitle2">WhatsApp</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Business API
                  </Typography>
                  <Chip label="Premium" color="primary" size="small" sx={{ mt: 1 }} />
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ textAlign: 'center', p: 2 }}>
                  <Twitter sx={{ fontSize: 40, color: '#1DA1F2', mb: 1 }} />
                  <Typography variant="subtitle2">Twitter/X</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Mentions & DMs
                  </Typography>
                  <Chip label="Available" color="info" size="small" sx={{ mt: 1 }} />
                </Card>
              </Grid>
            </Grid>
          </Paper>

          {/* Billing & Pricing */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <MonetizationOn sx={{ mr: 1 }} />
              Billing & Pricing for {client.business_name}
            </Typography>

            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Card sx={{ border: client.subscription_plan === 'starter' ? '2px solid #1976d2' : '1px solid #e0e0e0' }}>
                  <CardContent>
                    <Typography variant="h6" color="primary" gutterBottom>
                      Starter Plan
                    </Typography>
                    <Typography variant="h4" sx={{ mb: 2 }}>
                      ৳2,500<span style={{ fontSize: '0.8rem' }}>/month</span>
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      Perfect for small businesses starting with AI customer service.
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2">✓ 500 AI Responses/month</Typography>
                      <Typography variant="body2">✓ 2 Social Platforms</Typography>
                      <Typography variant="body2">✓ Basic Analytics</Typography>
                      <Typography variant="body2">✓ Email Support</Typography>
                    </Box>
                    <Button
                      variant={client.subscription_plan === 'starter' ? 'contained' : 'outlined'}
                      fullWidth
                      disabled={client.subscription_plan === 'starter'}
                    >
                      {client.subscription_plan === 'starter' ? 'Current Plan' : 'Upgrade'}
                    </Button>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={4}>
                <Card sx={{ border: client.subscription_plan === 'professional' ? '2px solid #1976d2' : '1px solid #e0e0e0' }}>
                  <CardContent>
                    <Typography variant="h6" color="primary" gutterBottom>
                      Professional
                    </Typography>
                    <Typography variant="h4" sx={{ mb: 2 }}>
                      ৳5,000<span style={{ fontSize: '0.8rem' }}>/month</span>
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      For growing businesses needing advanced AI features.
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2">✓ 2,000 AI Responses/month</Typography>
                      <Typography variant="body2">✓ All Social Platforms</Typography>
                      <Typography variant="body2">✓ Advanced Analytics</Typography>
                      <Typography variant="body2">✓ Priority Support</Typography>
                      <Typography variant="body2">✓ Voice Messages</Typography>
                    </Box>
                    <Button
                      variant={client.subscription_plan === 'professional' ? 'contained' : 'outlined'}
                      fullWidth
                      disabled={client.subscription_plan === 'professional'}
                    >
                      {client.subscription_plan === 'professional' ? 'Current Plan' : 'Upgrade'}
                    </Button>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={4}>
                <Card sx={{ border: client.subscription_plan === 'enterprise' ? '2px solid #1976d2' : '1px solid #e0e0e0' }}>
                  <CardContent>
                    <Typography variant="h6" color="primary" gutterBottom>
                      Enterprise
                    </Typography>
                    <Typography variant="h4" sx={{ mb: 2 }}>
                      ৳10,000<span style={{ fontSize: '0.8rem' }}>/month</span>
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      For large businesses with high-volume customer service needs.
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2">✓ Unlimited AI Responses</Typography>
                      <Typography variant="body2">✓ Custom AI Training</Typography>
                      <Typography variant="body2">✓ White-label Solution</Typography>
                      <Typography variant="body2">✓ 24/7 Phone Support</Typography>
                      <Typography variant="body2">✓ API Access</Typography>
                    </Box>
                    <Button
                      variant={client.subscription_plan === 'enterprise' ? 'contained' : 'outlined'}
                      fullWidth
                      disabled={client.subscription_plan === 'enterprise'}
                    >
                      {client.subscription_plan === 'enterprise' ? 'Current Plan' : 'Contact Sales'}
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            {/* Current Usage */}
            <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="subtitle1" gutterBottom>
                Current Usage for {client.business_name}
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={4}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h6" color="primary">
                      {client.current_month_customers || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Customers This Month
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h6" color="success.main">
                      ৳{client.ai_reply_balance?.toLocaleString() || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      AI Credits Balance
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h6" color="warning.main">
                      {client.monthly_customers_limit || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Monthly Limit
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </Box>
          </Paper>

          {/* Support & Resources */}
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <Support sx={{ mr: 1 }} />
              Support & Resources
            </Typography>

            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography>How do I connect social media accounts?</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography paragraph>
                      Go to Settings → Social Media Integration. Click "Connect" next to each platform and follow the authorization process.
                      You'll need admin access to your business social media accounts.
                    </Typography>
                  </AccordionDetails>
                </Accordion>

                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography>How does language detection work?</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography paragraph>
                      Our AI automatically detects if customers are messaging in Bengali, English, or Banglish (mixed language).
                      It responds in the same language to ensure clear communication.
                    </Typography>
                  </AccordionDetails>
                </Accordion>
              </Grid>

              <Grid item xs={12} md={6}>
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography>What if customers send voice messages?</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography paragraph>
                      Voice messages are automatically transcribed to text, processed by our AI, and responded to in the customer's language.
                      Voice responses can also be generated for supported platforms.
                    </Typography>
                  </AccordionDetails>
                </Accordion>

                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography>How do I top up my AI credits?</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography paragraph>
                      Go to Billing → Add Credits. You can pay via bKash, bank transfer, or credit card.
                      Credits are used per AI response and auto-recharge when low.
                    </Typography>
                  </AccordionDetails>
                </Accordion>
              </Grid>
            </Grid>
          </Paper>
        </Box>
      )}

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
