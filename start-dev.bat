@echo off
REM Development startup script with reverse proxy (No CORS issues!)

echo ========================================
echo Agent Architecture Dev Environment
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo ✅ Docker is running
echo.

REM Check if .env exists
if not exist .env (
    echo ⚠️  .env file not found!
    echo.
    echo Creating .env from template...
    if exist .env.example (
        copy .env.example .env
        echo ✅ Created .env file
        echo.
        echo 🔧 IMPORTANT: Edit .env with your Azure credentials before continuing!
        echo.
        pause
        notepad .env
    ) else (
        echo ❌ .env.example not found. Please create .env manually.
        pause
        exit /b 1
    )
)

echo ✅ .env file exists
echo.

echo Starting services with Docker Compose...
echo.
echo 📍 Frontend + Backend + Reverse Proxy
echo 🌐 Access at: http://localhost:8080
echo 📊 Backend API: http://localhost:8080/api
echo.
echo Press Ctrl+C to stop all services
echo.

docker-compose up --build

pause
