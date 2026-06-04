@echo off
title OSCA Desk Engine System Portal
:: Force reset the working path to the proper directory environment
cd /d "C:\Users\Jake\Desktop\SeniorCitizenInformationSystem"

:: Wake up the virtual environment layer quietly
call "C:\Users\Jake\Desktop\SeniorCitizenInformationSystem\venv\Scripts\activate.bat"

:: Move directly into the primary django project root directory
cd /d "C:\Users\Jake\Desktop\SeniorCitizenInformationSystem\osca_system"

:: Trigger the default browser window straight to the direct login node
start http://127.0.0.1:8000/dashboard/login/

:: Boot up the background database processing server engine
python manage.py runserver