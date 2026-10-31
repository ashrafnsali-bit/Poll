@echo off
title Barber SaaS Server & Admin Dashboard
chcp 65001 > nul
echo ========================================================
echo        💈 تشغيل نظام Barber SaaS وقاعدة البيانات 💈
echo ========================================================
echo.
echo جاري بدء تشغيل السيرفر المحلي...
echo.
echo - صفحة الهبوط:      http://localhost:8000/
echo - لوحة التحكم:      http://localhost:8000/admin
echo.
echo اضغط Ctrl + C لإيقاف السيرفر في أي وقت.
echo ========================================================
start "" http://localhost:8000/
python app.py
pause

