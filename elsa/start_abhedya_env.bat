@echo off
title 🛰️ ABHEDYA - Secure Startup & Shutdown (improved)
color 0E
setlocal

REM ---------- CONFIG ----------
set KAFKA_HOME=C:\kafka\kafka
set KAFKA_LOGDIR=C:\kafka\data\kafka-logs
set ZK_CFG=%KAFKA_HOME%\config\zookeeper.properties
set SERVER_CFG=%KAFKA_HOME%\config\server.properties
set PROJECT_DIR=C:\Users\Mithil K Gowda\OneDrive\Desktop\PROJECT 7TH SEM\PROJECT
REM ----------------------------

echo ==================================================
echo        🚀 Launching ABHEDYA Secure System (safe)
echo ==================================================

REM -------------------------
REM Ensure kafka/zookeeper not already running
REM -------------------------
call :ensure_kafka_stopped

echo [PRECHECK] Ensuring log dir exists and permissions...
if not exist "%KAFKA_LOGDIR%" (
  mkdir "%KAFKA_LOGDIR%"
)
icacls "%KAFKA_LOGDIR%" /grant "%USERNAME%:(OI)(CI)F" /T >nul 2>&1

echo [PRECHECK] Stopping lingering kafka-python test clients (if any)...
REM -------------------------
REM <<< ADDED: kill lingering kafka-python clients >>>
REM This block kills processes whose command-line contains "kafka-python".
REM -------------------------
for /f "tokens=2 delims== " %%p in ('wmic process where "CommandLine like '%%kafka-python%%'" get ProcessId /format:list ^| find "ProcessId"') do (
  echo Killing kafka-python PID %%p
  taskkill /F /PID %%p >nul 2>&1
)
REM If you want to also kill all python processes (dangerous), uncomment the next block
REM for /f "tokens=2 delims== " %%q in ('wmic process where "Name='python.exe' or Name='pythonw.exe'" get ProcessId /format:list ^| find "ProcessId"') do (
REM   echo Killing python PID %%q
REM   taskkill /F /PID %%q >nul 2>&1
REM )

echo ==================================================
echo [0/6] ⚠️  Please ensure Windows Defender and OneDrive have an exclusion for:
echo         - %KAFKA_HOME%
echo         - %KAFKA_LOGDIR%
echo         (Windows Security -> Virus & threat protection -> Manage settings -> Add an exclusion -> Folder)
echo ==================================================
echo.

REM === Step 1: Start ZooKeeper ===
echo [1/6] 🦓 Starting ZooKeeper...
start "ZooKeeper" cmd /k "cd /d %KAFKA_HOME% && bin\windows\zookeeper-server-start.bat %ZK_CFG%"

echo Waiting for ZooKeeper to bind port 2181...
setlocal enabledelayedexpansion
set /a tries=0
set found=0
:wait_zk
timeout /t 1 /nobreak >nul
set found=0
for /f "tokens=*" %%A in ('netstat -ano ^| findstr ":2181"') do set found=1
if "%found%"=="1" (
  echo ZooKeeper appears to be listening on port 2181.
) else (
  set /a tries+=1
  if %tries% GEQ 30 (
    echo WARNING: ZooKeeper not detected on port 2181 after 30s. Proceeding anyway...
  ) else goto wait_zk
)
endlocal

REM === Step 2: Clean old broker registration (safe conditional) ===
echo [2/6] 🧹 Checking /brokers/ids in ZooKeeper (will delete only if node exists)...
REM -------------------------
REM <<< REPLACED: unconditional deleteall /brokers/ids/0 >>>
REM This snippet checks the ZK list and deletes /brokers/ids/0 only if present.
REM -------------------------
set zkls=
for /f "delims=" %%L in ('echo ls /brokers/ids ^| "%KAFKA_HOME%\bin\windows\zookeeper-shell.bat" localhost:2181 2^>nul ^| findstr /r /c:"^\[" /c:"^/" /c:"^Error"') do set zkls=%%L
echo ZooKeeper ls output: %zkls%
echo %zkls% | findstr /C:"0" >nul 2>&1
if %errorlevel% equ 0 (
  echo Broker id 0 present in ZK — removing it safely...
  echo deleteall /brokers/ids/0 | "%KAFKA_HOME%\bin\windows\zookeeper-shell.bat" localhost:2181
) else (
  echo Broker id 0 not present in ZK — skipping delete.
)

