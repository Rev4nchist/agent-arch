# Reverse Proxy Setup Guide

## What Problem Does This Solve?

**CORS (Cross-Origin Resource Sharing) errors** happen when your browser blocks requests between different ports:
- Frontend at `localhost:3008`
- Backend at `localhost:8001`
- Browser: "Different ports = different websites = BLOCKED!" 🚫

**Solution:** Use a reverse proxy to serve everything from **one port** (`localhost:8080`)

---

## How It Works (Simple Explanation)

### Without Reverse Proxy (CORS Problems)
```
Browser → localhost:3008 (Frontend)
              ↓
              Tries to call localhost:8001 (Backend)
              ↓
              ❌ CORS ERROR - Different origins!
```

### With Reverse Proxy (No CORS!)
```
Browser → localhost:8080 (Reverse Proxy)
              ↓
              ├─→ /api/* → Backend (hidden at port 8001)
              └─→ /*     → Frontend (hidden at port 3000)
              ↓
              ✅ Same origin, no CORS!
```

Think of it like a **hotel concierge**:
- You only see the front desk (port 8080)
- The concierge routes your requests to the right department
- You never need to know about the different departments (ports)

---

## Quick Start

### Option 1: Using Docker (Recommended - Zero CORS Issues)

```bash
# 1. Make sure .env file exists with your Azure credentials
cp .env.example .env
# Edit .env with your actual values

# 2. Start everything with one command
docker-compose up --build

# 3. Open your browser
http://localhost:8080

# That's it! No CORS configuration needed! 🎉
```

**What happens:**
- Nginx reverse proxy starts on port 8080
- Frontend runs on internal port 3000 (not exposed)
- Backend runs on internal port 8001 (not exposed)
- Everything accessible via `localhost:8080`

### Option 2: Manual Setup (Requires CORS Config)

```bash
# Terminal 1 - Backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8001

# Terminal 2 - Frontend
cd frontend
npm install
PORT=3008 npm run dev

# Terminal 3 - No reverse proxy, so CORS must be configured in:
# - backend/src/main.py (CORS_ORIGINS)
# - frontend/.env (NEXT_PUBLIC_API_URL)
```

---

## File Structure

```
agent-arch/
├── docker-compose.yml       # Orchestrates all services
├── nginx.conf              # Reverse proxy routing rules
├── .env                    # Azure credentials (not in git)
├── backend/
│   ├── Dockerfile          # Backend container config
│   └── src/
│       └── main.py         # FastAPI app
└── frontend/
    ├── Dockerfile          # Frontend container config
    └── ...
```

---

## Nginx Configuration Explained

```nginx
# When browser requests localhost:8080/
location / {
    proxy_pass http://frontend;  # → Send to Next.js (port 3000)
}

# When browser requests localhost:8080/api/meetings
location /api {
    proxy_pass http://backend;   # → Send to FastAPI (port 8001)
}
```

**Result:** Browser thinks everything is from `localhost:8080`, no CORS needed!

---

## Common Commands

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Rebuild after code changes
docker-compose up --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## Troubleshooting

### "Cannot connect to Docker daemon"
```bash
# Make sure Docker Desktop is running
# Windows: Check system tray
# Mac: Check menu bar
```

### "Port 8080 already in use"
```bash
# Find what's using port 8080
netstat -ano | findstr :8080  # Windows
lsof -i :8080                 # Mac/Linux

# Either stop that process or change port in docker-compose.yml:
# reverse-proxy:
#   ports:
#     - "9090:80"  # Use 9090 instead
```

### "Backend not connecting to Cosmos DB"
```bash
# Check .env file has correct values
cat .env

# Check backend logs
docker-compose logs backend

# Common issues:
# - COSMOS_ENDPOINT missing https://
# - COSMOS_KEY has extra spaces/newlines
# - Wrong DATABASE_NAME
```

### Hot Reload Not Working
```bash
# Volume mounts allow code changes to reflect immediately
# If not working, rebuild:
docker-compose down
docker-compose up --build
```

---

## Why This Matches Production

Most production setups use reverse proxies (nginx, Azure Front Door, Cloudflare):

```
Production:
  yourdomain.com       → Nginx/Front Door
    ├─→ /            → Frontend (static files or Next.js)
    └─→ /api         → Backend (API server)

Development (with Docker):
  localhost:8080       → Nginx
    ├─→ /            → Frontend container
    └─→ /api         → Backend container
```

**Same architecture** = No surprises when deploying!

---

## Benefits Summary

✅ **No CORS issues** - Same origin for everything
✅ **Production parity** - Matches real deployment architecture
✅ **Simpler debugging** - CORS errors won't mask real issues
✅ **Team consistency** - Everyone uses same setup
✅ **Azure Front Door ready** - Similar to production CDN routing

---

## Next Steps

1. ✅ Start with Docker setup (easiest)
2. ✅ Verify http://localhost:8080 works
3. ✅ Test API calls work (check DevTools Network tab)
4. ✅ Make code changes, verify hot reload works
5. ✅ Document any team-specific setup steps

---

## References

- Based on recommendations from David Fowler's CORS thread
- Production patterns: nginx, Azure Front Door, Cloudflare
- JWT authentication (no cookie CORS complexity)
