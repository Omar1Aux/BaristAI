@echo off
cd /d C:\BaristAI

echo Starting optional InfluxDB for BaristAI...
echo.

set INFLUX_EXE=C:\BaristAI\influxdb3-core-3.9.3-windows_amd64\influxdb3.exe
set INFLUX_DATA=C:\BaristAI\influxdb_data

echo Influx executable:
echo %INFLUX_EXE%
echo.
echo Data directory:
echo %INFLUX_DATA%
echo.

if not exist "%INFLUX_EXE%" (
    echo ERROR: influxdb3.exe was not found.
    echo Check this path:
    echo %INFLUX_EXE%
    pause
    exit /b 1
)

if not exist "%INFLUX_DATA%" (
    mkdir "%INFLUX_DATA%"
)

echo If you see "Failed to bind address", InfluxDB is already running.
echo In that case, close the old Influx window or kill the old process using the port.
echo.

"%INFLUX_EXE%" serve --node-id baristai --object-store file --data-dir "%INFLUX_DATA%"

echo.
echo InfluxDB stopped or failed.
pause
