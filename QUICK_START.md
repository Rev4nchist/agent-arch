# Quick Start Guide - Reverse Proxy Setup

## TL;DR - Get Started in 3 Steps

```bash
# 1. Copy environment template
cp .env.example .env
# (Edit .env with your Azure credentials)

# 2. Start everything
docker-compose up --build

# 3. Open browser
http://localhost:8080
```

**That's it! No CORS configuration needed! 🎉**

---

## What Changed?

### Before (CORS Problems)
```
Browser → localhost:3008 (Frontend)
              ↓
              localhost:8001 (Backend)
              ↓
              ❌ CORS ERROR - Different ports!
```

### After (No CORS)
```
Browser → localhost:8080 (Everything!)
              ├─→ /     = Frontend
              └─→ /api  = Backend
              ✅ Same origin, no CORS!
```

---

## Convenient Scripts

### Windows
```bash
start-dev.bat     # Start with reverse proxy (recommended)
debug-cors.bat    # Debug CORS issues if they occur
```

### Mac/Linux
```bash
./start-dev.sh    # Start with reverse proxy (recommended)
```

---

## Manual Setup (If Not Using Docker)

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8001
```

### Frontend
```bash
cd frontend
npm install
set PORT=3008 && npm run dev  # Windows
PORT=3008 npm run dev         # Mac/Linux
```

**⚠️ Requires CORS configuration in:**
- `backend/.env`: `CORS_ORIGINS=http://localhost:3008`
- `frontend/.env`: `NEXT_PUBLIC_API_URL=http://localhost:8001`

---

## URLs Reference

### With Docker (Reverse Proxy)
- **Everything:** http://localhost:8080
- **Frontend:** http://localhost:8080/
- **Backend API:** http://localhost:8080/api
- **Health Check:** http://localhost:8080/health

### Without Docker (Manual)
- **Frontend:** http://localhost:3008
- **Backend:** http://localhost:8001
- **Backend API:** http://localhost:8001/api
- **Health Check:** http://localhost:8001/health

---

## Troubleshooting

### CORS Error Still Appearing?
```bash
# Run debugging script
debug-cors.bat  # Windows
```

**Common false CORS errors:**
1. Backend crashed → Shows as CORS
2. Network timeout → Shows as CORS
3. Wrong API URL → Shows as CORS

**Always check backend logs first!**

### Port Already in Use
```bash
# Option 1: Find and stop the process
netstat -ano | findstr :8080  # Windows
lsof -i :8080                 # Mac/Linux

# Option 2: Change port in docker-compose.yml
# reverse-proxy:
#   ports:
#     - "9090:80"  # Use different port
```

### Hot Reload Not Working
```bash
docker-compose down
docker-compose up --build
```

---

## Documentation

- Full setup guide: [docs/REVERSE_PROXY_SETUP.md](docs/REVERSE_PROXY_SETUP.md)
- Architecture decisions: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- CORS debugging: Run `debug-cors.bat`

---

## Why This Works

Based on real-world recommendations:
- ✅ Reverse proxy = Production pattern (nginx, Azure Front Door)
- ✅ Single origin = No CORS complexity
- ✅ JWT auth = No cookie CORS issues
- ✅ Team consistency = Same setup for everyone

**Reference:** [David Fowler's CORS thread analysis](learning-resources/CORS-issues.md)
