# Deployment Guide (Linux Server)

This guide gives you a **full working production setup** for this project on a Linux VPS/server.

## 1) Project requirements

### Server requirements

- OS: Ubuntu 22.04+ (or compatible Linux distro)
- CPU/RAM: minimum 2 vCPU / 2 GB RAM (4 GB recommended)
- Disk: 20 GB+
- Open ports:
  - `22` (SSH)
  - `80` (HTTP)
  - `443` (HTTPS)

### Software requirements

- Git
- Node.js 20 LTS + npm
- Python 3.11+
- Nginx
- Certbot (Let's Encrypt)
- (Optional) PostgreSQL 15+ (if you do not want SQLite)

Install base packages:

```bash
sudo apt update
sudo apt install -y git curl nginx python3 python3-venv python3-pip certbot python3-certbot-nginx
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

Verify:

```bash
node -v
npm -v
python3 --version
nginx -v
```

---

## 2) Clone project and install dependencies

```bash
sudo mkdir -p /var/www
cd /var/www
sudo git clone <YOUR_REPO_URL> hotwheels
sudo chown -R $USER:$USER /var/www/hotwheels
cd /var/www/hotwheels
```

### Frontend dependencies

```bash
npm ci
```

### Backend dependencies

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cd ..
```

---

## 3) Environment configuration

> The backend reads environment variables from the **repo root `.env`**.

Create production env:

```bash
cd /var/www/hotwheels
cp .env.example .env
```

### Option A: SQLite (fastest to start)

Use:

```env
DB_DRIVER=sqlite
SQLITE_PATH=backend/hotwheels.db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hotwheels
DB_USER=hotwheels_user
DB_PASSWORD=change_me
```

### Option B: PostgreSQL (recommended for production)

Install postgres (if needed):

```bash
sudo apt install -y postgresql postgresql-contrib
sudo -u postgres psql
```

Run in psql:

```sql
CREATE DATABASE hotwheels;
CREATE USER hotwheels_user WITH PASSWORD 'STRONG_PASSWORD_HERE';
GRANT ALL PRIVILEGES ON DATABASE hotwheels TO hotwheels_user;
\q
```

Set `.env` values:

```env
DB_DRIVER=postgresql
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=hotwheels
DB_USER=hotwheels_user
DB_PASSWORD=STRONG_PASSWORD_HERE
```

---

## 4) Build frontend for production

```bash
cd /var/www/hotwheels
npm run build
```

This generates static files in `dist/`.

---

## 5) Run backend with systemd (production)

Create service file:

```bash
sudo nano /etc/systemd/system/hotwheels-backend.service
```

Paste:

```ini
[Unit]
Description=Hotwheels FastAPI Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/hotwheels
EnvironmentFile=/var/www/hotwheels/.env
ExecStart=/var/www/hotwheels/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Set permissions and start:

```bash
sudo chown -R www-data:www-data /var/www/hotwheels
sudo systemctl daemon-reload
sudo systemctl enable hotwheels-backend
sudo systemctl start hotwheels-backend
sudo systemctl status hotwheels-backend
```

Logs:

```bash
journalctl -u hotwheels-backend -f
```

---

## 6) Nginx config (frontend + backend API)

Create site config:

```bash
sudo nano /etc/nginx/sites-available/hotwheels
```

Paste (replace `yourdomain.com`):

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    root /var/www/hotwheels/dist;
    index index.html;

    location / {
        try_files $uri /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://127.0.0.1:8000/health;
    }
}
```

Enable site and reload:

```bash
sudo ln -s /etc/nginx/sites-available/hotwheels /etc/nginx/sites-enabled/hotwheels
sudo nginx -t
sudo systemctl reload nginx
```

---

## 7) Enable HTTPS

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Auto-renew check:

```bash
sudo certbot renew --dry-run
```

---

## 8) Full working verification checklist

Run all checks:

```bash
# Backend service
systemctl status hotwheels-backend --no-pager

# Backend health endpoint
curl -i http://127.0.0.1:8000/health

# Public health through nginx
curl -i http://yourdomain.com/health

# Frontend served by nginx
curl -I http://yourdomain.com
```

Expected:

- backend service is `active (running)`
- `/health` returns `{"status":"ok"}`
- domain serves `index.html`

---

## 9) Update/deploy new versions

```bash
cd /var/www/hotwheels
git pull
npm ci
npm run build

cd backend
source .venv/bin/activate
pip install -r requirements.txt
cd ..

sudo systemctl restart hotwheels-backend
sudo systemctl reload nginx
```

---

## 10) Troubleshooting

### Backend not starting

```bash
journalctl -u hotwheels-backend -n 200 --no-pager
```

Common issues:

- missing python packages in `backend/.venv`
- invalid `.env`
- wrong `WorkingDirectory` in systemd service

### 502 Bad Gateway

- backend is not running on `127.0.0.1:8000`
- verify with `curl http://127.0.0.1:8000/health`

### Frontend routes return 404 on refresh

- `try_files $uri /index.html;` missing in nginx root location

