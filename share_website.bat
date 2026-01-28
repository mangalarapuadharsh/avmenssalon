@echo off
title Share Website - Public Link Generator
color 0A

echo ===================================================
echo       AV Mens Salon - Website Sharing Tool
echo ===================================================
echo.
echo  [INFO] This tool will generate a public link for your
echo         local server running on Port 5000.
echo.
echo  [INSTRUCTIONS]
echo  1. Make sure your BACKEND SERVER is running in another window!
echo     (Run 'start_server.bat' first)
echo  2. Look for the URL below (e.g., https://...localhost.run)
echo  3. Copy that link and send it to your friend.
echo  4. DO NOT CLOSE THIS WINDOW while they are using it.
echo.
echo ===================================================
echo.
echo Connecting to public tunnel service...
echo (If asked 'Are you sure...', type yes and press Enter)
echo.

ssh -i id_ed25519 -o StrictHostKeyChecking=no -R 80:127.0.0.1:5000 localhost.run

echo.
echo [Connection Closed]
pause
