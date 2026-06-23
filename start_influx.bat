@echo off
setlocal
set "BARISTAI_DIR=%~dp0"
set "INFLUX_DIR=%BARISTAI_DIR%influxdb3-core-3.9.3-windows_amd64"
set "INFLUX_DATA_DIR=%BARISTAI_DIR%influxdb_data"

if not exist "%INFLUX_DIR%\influxdb3.exe" (
    echo InfluxDB executable not found at "%INFLUX_DIR%\influxdb3.exe".
    echo Download/extract InfluxDB 3 there, or set INFLUX_PATH for influx_writer.py.
    pause
    exit /b 1
)

cd /d "%INFLUX_DIR%"
influxdb3.exe serve --node-id baristai --object-store file --data-dir "%INFLUX_DATA_DIR%" --without-auth
pause
