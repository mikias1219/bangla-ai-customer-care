import { useEffect, useState, useRef } from 'react'
import type { ChangeEvent, KeyboardEvent } from 'react'
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Avatar,
  Chip,
  IconButton,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  ListItemButton,
  InputAdornment,
  Badge,
  Card,
  CardContent,
  useTheme,
  useMediaQuery,
  Drawer,
  alpha,
  CircularProgress
} from '@mui/material'
import {
  Send as SendIcon,
  Phone as PhoneIcon,
  Videocam as VideocamIcon,
  Info as InfoIcon,
  Search as SearchIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  AccessTime as AccessTimeIcon,
  Chat as ChatBubbleLeftRightIcon,
  Menu as MenuIcon,
  ArrowBack as ArrowBackIcon,
  Facebook as FacebookIcon,
  WhatsApp as WhatsAppIcon,
  Instagram as InstagramIcon
} from '@mui/icons-material'

// Helper function to format time
const formatTime = (date: Date) => {
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

interface Message {
  id: number
  turn_index: number
  speaker: 'user' | 'bot' | 'agent'
  text: string
  text_language?: string
  intent?: string
  entities?: Record<string, any>
  asr_confidence?: number
  nlu_confidence?: number
  handoff_flag: boolean
  timestamp: string
  turn_metadata?: Record<string, any>
}

interface Conversation {
  id: number
  conversation_id: string
  channel: string
  customer_id?: string
  customer_name?: string
  customer_language: string
  status: 'active' | 'completed' | 'escalated'
  started_at: string
  ended_at?: string
  last_message_at?: string
  unread_count: number
  conversation_metadata?: Record<string, any>
  turns?: Message[]
}

// Add CSS animations
const globalStyles = `
  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;

export function Inbox() {
  const [activeChannel, setActiveChannel] = useState<'messenger' | 'whatsapp' | 'instagram'>('messenger')
  const [messages, setMessages] = useState<Message[]>([])
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [activeConversation, setActiveConversation] = useState<string | null>(null)
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [infoOpen, setInfoOpen] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const isTablet = useMediaQuery(theme.breakpoints.down('lg'))

  // Fetch conversations from backend
  const fetchConversations = async (channel?: string) => {
    try {
      const params = new URLSearchParams()
      if (channel) params.append('channel', channel)
      params.append('limit', '50')

      const response = await fetch(`/api/conversations?${params}`)
      if (!response.ok) throw new Error('Failed to fetch conversations')

      const data: Conversation[] = await response.json()
      setConversations(data)

      // Auto-select first conversation if none selected
      if (!activeConversation && data.length > 0) {
        setActiveConversation(data[0].id.toString())
      }
    } catch (error) {
      console.error('Error fetching conversations:', error)
      // Keep existing conversations or show empty state
    }
  }

  // Fetch conversation details including turns
  const fetchConversationDetails = async (conversationId: number) => {
    try {
      const response = await fetch(`/api/conversations/${conversationId}`)
      if (!response.ok) throw new Error('Failed to fetch conversation details')

      const data: Conversation = await response.json()
      if (data.turns) {
        setMessages(data.turns)
      }
    } catch (error) {
      console.error('Error fetching conversation details:', error)
    }
  }

  useEffect(() => {
    fetchConversations(activeChannel)
  }, [activeChannel])

  useEffect(() => {
    if (activeConversation) {
      fetchConversationDetails(parseInt(activeConversation))
    }
  }, [activeConversation])

  // Inject global styles for animations
  useEffect(() => {
    const styleSheet = document.createElement('style');
    styleSheet.type = 'text/css';
    styleSheet.innerText = globalStyles;
    document.head.appendChild(styleSheet);

    return () => {
      document.head.removeChild(styleSheet);
    };
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  async function sendMessage() {
    if (!input.trim() || !activeConversation) return

    const userText = input
    const tempMessage: Message = {
      id: -1, // Temporary ID
      turn_index: messages.length,
      text: userText,
      speaker: 'user',
      text_language: 'en', // Will be detected by backend
      handoff_flag: false,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, tempMessage])
    setInput('')
    setIsTyping(true)

    try {
      // Call backend NLU API for processing
      const response = await fetch('/api/nlu/resolve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: userText,
          context: {
            channel: activeChannel,
            conversation_id: activeConversation
          }
        })
      })

      if (!response.ok) {
        throw new Error(`Backend API error: ${response.status}`)
      }

      const nluResult = await response.json()

      // Call dialogue manager for response
      const dmResponse = await fetch('/api/dm/decide', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          intent: nluResult.intent,
          entities: nluResult.entities,
          context: {
            channel: activeChannel,
            customer_id: activeConversation,
            message: userText,
            language: nluResult.language
          }
        })
      })

      if (!dmResponse.ok) {
        throw new Error(`Dialogue API error: ${dmResponse.status}`)
      }

      const dmResult = await dmResponse.json()

      const botMessage: Message = {
        id: -2, // Temporary ID
        turn_index: messages.length + 1,
        text: dmResult.response_text || 'I apologize, but I cannot help you right now. Please try again.',
        speaker: 'bot',
        text_language: dmResult.language || 'en',
        intent: nluResult.intent,
        entities: nluResult.entities,
        nlu_confidence: nluResult.confidence,
        handoff_flag: dmResult.action === 'handoff',
        timestamp: new Date().toISOString(),
        turn_metadata: dmResult.metadata
      }

      setMessages(prev => [...prev, botMessage])

      // Refresh conversations to update last message
      fetchConversations(activeChannel)

    } catch (error) {
      console.error('Error sending message:', error)

      // Fallback response if backend fails
      const errorMessage: Message = {
        id: -3,
        turn_index: messages.length + 1,
        text: 'Sorry, there was an issue connecting to the server. Please try again later.',
        speaker: 'bot',
        text_language: 'en',
        handoff_flag: false,
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsTyping(false)
    }
  }

  const getChannelColor = (channel: string) => {
    switch (channel) {
      case 'whatsapp':
        return theme.palette.whatsapp?.main || '#25d366'
      case 'messenger':
        return theme.palette.facebook?.main || '#1877f2'
      case 'instagram':
        return theme.palette.instagram?.main || '#e4405f'
      default:
        return theme.palette.grey[500]
    }
  }

  const ConversationsSidebar = () => (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Search */}
      <Box sx={{ p: 2, borderBottom: `1px solid ${theme.palette.divider}` }}>
        <TextField
          fullWidth
          placeholder="Search conversations..."
          variant="outlined"
          size="small"
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon sx={{ color: 'text.secondary' }} />
              </InputAdornment>
            ),
          }}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 2,
            }
          }}
        />
      </Box>

      {/* Conversations list */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        <List dense>
          {conversations.map((conversation) => (
            <ListItem key={conversation.id} disablePadding>
                <ListItemButton
                  selected={activeConversation === conversation.id.toString()}
                  onClick={() => {
                    setActiveConversation(conversation.id.toString())
                    if (isMobile) setSidebarOpen(false)
                  }}
                  sx={{
                    py: 2,
                    px: 2,
                    '&.Mui-selected': {
                      bgcolor: alpha(theme.palette.primary.main, 0.08),
                      borderRight: `3px solid ${theme.palette.primary.main}`,
                    },
                  }}
                >
                  <ListItemAvatar>
                    <Badge
                      color="error"
                      badgeContent={conversation.unread_count}
                      invisible={conversation.unread_count === 0}
                    >
                      <Avatar
                        sx={{
                          bgcolor: getChannelColor(conversation.channel),
                          width: 40,
                          height: 40
                        }}
                      >
                        {conversation.customer_name?.charAt(0).toUpperCase() || conversation.customer_id?.charAt(0).toUpperCase() || '?'}
                      </Avatar>
                    </Badge>
                  </ListItemAvatar>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 0.5 }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'text.primary' }}>
                          {conversation.customer_name || conversation.customer_id || 'Unknown Customer'}
                        </Typography>
                        <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                          {conversation.last_message_at ? formatTime(new Date(conversation.last_message_at)) : formatTime(new Date(conversation.started_at))}
                        </Typography>
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography
                          variant="body2"
                          sx={{
                            color: 'text.secondary',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                            mb: 1
                          }}
                        >
                          {conversation.conversation_metadata?.last_message || 'No messages yet'}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Chip
                            label={conversation.channel}
                            size="small"
                            variant="outlined"
                            sx={{ height: 20, fontSize: '0.7rem' }}
                          />
                          <Chip
                            label={conversation.customer_language.toUpperCase()}
                            size="small"
                            variant="outlined"
                            sx={{ height: 20, fontSize: '0.7rem' }}
                          />
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            {conversation.status === 'active' && (
                              <AccessTimeIcon sx={{ fontSize: 12, color: 'warning.main' }} />
                            )}
                            {conversation.status === 'completed' && (
                              <CheckCircleIcon sx={{ fontSize: 12, color: 'success.main' }} />
                            )}
                            {conversation.status === 'escalated' && (
                              <ErrorIcon sx={{ fontSize: 12, color: 'error.main' }} />
                            )}
                          </Box>
                        </Box>
                      </Box>
                    }
                  />
                </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Box>
    </Box>
  )

  return (
    <Box sx={{ height: { xs: 'calc(100vh - 64px)', md: '100%' }, display: 'flex', flexDirection: 'column', bgcolor: 'background.default' }}>
      {/* Header */}
      <Paper
        elevation={0}
        sx={{
          borderBottom: `1px solid ${theme.palette.divider}`,
          px: { xs: 2, md: 3 },
          py: 2,
          borderRadius: 0
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {isMobile && !activeConversation && (
              <IconButton onClick={() => setSidebarOpen(true)}>
                <MenuIcon />
              </IconButton>
            )}
            {isMobile && activeConversation && (
              <IconButton onClick={() => setActiveConversation(null)}>
                <ArrowBackIcon />
              </IconButton>
            )}
            <Box>
              <Typography variant={isMobile ? 'h5' : 'h4'} sx={{ fontWeight: 'bold', color: 'text.primary', mb: 0.5 }}>
                Inbox
              </Typography>
              {!isMobile && (
                <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                  AI-powered multilingual support
                </Typography>
              )}
            </Box>
          </Box>

          {/* Channel tabs */}
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {[
              { id: 'messenger' as const, label: isMobile ? 'FB' : 'Messenger', color: getChannelColor('messenger'), icon: FacebookIcon },
              { id: 'whatsapp' as const, label: isMobile ? 'WA' : 'WhatsApp', color: getChannelColor('whatsapp'), icon: WhatsAppIcon },
              { id: 'instagram' as const, label: isMobile ? 'IG' : 'Instagram', color: getChannelColor('instagram'), icon: InstagramIcon }
            ].map(({ id, label, color, icon: Icon }) => (
              <Button
                key={id}
                onClick={() => setActiveChannel(id)}
                variant={activeChannel === id ? 'contained' : 'outlined'}
                startIcon={!isMobile && <Icon sx={{ fontSize: '1.2rem' }} />}
                size={isMobile ? 'small' : 'medium'}
                sx={{
                  borderRadius: 3,
                  textTransform: 'none',
                  fontWeight: 600,
                  minWidth: isMobile ? 50 : 120,
                  py: 1.5,
                  px: 2,
                  boxShadow: activeChannel === id ? '0 2px 8px rgba(0,0,0,0.15)' : 'none',
                  transition: 'all 0.2s ease-in-out',
                  ...(activeChannel === id && {
                    backgroundColor: color,
                    borderColor: color,
                    color: 'white',
                    transform: 'translateY(-1px)',
                    '&:hover': {
                      backgroundColor: alpha(color, 0.9),
                      transform: 'translateY(-1px)',
                      boxShadow: '0 4px 12px rgba(0,0,0,0.2)'
                    }
                  }),
                  '&:hover': {
                    transform: 'translateY(-1px)',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                  }
                }}
              >
                {label}
              </Button>
            ))}
          </Box>
        </Box>
      </Paper>

      {/* Main content */}
      <Box sx={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {/* Conversations sidebar - Desktop */}
        {!isMobile && (
          <Paper
            elevation={0}
            sx={{
              width: 320,
              borderRight: `1px solid ${theme.palette.divider}`,
              borderRadius: 0,
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            <ConversationsSidebar />
          </Paper>
        )}

        {/* Conversations sidebar - Mobile Drawer */}
        {isMobile && (
          <Drawer
            anchor="left"
            open={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
            sx={{
              '& .MuiDrawer-paper': {
                width: 280,
                boxSizing: 'border-box',
              },
            }}
          >
            <ConversationsSidebar />
          </Drawer>
        )}

        {/* Chat area */}
        <Box sx={{ 
          flex: 1, 
          display: (!isMobile || activeConversation) ? 'flex' : 'none', 
          flexDirection: 'column', 
          bgcolor: 'background.paper' 
        }}>
          {activeConversation ? (
            <>
              {/* Chat header */}
              <Paper
                elevation={0}
                sx={{
                  borderBottom: `1px solid ${theme.palette.divider}`,
                  px: { xs: 2, md: 3 },
                  py: 2,
                  borderRadius: 0,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between'
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  {(() => {
                    const activeConv = conversations.find(c => c.id.toString() === activeConversation)
                    return (
                      <>
                        <Avatar
                          sx={{
                            bgcolor: getChannelColor(activeConv?.channel || activeChannel),
                            width: 40,
                            height: 40
                          }}
                        >
                          {activeConv?.customer_name?.charAt(0).toUpperCase() ||
                           activeConv?.customer_id?.charAt(0).toUpperCase() || '?'}
                        </Avatar>
                        <Box>
                          <Typography variant="h6" sx={{ fontWeight: 600, color: 'text.primary' }}>
                            {activeConv?.customer_name || activeConv?.customer_id || 'Unknown Customer'}
                          </Typography>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Box
                              sx={{
                                width: 8,
                                height: 8,
                                borderRadius: '50%',
                                bgcolor: getChannelColor(activeConv?.channel || activeChannel),
                              }}
                            />
                            <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                              {activeConv?.channel || activeChannel} • {activeConv?.customer_language.toUpperCase() || 'EN'}
                            </Typography>
                          </Box>
                        </Box>
                      </>
                    )
                  })()}
                </Box>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  {!isMobile && (
                    <>
                      <IconButton size="small" sx={{ color: 'text.secondary' }}>
                        <PhoneIcon />
                      </IconButton>
                      <IconButton size="small" sx={{ color: 'text.secondary' }}>
                        <VideocamIcon />
                      </IconButton>
                    </>
                  )}
                  <IconButton 
                    size="small" 
                    sx={{ color: 'text.secondary' }}
                    onClick={() => setInfoOpen(true)}
                  >
                    <InfoIcon />
                  </IconButton>
                </Box>
              </Paper>

              {/* Messages */}
              <Box
                sx={{
                  flex: 1,
                  overflowY: 'auto',
                  p: { xs: 2, md: 3 },
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 1,
                  bgcolor: alpha(theme.palette.background.default, 0.8),
                  backgroundImage: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.05)} 0%, ${alpha(theme.palette.background.paper, 0.02)} 100%)`,
                  backgroundAttachment: 'fixed'
                }}
              >
                {messages.map((message, index) => (
                  <Box
                    key={message.id || message.turn_index}
                    sx={{
                      display: 'flex',
                      justifyContent: message.speaker === 'user' ? 'flex-end' : 'flex-start',
                      mb: 2,
                      animation: 'fadeInUp 0.3s ease-out',
                      animationDelay: `${index * 0.1}s`,
                      animationFillMode: 'both'
                    }}
                  >
                    <Box
                      sx={{
                        maxWidth: { xs: '85%', sm: '70%', md: '60%' },
                        px: 3,
                        py: 2,
                        borderRadius: message.speaker === 'user' ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
                        position: 'relative',
                        transition: 'all 0.2s ease-in-out',
                        ...(message.speaker === 'user'
                          ? {
                              bgcolor: getChannelColor(activeChannel),
                              color: 'white',
                              boxShadow: `0 2px 8px ${alpha(getChannelColor(activeChannel), 0.3)}`,
                              '&::before': {
                                content: '""',
                                position: 'absolute',
                                bottom: -2,
                                right: 16,
                                width: 0,
                                height: 0,
                                borderLeft: '8px solid transparent',
                                borderRight: '8px solid transparent',
                                borderTop: `8px solid ${getChannelColor(activeChannel)}`,
                              }
                            }
                          : {
                              bgcolor: 'background.paper',
                              color: 'text.primary',
                              boxShadow: '0 1px 4px rgba(0,0,0,0.1)',
                              border: `1px solid ${alpha(theme.palette.divider, 0.3)}`,
                              '&::before': {
                                content: '""',
                                position: 'absolute',
                                bottom: -2,
                                left: 16,
                                width: 0,
                                height: 0,
                                borderLeft: '8px solid transparent',
                                borderRight: '8px solid transparent',
                                borderTop: `8px solid ${theme.palette.background.paper}`,
                              }
                            }
                        ),
                        '&:hover': {
                          transform: 'translateY(-1px)',
                          boxShadow: message.speaker === 'user'
                            ? `0 4px 16px ${alpha(getChannelColor(activeChannel), 0.4)}`
                            : '0 4px 16px rgba(0,0,0,0.15)'
                        }
                      }}
                    >
                      <Typography
                        variant="body1"
                        sx={{
                          wordBreak: 'break-word',
                          lineHeight: 1.5,
                          fontWeight: 400
                        }}
                      >
                        {message.text}
                      </Typography>

                      <Box sx={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: message.speaker === 'user' ? 'flex-end' : 'flex-start',
                        gap: 1,
                        mt: 1,
                        flexWrap: 'wrap'
                      }}>
                        <Typography
                          variant="caption"
                          sx={{
                            opacity: 0.7,
                            fontSize: '0.7rem'
                          }}
                        >
                          {formatTime(new Date(message.timestamp))}
                        </Typography>

                        {message.intent && (
                          <Chip
                            label={`${message.intent}${message.nlu_confidence ? ` (${(message.nlu_confidence * 100).toFixed(0)}%)` : ''}`}
                            size="small"
                            variant="filled"
                            sx={{
                              height: 18,
                              fontSize: '0.65rem',
                              bgcolor: message.speaker === 'user' ? 'rgba(255,255,255,0.2)' : alpha(theme.palette.primary.main, 0.1),
                              color: message.speaker === 'user' ? 'white' : 'primary.main',
                              borderRadius: 1
                            }}
                          />
                        )}

                        {message.handoff_flag && (
                          <Chip
                            label="🤝 Handoff"
                            size="small"
                            sx={{
                              height: 18,
                              fontSize: '0.65rem',
                              bgcolor: 'warning.main',
                              color: 'warning.contrastText',
                              borderRadius: 1
                            }}
                          />
                        )}

                        {message.speaker === 'bot' && (
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <Box
                              sx={{
                                width: 6,
                                height: 6,
                                borderRadius: '50%',
                                bgcolor: 'success.main'
                              }}
                            />
                            <Typography variant="caption" sx={{ fontSize: '0.65rem', opacity: 0.7 }}>
                              AI Assistant
                            </Typography>
                          </Box>
                        )}
                      </Box>
                    </Box>
                  </Box>
                ))}

                {isTyping && (
                  <Box sx={{ display: 'flex', justifyContent: 'flex-start' }}>
                    <Box
                      sx={{
                        bgcolor: 'background.paper',
                        px: 2,
                        py: 1.5,
                        borderRadius: 3,
                        borderBottomLeftRadius: 1,
                        display: 'flex',
                        alignItems: 'center',
                        gap: 0.5,
                        boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                      }}
                    >
                      <CircularProgress size={16} thickness={4} />
                      <Typography variant="body2" sx={{ ml: 1 }}>Typing...</Typography>
                    </Box>
                  </Box>
                )}
                <div ref={messagesEndRef} />
              </Box>

              {/* Message input */}
              <Paper
                elevation={0}
                sx={{
                  borderTop: `1px solid ${theme.palette.divider}`,
                  p: { xs: 2, md: 3 },
                  borderRadius: 0,
                  bgcolor: alpha(theme.palette.background.paper, 0.95),
                  backdropFilter: 'blur(10px)'
                }}
              >
                <Box
                  sx={{
                    display: 'flex',
                    gap: { xs: 1, md: 2 },
                    alignItems: 'flex-end',
                    position: 'relative'
                  }}
                >
                  <TextField
                    fullWidth
                    value={input}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => setInput(e.target.value)}
                    onKeyDown={(e: KeyboardEvent<HTMLInputElement>) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault()
                        if (input.trim() && !isTyping) {
                          sendMessage()
                        }
                      }
                    }}
                    placeholder="Type your message... (Press Enter to send)"
                    variant="outlined"
                    size="small"
                    multiline
                    maxRows={4}
                    disabled={isTyping}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        borderRadius: 4,
                        bgcolor: 'background.paper',
                        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                        transition: 'all 0.2s ease-in-out',
                        '&:hover': {
                          boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
                        },
                        '&.Mui-focused': {
                          boxShadow: `0 0 0 3px ${alpha(getChannelColor(activeChannel), 0.1)}`,
                        }
                      },
                      '& .MuiOutlinedInput-notchedOutline': {
                        borderColor: alpha(theme.palette.divider, 0.5),
                      }
                    }}
                  />

                  <IconButton
                    onClick={sendMessage}
                    disabled={!input.trim() || isTyping}
                    sx={{
                      bgcolor: input.trim() && !isTyping ? getChannelColor(activeChannel) : 'grey.300',
                      color: 'white',
                      borderRadius: 3,
                      width: { xs: 48, md: 56 },
                      height: { xs: 48, md: 56 },
                      boxShadow: input.trim() && !isTyping ? '0 4px 12px rgba(0,0,0,0.2)' : 'none',
                      transition: 'all 0.2s ease-in-out',
                      '&:hover': {
                        bgcolor: input.trim() && !isTyping ? alpha(getChannelColor(activeChannel), 0.9) : 'grey.400',
                        transform: input.trim() && !isTyping ? 'scale(1.05)' : 'none',
                        boxShadow: input.trim() && !isTyping ? '0 6px 20px rgba(0,0,0,0.3)' : 'none'
                      },
                      '&:disabled': {
                        bgcolor: 'grey.300',
                        color: 'grey.500',
                        cursor: 'not-allowed'
                      }
                    }}
                  >
                    {isTyping ? (
                      <CircularProgress size={20} sx={{ color: 'white' }} />
                    ) : (
                      <SendIcon sx={{ fontSize: { xs: 20, md: 24 } }} />
                    )}
                  </IconButton>
                </Box>

                {/* Typing indicator */}
                {isTyping && (
                  <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CircularProgress size={14} />
                    <Typography variant="caption" sx={{ color: 'text.secondary', fontStyle: 'italic' }}>
                      AI is typing...
                    </Typography>
                  </Box>
                )}
              </Paper>
            </>
          ) : (
            <Box
              sx={{
                flex: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexDirection: 'column',
                gap: 2,
              }}
            >
              <Avatar
                sx={{
                  width: 64,
                  height: 64,
                  bgcolor: 'grey.100',
                  color: 'grey.400',
                }}
              >
                <ChatBubbleLeftRightIcon sx={{ fontSize: 32 }} />
              </Avatar>
              <Typography variant="h6" sx={{ color: 'text.primary', fontWeight: 500 }}>
                Select a conversation
              </Typography>
              <Typography variant="body2" sx={{ color: 'text.secondary', textAlign: 'center', maxWidth: 300 }}>
                Choose a conversation from the sidebar to start chatting with our AI-powered assistant
              </Typography>
            </Box>
          )}
        </Box>

        {/* Customer info sidebar - Desktop */}
        {!isMobile && !isTablet && activeConversation && (
          <Paper
            elevation={0}
            sx={{
              width: 320,
              borderLeft: `1px solid ${theme.palette.divider}`,
              borderRadius: 0,
              display: 'flex',
              flexDirection: 'column',
              overflow: 'auto'
            }}
          >
            <Box sx={{ p: 3 }}>
              <Box sx={{ textAlign: 'center', mb: 4 }}>
                <Avatar
                  sx={{
                    width: 64,
                    height: 64,
                    bgcolor: getChannelColor(activeChannel),
                    mx: 'auto',
                    mb: 2,
                    fontSize: 24,
                    fontWeight: 'bold',
                  }}
                >
                  J
                </Avatar>
                <Typography variant="h6" sx={{ fontWeight: 600, color: 'text.primary', mb: 1 }}>
                  John Doe
                </Typography>
                <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                  Customer ID: #12345
                </Typography>
              </Box>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                <Card variant="outlined" sx={{ bgcolor: 'grey.50' }}>
                  <CardContent sx={{ p: 2 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'text.primary', mb: 2 }}>
                      Contact Info
                    </Typography>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="body2" sx={{ color: 'text.secondary' }}>Phone:</Typography>
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>+880 1234-567890</Typography>
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="body2" sx={{ color: 'text.secondary' }}>Channel:</Typography>
                        <Chip label={activeChannel} size="small" color="primary" />
                      </Box>
                    </Box>
                  </CardContent>
                </Card>

                <Card variant="outlined" sx={{ bgcolor: 'grey.50' }}>
                  <CardContent sx={{ p: 2 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'text.primary', mb: 2 }}>
                      AI Assistant
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'text.secondary', lineHeight: 1.6 }}>
                      Using GPT-4o-mini for multilingual support in Bangla, English, Hindi, Arabic, and Urdu.
                    </Typography>
                  </CardContent>
                </Card>
              </Box>
            </Box>
          </Paper>
        )}

        {/* Customer info drawer - Mobile/Tablet */}
        {(isMobile || isTablet) && (
          <Drawer
            anchor="right"
            open={infoOpen}
            onClose={() => setInfoOpen(false)}
            sx={{
              '& .MuiDrawer-paper': {
                width: { xs: '100%', sm: 360 },
                boxSizing: 'border-box',
              },
            }}
          >
            <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <Box sx={{ p: 2, borderBottom: `1px solid ${theme.palette.divider}`, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>Customer Info</Typography>
                <IconButton onClick={() => setInfoOpen(false)}>
                  <ArrowBackIcon />
                </IconButton>
              </Box>
              <Box sx={{ p: 3, flex: 1, overflow: 'auto' }}>
                <Box sx={{ textAlign: 'center', mb: 4 }}>
                  <Avatar
                    sx={{
                      width: 64,
                      height: 64,
                      bgcolor: getChannelColor(activeChannel),
                      mx: 'auto',
                      mb: 2,
                      fontSize: 24,
                      fontWeight: 'bold',
                    }}
                  >
                    J
                  </Avatar>
                  <Typography variant="h6" sx={{ fontWeight: 600, color: 'text.primary', mb: 1 }}>
                    John Doe
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    Customer ID: #12345
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                  <Card variant="outlined" sx={{ bgcolor: 'grey.50' }}>
                    <CardContent sx={{ p: 2 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'text.primary', mb: 2 }}>
                        Contact Info
                      </Typography>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Typography variant="body2" sx={{ color: 'text.secondary' }}>Phone:</Typography>
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>+880 1234-567890</Typography>
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Typography variant="body2" sx={{ color: 'text.secondary' }}>Channel:</Typography>
                          <Chip label={activeChannel} size="small" color="primary" />
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>

                  <Card variant="outlined" sx={{ bgcolor: 'grey.50' }}>
                    <CardContent sx={{ p: 2 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'text.primary', mb: 2 }}>
                        AI Assistant
                      </Typography>
                      <Typography variant="body2" sx={{ color: 'text.secondary', lineHeight: 1.6 }}>
                        Using GPT-4o-mini for multilingual support in Bangla, English, Hindi, Arabic, and Urdu.
                      </Typography>
                    </CardContent>
                  </Card>
                </Box>
              </Box>
            </Box>
          </Drawer>
        )}
      </Box>
    </Box>
  )
}
