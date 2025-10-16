const express = require('express');
const path = require('path');
const cors = require('cors');
const { createServer } = require('http');
const { Server } = require('socket.io');

const app = express();
const server = createServer(app);
const io = new Server(server, {
  cors: {
    origin: ["https://bdchatpro.com", "http://localhost:3000", "http://localhost:3002"],
    methods: ["GET", "POST"]
  }
});

const PORT = process.env.PORT || 3002;

// Middleware
app.use(cors({
  origin: ["https://bdchatpro.com", "http://localhost:3000", "http://localhost:3002"],
  credentials: true
}));
app.use(express.json());

// API proxy to backend
app.use('/api', (req, res) => {
  const http = require('http');
  const options = {
    hostname: '127.0.0.1',
    port: 8000,
    path: req.path,
    method: req.method,
    headers: {
      ...req.headers,
      host: 'localhost:8000'
    }
  };

  const proxyReq = http.request(options, (proxyRes) => {
    res.writeHead(proxyRes.statusCode, proxyRes.headers);
    proxyRes.pipe(res);
  });

  proxyReq.on('error', (err) => {
    console.error('Proxy error:', err);
    res.status(500).json({ error: 'Backend service unavailable' });
  });

  req.pipe(proxyReq);
});

// Serve static files from dashboard/dist directory
app.use(express.static(path.join(__dirname, 'dashboard', 'dist')));

// SPA fallback - serve index.html for all non-API routes
app.get('*', (req, res) => {
  const indexPath = path.join(__dirname, 'dashboard', 'dist', 'index.html');
  if (require('fs').existsSync(indexPath)) {
    res.sendFile(indexPath);
  } else {
    res.send(`
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bangla AI Customer Care</title>
        <style>
          body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
          .container { max-width: 600px; margin: 0 auto; }
          h1 { color: #2563eb; }
          .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
          .success { background: #d1fae5; color: #065f46; }
          .info { background: #dbeafe; color: #1e40af; }
        </style>
      </head>
      <body>
        <div class="container">
          <h1>🚀 Bangla AI Customer Care</h1>
          <div class="status success">
            ✅ Frontend server is running on port ${PORT}
          </div>
          <div class="status info">
            🔧 Backend API: http://localhost:8000<br>
            🌐 Public URL: https://bdchatpro.com<br>
            📊 Health Check: https://bdchatpro.com/health
          </div>
          <p>The React dashboard will be served here once deployed.</p>
        </div>
      </body>
      </html>
    `);
  }
});

// WebSocket handling
io.on('connection', (socket) => {
  console.log(`🔗 User connected: ${socket.id}`);

  socket.on('disconnect', () => {
    console.log(`📴 User disconnected: ${socket.id}`);
  });

  // Handle real-time messaging
  socket.on('message', (data) => {
    console.log('Message received:', data);
    // Broadcast to other clients if needed
    socket.broadcast.emit('message', data);
  });
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'frontend',
    port: PORT,
    timestamp: new Date().toISOString()
  });
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Frontend server running on http://0.0.0.0:${PORT}`);
  console.log(`🌐 Public access: https://bdchatpro.com`);
  console.log(`🔧 Backend proxy: http://127.0.0.1:8000`);
});
