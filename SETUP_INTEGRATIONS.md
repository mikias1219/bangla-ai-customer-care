# Bangla AI Platform - Complete Setup Guide

This guide covers setting up all communication channels for your Bangla AI customer service platform.

## 🚀 Overview

Your platform supports:
- **Voice Calls**: Twilio IVR + Asterisk/FreeSWITCH VoIP
- **Chat Channels**: Facebook Messenger, WhatsApp, Instagram
- **Website Chat**: Web widget integration
- **Admin Dashboard**: Real-time monitoring and management

## 📋 Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL database
- Redis
- Docker & Docker Compose (recommended)
- **OpenAI API Key** (for multilingual TTS, ASR, and advanced AI features)

## 🏗️ 1. Initial Setup

### Clone and Install Dependencies

```bash
git clone <your-repo-url>
cd bangla
cp env.example .env
```

### Configure Environment Variables

Edit `.env` with your configuration. See `env.example` for all available options.

**Important**: Set your OpenAI API key for multilingual AI features:

```env
BANG_OPENAI_API_KEY=your-openai-api-key-here
BANG_TTS_PROVIDER=openai
BANG_OPENAI_TTS_VOICE=alloy
BANG_OPENAI_TTS_MODEL=tts-1
```

### Start the Platform

```bash
# Using Docker Compose (recommended)
docker-compose up -d

# Or manually
cd backend && pip install -r requirements.txt
cd ../frontend/dashboard && npm install
# Start services...
```

## 📱 2. Social Media Integrations

### Facebook Messenger Setup

