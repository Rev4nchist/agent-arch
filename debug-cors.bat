@echo off
REM CORS Debugging Script
REM Based on insights from David Fowler's thread

echo ========================================
echo 🔍 CORS Issue Debugger
echo ========================================
echo.
echo ⚠️  IMPORTANT: CORS errors often MASK other problems!
echo.

echo Step 1: Check if backend is actually running
echo ----------------------------------------
curl -s http://localhost:8001/health
if errorlevel 1 (
    echo ❌ Backend is NOT responding!
    echo.
    echo Possible causes:
    echo - Backend not started
    echo - Backend crashed
    echo - Wrong port number
    echo - Firewall blocking connection
    echo.
    echo TIP: Check backend console for errors
    goto :end
) else (
    echo ✅ Backend is responding
)
echo.

echo Step 2: Check if frontend can reach backend
echo ----------------------------------------
curl -s http://localhost:8001/api/meetings >nul
if errorlevel 1 (
    echo ❌ Cannot reach /api/meetings endpoint
    echo.
    echo Possible causes:
    echo - Endpoint doesn't exist
    echo - Database not connected
    echo - Backend error (check logs!)
    goto :end
) else (
    echo ✅ Backend API is accessible
)
echo.

echo Step 3: Check environment configuration
echo ----------------------------------------
echo Frontend API URL:
findstr NEXT_PUBLIC_API_URL frontend\.env 2>nul
if errorlevel 1 (
    echo ⚠️  NEXT_PUBLIC_API_URL not found in frontend\.env
)
echo.
echo Backend CORS Origins:
findstr CORS_ORIGINS backend\.env 2>nul
if errorlevel 1 (
    echo ⚠️  CORS_ORIGINS not found in backend\.env
)
echo.

echo Step 4: Common CORS "False Positives"
echo ----------------------------------------
echo Real problem might be:
echo 1. Backend down/crashed → Shows as CORS error
echo 2. Network timeout → Shows as CORS error
echo 3. Gateway error (502/504) → Shows as CORS error
echo 4. Wrong API URL → Shows as CORS error
echo.
echo 💡 Always check backend logs BEFORE assuming CORS!
echo.

echo Step 5: Check Browser DevTools
echo ----------------------------------------
echo In Chrome/Edge DevTools (F12):
echo 1. Network tab
echo 2. Look for failed request
echo 3. Check "Status" column:
echo    - 0 or (failed) = Network/CORS
echo    - 4xx/5xx = Backend error (not CORS!)
echo 4. Check "Response" tab for actual error
echo.

:end
echo.
echo ========================================
echo For reverse proxy setup (eliminates CORS):
echo   docker-compose up
echo   Open: http://localhost:8080
echo ========================================
pause
