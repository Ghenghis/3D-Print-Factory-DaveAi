@echo off
title DaveAI Local Agent
cd /d "%~dp0..\.."
echo =============================================
echo  DaveAI 3D Print Factory — Local Agent
echo =============================================
echo.
echo Starting local agent runner...
echo All proof gates will execute automatically.
echo Do NOT close this window until complete.
echo.
python -m local_agent.runner
if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Local agent exited with code %ERRORLEVEL%
    echo Check proof/windsurf/local-agent/local-agent-startup.log
)
echo.
echo Done. Check proof/windsurf/final/WINDSURF_FINAL_VERDICT.md
pause
