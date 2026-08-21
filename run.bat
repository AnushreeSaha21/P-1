@echo off
title FIU Depository Analytics

cd /d "%~dp0"

call myvenv\Scripts\activate.bat

start "" http://localhost:4444

streamlit run frontend\app.py --server.port 4444