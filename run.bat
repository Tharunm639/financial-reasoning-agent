@echo off
echo Starting FinSight AI...
cd /d e:\financial-reasoning-agent
call venv\Scripts\activate
streamlit run main.py
pause
