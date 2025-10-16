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
  alpha
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
  ArrowBack as ArrowBackIcon
} from '@mui/icons-material'

// Helper function to format time
const formatTime = (date: Date) => {
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

interface Message {
  id: string
  text: string
  sender: 'user' | 'bot'
  timestamp: Date
  channel: 'messenger' | 'whatsapp' | 'instagram'
}

interface Conversation {
  id: string
  customerName: string
  lastMessage: string
  timestamp: Date
  unreadCount: number
  channel: 'messenger' | 'whatsapp' | 'instagram'
  status: 'active' | 'waiting' | 'resolved' | 'completed' | 'escalated'
}

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

  // Sample conversations
  useEffect(() => {
    const sampleConversations: Conversation[] = [
      {
        id: '1',
        customerName: 'John Doe',
        lastMessage: 'আমার অর্ডার কোথায়?',
        timestamp: new Date(Date.now() - 5 * 60 * 1000),
        unreadCount: 2,
        channel: 'whatsapp',
        status: 'active'
      },
      {
        id: '2',
        customerName: 'Sarah Wilson',
        lastMessage: 'iPhone 15 price?',
        timestamp: new Date(Date.now() - 15 * 60 * 1000),
        unreadCount: 0,
        channel: 'messenger',
        status: 'waiting'
      },
      {
        id: '3',
        customerName: 'Ahmed Khan',
        lastMessage: 'ডেলিভারি টাইম কত?',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
        unreadCount: 1,
        channel: 'instagram',
        status: 'resolved'
      }
    ]
    setConversations(sampleConversations)
    setActiveConversation('1')

    // Sample messages for active conversation
    const sampleMessages: Message[] = [
      {
        id: '1',
        text: 'হ্যালো, আমি কিছু জিজ্ঞাসা করতে চাই',
        sender: 'user',
        timestamp: new Date(Date.now() - 10 * 60 * 1000),
        channel: 'whatsapp'
      },
      {
        id: '2',
        text: 'নিশ্চয়ই! আমি আপনাকে সাহায্য করতে পারি। আপনার কী প্রশ্ন আছে?',
        sender: 'bot',
        timestamp: new Date(Date.now() - 9 * 60 * 1000),
        channel: 'whatsapp'
      },
      {
        id: '3',
        text: 'আমার অর্ডার #123 এর স্ট্যাটাস কী?',
        sender: 'user',
        timestamp: new Date(Date.now() - 8 * 60 * 1000),
        channel: 'whatsapp'
      },
      {
        id: '4',
        text: 'আপনার অর্ডার #123 বর্তমানে "প্রসেসিং" স্ট্যাটাসে আছে। এটি আজ রাতের মধ্যে শিপ করা হবে। আপনার কোনো অন্য প্রশ্ন আছে?',
        sender: 'bot',
        timestamp: new Date(Date.now() - 7 * 60 * 1000),
        channel: 'whatsapp'
      }
    ]
    setMessages(sampleMessages)
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  async function sendMessage() {
    if (!input.trim()) return

    const newMessage: Message = {
      id: Date.now().toString(),
      text: input,
      sender: 'user',
      timestamp: new Date(),
      channel: activeChannel
    }

    setMessages(prev => [...prev, newMessage])
    setInput('')
    setIsTyping(true)

    // Simulate AI response
    setTimeout(() => {
      const aiResponse = generateAIResponse(input)
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: aiResponse,
        sender: 'bot',
        timestamp: new Date(),
        channel: activeChannel
      }
      setMessages(prev => [...prev, botMessage])
      setIsTyping(false)
    }, 1000 + Math.random() * 2000)
  }

  function generateAIResponse(userMessage: string): string {
    const lowerMessage = userMessage.toLowerCase()

    if (lowerMessage.includes('অর্ডার') || lowerMessage.includes('order')) {
      return 'আপনার অর্ডার স্ট্যাটাস দেখার জন্য আপনার অর্ডার আইডি দিন। উদাহরণ: "অর্ডার #123"'
    }

    if (lowerMessage.includes('দাম') || lowerMessage.includes('price') || lowerMessage.includes('কত')) {
      return 'আমাদের প্রোডাক্টের দাম জানতে চান? কোন প্রোডাক্টের দাম জানতে চান বলুন।'
    }

    if (lowerMessage.includes('ডেলিভারি') || lowerMessage.includes('delivery')) {
      return 'আমাদের ডেলিভারি ২-৩ কার্যদিবসের মধ্যে হয়। আপনার এলাকায় কতদিন লাগবে জানতে চান?'
    }

    if (lowerMessage.includes('রিটার্ন') || lowerMessage.includes('return')) {
      return 'প্রোডাক্ট রিটার্ন করতে চান? রিসিভ করে ৭ দিনের মধ্যে রিটার্ন করা যায়। বিস্তারিত জানতে বলুন।'
    }

    return 'আপনার প্রশ্নটি ভালো করে বুঝতে পারলাম না। অনুগ্রহ করে আরেকটু বিস্তারিত করে বলুন, যেমন: "অর্ডার স্ট্যাটাস", "প্রোডাক্ট দাম", বা "ডেলিভারি ইনফো"।'
  }


  const getChannelColor = (channel: string) => {
    switch (channel) {
      case 'whatsapp':
        return theme.palette.whatsapp.main
      case 'messenger':
        return theme.palette.facebook.main
      case 'instagram':
        return theme.palette.instagram.main
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
                selected={activeConversation === conversation.id}
                onClick={() => {
                  setActiveConversation(conversation.id)
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
                    badgeContent={conversation.unreadCount}
                    invisible={conversation.unreadCount === 0}
                  >
                    <Avatar
                      sx={{
                        bgcolor: getChannelColor(conversation.channel),
                        width: 40,
                        height: 40
                      }}
                    >
                      {conversation.customerName.charAt(0).toUpperCase()}
                    </Avatar>
                  </Badge>
                </ListItemAvatar>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'text.primary' }}>
                        {conversation.customerName}
                      </Typography>
                      <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                        {formatTime(conversation.timestamp)}
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
                        {conversation.lastMessage}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Chip
                          label={conversation.channel}
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
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', bgcolor: 'background.default' }}>
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
                  Manage customer conversations
                </Typography>
              )}
            </Box>
          </Box>

          {/* Channel tabs */}
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {[
              { id: 'messenger' as const, label: isMobile ? 'FB' : 'Messenger', color: theme.palette.facebook.main, emoji: '💙' },
              { id: 'whatsapp' as const, label: isMobile ? 'WA' : 'WhatsApp', color: theme.palette.whatsapp.main, emoji: '💚' },
              { id: 'instagram' as const, label: isMobile ? 'IG' : 'Instagram', color: theme.palette.instagram.main, emoji: '💜' }
            ].map(({ id, label, color, emoji }) => (
              <Button
                key={id}
                onClick={() => setActiveChannel(id)}
                variant={activeChannel === id ? 'contained' : 'outlined'}
                startIcon={!isMobile && <Box sx={{ fontSize: '1.2rem' }}>{emoji}</Box>}
                size={isMobile ? 'small' : 'medium'}
                sx={{
                  borderRadius: 2,
                  textTransform: 'none',
                  fontWeight: 500,
                  minWidth: isMobile ? 50 : 120,
                  ...(activeChannel === id && {
                    backgroundColor: color,
                    '&:hover': { backgroundColor: alpha(color, 0.8) }
                  })
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
                  px: 3,
                  py: 2,
                  borderRadius: 0,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between'
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Avatar
                    sx={{
                      bgcolor: getChannelColor(activeChannel),
                      width: 40,
                      height: 40
                    }}
                  >
                    J
                  </Avatar>
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 600, color: 'text.primary' }}>
                      John Doe
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box
                        sx={{
                          width: 8,
                          height: 8,
                          borderRadius: '50%',
                          bgcolor: activeChannel === 'whatsapp' ? 'whatsapp.main' : 'primary.main',
                        }}
                      />
                      <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                        Active now
                      </Typography>
                    </Box>
                  </Box>
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
                className="chat-messages"
                sx={{
                  flex: 1,
                  overflowY: 'auto',
                  p: 3,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 2,
                }}
              >
                {messages.map((message) => (
                  <Box
                    key={message.id}
                    sx={{
                      display: 'flex',
                      justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                    }}
                  >
                    <Box
                      className="chat-message"
                      sx={{
                        ...(message.sender === 'user'
                          ? {
                              bgcolor: 'primary.main',
                              color: 'primary.contrastText',
                              ml: 'auto',
                              borderBottomRightRadius: 1,
                            }
                          : {
                              bgcolor: 'grey.100',
                              color: 'text.primary',
                              borderBottomLeftRadius: 1,
                            }
                        ),
                      }}
                    >
                      <Typography variant="body2">{message.text}</Typography>
                      <Typography
                        variant="caption"
                        sx={{
                          mt: 0.5,
                          display: 'block',
                          color: message.sender === 'user' ? 'primary.light' : 'text.secondary',
                        }}
                      >
                        {formatTime(message.timestamp)}
                      </Typography>
                    </Box>
                  </Box>
                ))}

                {isTyping && (
                  <Box sx={{ display: 'flex', justifyContent: 'flex-start' }}>
                    <Box
                      sx={{
                        bgcolor: 'grey.100',
                        px: 2,
                        py: 1,
                        borderRadius: 3,
                        borderBottomLeftRadius: 1,
                      }}
                    >
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <Box className="typing-indicator" />
                        <Box className="typing-indicator" sx={{ animationDelay: '0.1s' }} />
                        <Box className="typing-indicator" sx={{ animationDelay: '0.2s' }} />
                      </Box>
                    </Box>
                  </Box>
                )}
                <div ref={messagesEndRef} />
              </Box>

              {/* Message input */}
              <Box
                className="chat-input-area"
                sx={{
                  borderTop: `1px solid ${theme.palette.divider}`,
                  p: 2,
                  display: 'flex',
                  gap: 2,
                  alignItems: 'center',
                }}
              >
                <TextField
                  fullWidth
                  value={input}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => setInput(e.target.value)}
                  onKeyPress={(e: KeyboardEvent<HTMLInputElement>) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
                  placeholder="Type a message..."
                  variant="outlined"
                  size="small"
                  multiline
                  maxRows={3}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 3,
                    },
                  }}
                />
                <Button
                  onClick={sendMessage}
                  disabled={!input.trim()}
                  variant="contained"
                  endIcon={<SendIcon />}
                  sx={{
                    borderRadius: 3,
                    px: 3,
                    textTransform: 'none',
                    fontWeight: 500,
                  }}
                >
                  Send
                </Button>
              </Box>
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
              <Typography variant="body2" sx={{ color: 'text.secondary', textAlign: 'center' }}>
                Choose a conversation from the sidebar to start chatting
              </Typography>
            </Box>
          )}
        </Box>

        {/* Customer info sidebar - Desktop */}
        {!isMobile && !isTablet && (
          <Paper
            elevation={0}
            sx={{
              width: 320,
              borderLeft: `1px solid ${theme.palette.divider}`,
              borderRadius: 0,
              display: 'flex',
              flexDirection: 'column',
            }}
          >
            {activeConversation ? (
            <Box sx={{ p: 3, height: '100%', overflow: 'auto' }}>
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
                        <Typography variant="body2" sx={{ color: 'text.secondary' }}>Email:</Typography>
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>john@example.com</Typography>
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="body2" sx={{ color: 'text.secondary' }}>Channel:</Typography>
                        <Typography variant="body2" sx={{ fontWeight: 500, textTransform: 'capitalize' }}>
                          {activeChannel}
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>

                <Card variant="outlined" sx={{ bgcolor: 'grey.50' }}>
                  <CardContent sx={{ p: 2 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'text.primary', mb: 2 }}>
                      Recent Orders
                    </Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="body2">Order #123</Typography>
                      <Chip
                        label="Processing"
                        size="small"
                        sx={{
                          height: 20,
                          fontSize: '0.7rem',
                          bgcolor: 'warning.light',
                          color: 'warning.dark',
                        }}
                      />
                    </Box>
                    <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                      iPhone 15 Pro • $999 • 2 days ago
                    </Typography>
                  </CardContent>
                </Card>

                <Card variant="outlined" sx={{ bgcolor: 'grey.50' }}>
                  <CardContent sx={{ p: 2 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'text.primary', mb: 2 }}>
                      Conversation Summary
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'text.secondary', lineHeight: 1.5 }}>
                      Customer is inquiring about order status and delivery timeline.
                      Previous interaction was about product pricing.
                    </Typography>
                  </CardContent>
                </Card>
              </Box>
            </Box>
          ) : (
            <Box sx={{ p: 3, textAlign: 'center', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Box>
                <InfoIcon sx={{ fontSize: 48, color: 'grey.400', mb: 2 }} />
                <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                  Select a conversation to view customer details
                </Typography>
              </Box>
            </Box>
          )}
          </Paper>
        )}

        {/* Customer info sidebar - Mobile/Tablet Drawer */}
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
            {activeConversation && (
              <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <Box sx={{ p: 2, borderBottom: `1px solid ${theme.palette.divider}`, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>Customer Info</Typography>
                  <IconButton onClick={() => setInfoOpen(false)}>
                    <ArrowBackIcon />
                  </IconButton>
                </Box>
                <Box sx={{ p: 3, height: '100%', overflow: 'auto' }}>
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
                            <Typography variant="body2" sx={{ color: 'text.secondary' }}>Email:</Typography>
                            <Typography variant="body2" sx={{ fontWeight: 500 }}>john@example.com</Typography>
                          </Box>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Typography variant="body2" sx={{ color: 'text.secondary' }}>Channel:</Typography>
                            <Typography variant="body2" sx={{ fontWeight: 500, textTransform: 'capitalize' }}>
                              {activeChannel}
                            </Typography>
                          </Box>
                        </Box>
                      </CardContent>
                    </Card>

                    <Card variant="outlined" sx={{ bgcolor: 'grey.50' }}>
                      <CardContent sx={{ p: 2 }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'text.primary', mb: 2 }}>
                          Recent Orders
                        </Typography>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                          <Typography variant="body2">Order #123</Typography>
                          <Chip
                            label="Processing"
                            size="small"
                            sx={{
                              height: 20,
                              fontSize: '0.7rem',
                              bgcolor: 'warning.light',
                              color: 'warning.dark',
                            }}
                          />
                        </Box>
                        <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                          iPhone 15 Pro • $999 • 2 days ago
                        </Typography>
                      </CardContent>
                    </Card>

                    <Card variant="outlined" sx={{ bgcolor: 'grey.50' }}>
                      <CardContent sx={{ p: 2 }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'text.primary', mb: 2 }}>
                          Conversation Summary
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'text.secondary', lineHeight: 1.5 }}>
                          Customer is inquiring about order status and delivery timeline.
                          Previous interaction was about product pricing.
                        </Typography>
                      </CardContent>
                    </Card>
                  </Box>
                </Box>
              </Box>
            )}
          </Drawer>
        )}
      </Box>
    </Box>
  )
}
