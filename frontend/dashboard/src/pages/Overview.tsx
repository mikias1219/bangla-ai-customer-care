import { useEffect, useState } from 'react'
import { apiBase } from '../lib/api'
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  Divider,
  useTheme
} from '@mui/material'
import {
  ChatBubbleLeftRightIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  CpuChipIcon as CpuIcon,
  ServerIcon,
  ChartBarIcon,
  UserGroupIcon
} from '@heroicons/react/24/outline'

interface AnalyticsData {
  total_conversations: number
  active_conversations: number
  messages_today: number
  avg_response_time: number
  nlu_accuracy: number
  fallback_rate: number
  channel_breakdown: Record<string, number>
  top_intents: Array<{ intent: string; count: number }>
  system_health: {
    cpu_usage: number
    memory_usage: number
    db_connections: number
    uptime_hours: number
  }
}

export function Overview() {
  const theme = useTheme()
  const [status, setStatus] = useState<string>('loading…')
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadData = async () => {
      try {
        // Load health status
        const healthResponse = await fetch(`${apiBase()}/health`)
        setStatus(`${healthResponse.status} ${healthResponse.statusText}`)

        // Load analytics
        const analyticsResponse = await fetch(`${apiBase()}/admin/analytics/overview`)
        if (analyticsResponse.ok) {
          const data = await analyticsResponse.json()
          setAnalytics(data)
        }
      } catch (error) {
        setStatus('offline')
        console.error('Failed to load overview data:', error)
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [])

  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case 'whatsapp': return '📱'
      case 'messenger': return '💬'
      case 'instagram': return '📸'
      case 'voice': return '📞'
      case 'webchat': return '🌐'
      default: return '💬'
    }
  }

  const getChannelColor = (channel: string) => {
    switch (channel) {
      case 'whatsapp': return '#25d366'
      case 'messenger': return '#0084ff'
      case 'instagram': return '#e4405f'
      case 'voice': return '#10b981'
      case 'webchat': return '#6b7280'
      default: return '#6b7280'
    }
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <LinearProgress sx={{ width: '50%' }} />
      </Box>
    )
  }

  return (
    <Box sx={{ p: 3, maxWidth: '1200px', mx: 'auto' }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 2, color: 'text.primary' }}>
          Dashboard Overview
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Chip
            label={`Backend: ${status}`}
            color={status.includes('200') ? 'success' : 'error'}
            size="small"
          />
          <Typography variant="body2" sx={{ color: 'text.secondary' }}>
            Last updated: {new Date().toLocaleTimeString()}
          </Typography>
        </Box>
      </Box>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 2 }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                    {analytics?.total_conversations || 0}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    Total Conversations
                  </Typography>
                </Box>
                <ChatBubbleLeftRightIcon style={{ width: 32, height: 32, color: theme.palette.primary.main }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 2 }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                    {analytics?.active_conversations || 0}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    Active Now
                  </Typography>
                </Box>
                <ClockIcon style={{ width: 32, height: 32, color: theme.palette.success.main }} />
              </CardContent>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 2 }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'warning.main' }}>
                    {analytics?.messages_today || 0}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    Messages Today
                  </Typography>
                </Box>
                <ChartBarIcon style={{ width: 32, height: 32, color: theme.palette.warning.main }} />
              </CardContent>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 2 }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'info.main' }}>
                    {analytics ? `${analytics.nlu_accuracy * 100}%` : '0%'}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    AI Accuracy
                  </Typography>
                </Box>
                <CpuIcon style={{ width: 32, height: 32, color: theme.palette.info.main }} />
              </CardContent>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Channel Breakdown & System Health */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, borderRadius: 2 }}>
            <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
              Channel Distribution
            </Typography>
            <List>
              {analytics?.channel_breakdown && Object.entries(analytics.channel_breakdown).map(([channel, count]) => (
                <ListItem key={channel} sx={{ px: 0 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                    <Box sx={{ fontSize: '1.5rem', mr: 2 }}>
                      {getChannelIcon(channel)}
                    </Box>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Typography variant="body1" sx={{ textTransform: 'capitalize' }}>
                            {channel}
                          </Typography>
                          <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                            {count}%
                          </Typography>
                        </Box>
                      }
                    />
                    <LinearProgress
                      variant="determinate"
                      value={count}
                      sx={{
                        width: 80,
                        ml: 2,
                        height: 8,
                        borderRadius: 4,
                        bgcolor: 'grey.200',
                        '& .MuiLinearProgress-bar': {
                          bgcolor: getChannelColor(channel),
                          borderRadius: 4
                        }
                      }}
                    />
                  </Box>
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, borderRadius: 2 }}>
            <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
              System Health
            </Typography>
            {analytics?.system_health && (
              <Box sx={{ spaceY: 2 }}>
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">CPU Usage</Typography>
                    <Typography variant="body2">{analytics.system_health.cpu_usage}%</Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={analytics.system_health.cpu_usage}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      bgcolor: 'grey.200',
                      '& .MuiLinearProgress-bar': {
                        bgcolor: analytics.system_health.cpu_usage > 80 ? 'error.main' : 'success.main',
                        borderRadius: 4
                      }
                    }}
                  />
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Memory Usage</Typography>
                    <Typography variant="body2">{analytics.system_health.memory_usage}%</Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={analytics.system_health.memory_usage}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      bgcolor: 'grey.200',
                      '& .MuiLinearProgress-bar': {
                        bgcolor: analytics.system_health.memory_usage > 80 ? 'error.main' : 'warning.main',
                        borderRadius: 4
                      }
                    }}
                  />
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
                  <Typography variant="body2">Database Connections</Typography>
                  <Typography variant="body2">{analytics.system_health.db_connections}</Typography>
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Uptime</Typography>
                  <Typography variant="body2">{analytics.system_health.uptime_hours}h</Typography>
                </Box>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Top Intents */}
      {analytics?.top_intents && analytics.top_intents.length > 0 && (
        <Paper sx={{ p: 3, borderRadius: 2, mt: 3 }}>
          <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
            Top Customer Intents
          </Typography>
          <Grid container spacing={2}>
            {analytics.top_intents.map((intent, index) => (
              <Grid item xs={12} sm={6} md={3} key={intent.intent}>
                <Card sx={{ borderRadius: 2 }}>
                  <CardContent sx={{ p: 2 }}>
                    <Typography variant="body2" sx={{ color: 'text.secondary', mb: 1 }}>
                      #{index + 1} {intent.intent.replace('_', ' ')}
                    </Typography>
                    <Typography variant="h6" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                      {intent.count}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Paper>
      )}
    </Box>
  )
}
