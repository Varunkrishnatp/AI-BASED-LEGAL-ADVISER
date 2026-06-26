@echo off
cd /d E:\zzz
start "" http://localhost:8501
call "E:\coding\python\python.exe" -m streamlit run streamlit_app.py
pause
