# 🚀 Simple VPS Deployment (No Docker) - Bangla AI Platform

Deploy the backend (FastAPI) and dashboard (Vite React) directly on a VPS with SQLite and Nginx.

## Prerequisites

- Ubuntu 22.04+ VPS
- Domain pointed to server IP (e.g., `yourdomain.com`)
- sudo user and SSH access

## 1) Server setup

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip nginx certbot python3-certbot-nginx git
```

## 2) Clone project

```bash
cd /opt
sudo git clone https://github.com/your/repo.git bangla
sudo chown -R $USER:$USER bangla
cd bangla
cp env.example .env
# edit .env
# BANG_DATABASE_URL=sqlite:///./bangla.db
# BANG_CORS_ORIGINS=["https://yourdomain.com"]
```

## 3) Backend install (venv)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python scripts/init_db.py  # create tables/seed
deactivate
```

## 4) Create systemd service for backend

Create `/etc/systemd/system/bangla-backend.service`:

```
[Unit]
Description=Bangla AI Backend (FastAPI)
After=network.target

[Service]
User=%i
WorkingDirectory=/opt/bangla/backend
EnvironmentFile=/opt/bangla/.env
ExecStart=/opt/bangla/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now bangla-backend
sudo systemctl status bangla-backend
```

## 5) Build frontend

```bash
cd /opt/bangla/frontend/dashboard
npm ci || npm install
npm run build
sudo mkdir -p /var/www/bangla
sudo cp -r dist/* /var/www/bangla/
```

## 6) Nginx site

Create `/etc/nginx/sites-available/bangla`:

```
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        root /var/www/bangla;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location / {
        add_header Access-Control-Allow-Origin *;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /channels/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Enable and obtain HTTPS:

```bash
sudo ln -s /etc/nginx/sites-available/bangla /etc/nginx/sites-enabled/bangla
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## 7) Frontend API base

Set `VITE_API_BASE` at build time if needed:

```bash
VITE_API_BASE=https://yourdomain.com npm run build
```

## 8) Updates

```bash
cd /opt/bangla
git pull
cd backend && source .venv/bin/activate && pip install -r requirements.txt && deactivate
sudo systemctl restart bangla-backend
npm --prefix frontend/dashboard run build
sudo cp -r frontend/dashboard/dist/* /var/www/bangla/
```

## Notes

- SQLite DB file is at `/opt/bangla/backend/bangla.db` (relative to WorkingDirectory).
- For migrations, `alembic` can run against SQLite; ensure models are in sync.