1. **Create Facebook App**
   - Go to [Facebook Developers](https://developers.facebook.com)
   - Create a new app → Business → App Contacts
   - Add Messenger product

2. **Configure Webhooks**
   - Webhook URL: `https://yourdomain.com/channels/meta/webhook`
   - Verify Token: Set in `.env` as `BANG_FACEBOOK_VERIFY_TOKEN`
   - Subscribe to: `messages`, `messaging_postbacks`

3. **Get Access Tokens**
   ```bash
   # Use Facebook Graph API Explorer to get Page Access Token
   # App ID and App Secret from app settings
   ```

4. **Environment Variables**
   ```env
   BANG_FACEBOOK_APP_ID=your-app-id
   BANG_FACEBOOK_APP_SECRET=your-app-secret
   BANG_FACEBOOK_PAGE_ACCESS_TOKEN=your-page-token
   BANG_FACEBOOK_VERIFY_TOKEN=your-verify-token
   ```

### Instagram Business Setup

1. **Connect Instagram Business Account**
   - Go to your Facebook Page settings
   - Connect Instagram Business account
   - Get Instagram Business ID from Graph API Explorer

2. **Configure Webhooks**
   - Same webhook URL as Messenger
   - Subscribe to Instagram events

3. **Environment Variables**
   ```env
   BANG_INSTAGRAM_BUSINESS_ID=your-instagram-business-id
   BANG_INSTAGRAM_ACCESS_TOKEN=your-instagram-token
   ```

### WhatsApp Business API Setup

1. **Get WhatsApp Business API Access**
   - Apply for WhatsApp Business API through approved providers
   - Or use Meta's direct access for eligible businesses

2. **Configure Webhooks**
   - Webhook URL: `https://yourdomain.com/channels/whatsapp/webhook`
   - Verify Token: Set in `.env`

3. **Environment Variables**
   ```env
   BANG_WHATSAPP_BUSINESS_ID=your-business-id
   BANG_WHATSAPP_ACCESS_TOKEN=your-access-token
   BANG_WHATSAPP_VERIFY_TOKEN=your-verify-token
   BANG_WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id
   ```

## 🤖 3. Multilingual AI Configuration

### OpenAI TTS & ASR Setup

Your platform now supports **all languages** using OpenAI's advanced AI models:

#### Text-to-Speech (TTS) Features:
- **6 High-Quality Voices**: alloy, echo, fable, onyx, nova, shimmer
- **Automatic Language Detection**: No need to specify language codes
- **Natural Sounding Speech**: Superior quality compared to traditional TTS
- **Multiple Languages**: English, Spanish, French, German, Italian, Portuguese, Arabic, Chinese, Japanese, Korean, and more

#### Speech-to-Text (ASR) Features:
- **OpenAI Whisper**: Industry-leading accuracy
- **Automatic Language Detection**: Detects language from speech automatically
- **99 Languages Supported**: From Afrikaans to Zulu
- **Real-time Processing**: Optimized for conversational AI

#### Configuration:

```env
# TTS Settings
BANG_TTS_PROVIDER=openai
BANG_OPENAI_TTS_VOICE=alloy          # alloy, echo, fable, onyx, nova, shimmer
BANG_OPENAI_TTS_MODEL=tts-1          # tts-1 or tts-1-hd (higher quality)

# ASR Settings (Whisper)
BANG_WHISPER_MODEL_SIZE=base         # tiny, base, small, medium, large

# OpenAI API
BANG_OPENAI_API_KEY=your-key-here
```

#### Voice Options:
- **alloy**: Neutral, clear voice (recommended)
- **echo**: American male voice
- **fable**: British male voice, storytelling
- **onyx**: Deep American male voice
- **nova**: American female voice, young
- **shimmer**: American female voice, warm

#### Testing Multilingual AI:

```bash
# Run the test script
python test_multilingual_ai.py

# Test TTS API directly
curl -X POST "http://localhost:8000/channels/voice/twilio/audio/Hello%20world?lang=en&voice=alloy" \
  --output test_tts.mp3

# Test ASR with file (if you have an audio file)
# The system auto-detects language from speech
```

## 📞 4. Voice Integration Setup

### Twilio IVR Setup

1. **Create Twilio Account**
   - Sign up at [Twilio](https://twilio.com)
   - Get Account SID, Auth Token, and phone number

2. **Configure Voice Webhooks**
   - Voice URL: `https://yourdomain.com/channels/voice/twilio/voice`
   - Fallback URL: Same as above

3. **Environment Variables**
   ```env
   TWILIO_ACCOUNT_SID=your-account-sid
   TWILIO_AUTH_TOKEN=your-auth-token
   TWILIO_PHONE_NUMBER=+1234567890
   ```

### Asterisk/FreeSWITCH VoIP Setup

1. **Install Asterisk or FreeSWITCH**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install asterisk

   # Or FreeSWITCH
   # Follow official FreeSWITCH installation guide
   ```

2. **Configure AGI Script**
   Create `/etc/asterisk/agi-bin/bangla_ai.py`:

   ```python
   import requests
   import sys

   def agi_request():
       # Read AGI variables
       agi_vars = {}
       for line in sys.stdin:
           if line.strip() == '':
               break
           key, value = line.split(':', 1)
           agi_vars[key.strip()] = value.strip()

       # Send to Bangla AI
       response = requests.post('http://your-server:8000/channels/voice/voip/asterisk/inbound',
                               json={'caller_id': agi_vars.get('callerid')})

       # Process response and generate audio
       # ... implementation details
   ```

3. **Dialplan Configuration**
   Add to `/etc/asterisk/extensions.conf`:

   ```
   [bangla-ai]
   exten => _X.,1,AGI(bangla_ai.py)
   exten => _X.,n,Hangup()
   ```

## 🌐 4. Website Chat Widget

### Frontend Integration

1. **Build the Chat Widget**
   ```bash
   cd frontend/widget
   npm run build
   ```

2. **Add to Your Website**
   ```html
   <!-- Add this to your website's HTML -->
   <script src="https://yourdomain.com/widget/bangla-chat.js"></script>
   <div id="bangla-chat-widget"></div>
   ```

### Backend Configuration

The webchat endpoint is available at:
- Webhook: `https://yourdomain.com/channels/webchat/message`

## 📊 5. Admin Dashboard Features

### Real-time Monitoring

- **Conversation Analytics**: View message volume, response times
- **Channel Performance**: Compare engagement across platforms
- **AI Accuracy Metrics**: Track NLU confidence scores

### Intent & Entity Management

- **Edit Intents**: Add/modify conversation intents
- **Manage Entities**: Update entity recognition rules
- **Training Data**: Upload new training examples

### System Health

- **API Response Times**: Monitor endpoint performance
- **Error Rates**: Track failed interactions
- **Resource Usage**: CPU, memory, and database metrics

## 🔧 6. Testing & Deployment

### Test All Channels

```bash
# Test voice endpoints
curl -X POST http://localhost:8000/channels/voice/twilio/voice

# Test chat endpoints
curl -X POST http://localhost:8000/channels/meta/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": "message"}'

# Test NLU
curl -X POST http://localhost:8000/nlu/resolve \
  -H "Content-Type: application/json" \
  -d '{"text": "আমার অর্ডার কোথায়?"}'
```

### Production Deployment

1. **SSL Certificate**: Required for webhooks
2. **Load Balancing**: Use nginx or similar
3. **Database Backup**: Regular PostgreSQL backups
4. **Monitoring**: Set up Prometheus/Grafana

### Scaling Considerations

- **Redis Clustering**: For high message volumes
- **Database Sharding**: For large customer bases
- **AI Model Optimization**: Use GPU instances for better performance

## 🚨 Troubleshooting

### Common Issues

1. **Webhook Verification Fails**
   - Check verify tokens match exactly
   - Ensure HTTPS URLs for production

2. **Messages Not Received**
   - Verify access tokens are valid
   - Check webhook subscription status

3. **Voice Quality Issues**
   - Test TTS provider connectivity
   - Check audio encoding formats

4. **High Latency**
   - Optimize database queries
   - Consider CDN for static assets
   - Use caching for frequent responses

### Logs & Debugging

```bash
# View application logs
docker-compose logs -f backend

# Check API health
curl http://localhost:8000/health

# Monitor metrics
curl http://localhost:8000/metrics

# Test multilingual AI services
python test_multilingual_ai.py
```

## 📚 Additional Resources

- [Facebook Messenger Platform Docs](https://developers.facebook.com/docs/messenger-platform/)
- [WhatsApp Business API Docs](https://developers.facebook.com/docs/whatsapp/)
- [Twilio Voice API Docs](https://www.twilio.com/docs/voice)
- [Asterisk Documentation](https://wiki.asterisk.org/)

## 🎯 Next Steps

1. Configure all desired channels
2. Test integrations thoroughly
3. Set up monitoring and alerts
4. Train AI models with domain-specific data
5. Deploy to production with proper scaling

Your Bangla AI platform is now ready to handle customer conversations across multiple channels! 🇧🇩