REM === Step 3: Start Kafka Broker ===
echo [3/6] 🧠 Starting Kafka Broker...
REM -------------------------
REM <<< IMPORTANT ADDED: use --override log.dirs to force Kafka to use %KAFKA_LOGDIR% >>>
REM This avoids mismatch between server.properties and the script.
REM -------------------------
start "Kafka Server" cmd /k "cd /d %KAFKA_HOME% && bin\windows\kafka-server-start.bat %SERVER_CFG% --override log.dirs=%KAFKA_LOGDIR%"

echo Waiting for Kafka to bind port 9092...
set /a tries=0
set kfound=0
:wait_kafka
timeout /t 1 /nobreak >nul
set kfound=0
for /f "tokens=*" %%A in ('netstat -ano ^| findstr ":9092"') do set kfound=1
if "%kfound%"=="1" (
  echo Kafka appears to be listening on port 9092.
) else (
  set /a tries+=1
  if %tries% GEQ 30 (
    echo WARNING: Kafka not detected on port 9092 after 30s. Check logs if needed.
  ) else goto wait_kafka
)

REM === Step 4: Activate Python Env ===
echo [4/6] 🧩 Activating Python virtual environment...
cd /d "%PROJECT_DIR%"
call venv\Scripts\activate

echo ==================================================
echo ✅ Kafka and ZooKeeper started (or at least listening).
echo ==================================================
echo.
echo ⚙️  Now open VS Code and run:
echo     venv\Scripts\activate
echo     python app.py
echo.
echo 🔸 Keep this window open while testing.
echo 🔸 When done press any key to run a graceful shutdown (below).
pause >nul

REM ---------- Shutdown sequence ----------
echo ==================================================
echo 🔻 Initiating safe shutdown for ABHEDYA system...
echo ==================================================

REM === Stop Kafka gracefully ===
echo [1/3] 📴 Stopping Kafka Broker (graceful)...
cd /d %KAFKA_HOME%
call bin\windows\kafka-server-stop.bat
REM wait a bit for graceful exit (10s)
timeout /t 10 /nobreak >nul

REM If Kafka JVM still exists and contains kafka-server-start in the command line, kill it specifically
for /f "tokens=*" %%P in ('wmic process where "CommandLine like '%%kafka-server-start%%'" get ProcessId ^| findstr /r /v "^$"') do (
  if NOT "%%P"=="" (
    echo Killing leftover Kafka java PID %%P
    taskkill /F /PID %%P /T >nul 2>&1
  )
)

REM === Stop ZooKeeper gracefully ===
echo [2/3] 💤 Stopping ZooKeeper server (graceful)...
call bin\windows\zookeeper-server-stop.bat
timeout /t 5 /nobreak >nul

REM Kill any ZK java process whose command line contains zookeeper-server-start
for /f "tokens=*" %%Q in ('wmic process where "CommandLine like '%%zookeeper-server-start%%'" get ProcessId ^| findstr /r /v "^$"') do (
  if NOT "%%Q"=="" (
    echo Killing leftover ZooKeeper java PID %%Q
    taskkill /F /PID %%Q /T >nul 2>&1
  )
)

REM === Diagnostic: if Kafka reported file-lock errors previously, show potential lockers ===
echo [DIAG] Checking for known problem files and locks...
set problemFile=%KAFKA_LOGDIR%\network-traffic-0\00000000000000000000.timeindex
if exist "%problemFile%" (
  echo Problem file exists: %problemFile%
  REM If you have Sysinternals handle.exe in the script folder, it will be used. Place handle.exe beside this .bat
  if exist "%~dp0handle.exe" (
    echo Running handle.exe to show processes that hold the file...
    "%~dp0handle.exe" "%problemFile%"
  ) else (
    echo handle.exe not found in the script folder.
    echo Download Sysinternals handle.exe and place it next to this .bat, or use Resource Monitor (resmon) -> CPU -> Associated Handles -> search for the filename.
  )
) else (
  echo Problem file not present; no lock check needed.
)

REM === Deactivate Python environment ===
echo [3/3] 🔒 Deactivating Python environment...
call venv\Scripts\deactivate

echo ==================================================
echo ✅ All ABHEDYA components shut down safely!
echo ==================================================
pause
endlocal
exit /b 0

REM -------------------------
REM Helper: ensure no kafka/zookeeper JVMs are running (for startup precheck)
REM -------------------------
:ensure_kafka_stopped
echo [ensure_kafka_stopped] Looking for kafka & zookeeper JVMs and killing them...
for /f "tokens=2 delims== " %%j in ('wmic process where "CommandLine like '%%kafka-server-start%%' or CommandLine like '%%zookeeper-server-start%%'" get ProcessId /format:list ^| find "ProcessId"') do (
  if NOT "%%j"=="" (
    echo Killing PID %%j
    taskkill /F /PID %%j /T >nul 2>&1
  )
)
goto :eof
