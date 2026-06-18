@echo off
cd /d C:\BaristAI\influxdb3-core-3.9.3-windows_amd64
influxdb3.exe serve --node-id baristai --object-store file --data-dir "C:\BaristAI\influxdb_data" --without-auth
pause