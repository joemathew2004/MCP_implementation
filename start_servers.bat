@echo off
echo Starting MCP servers on different ports...

start cmd /k "title KeyValue MCP Server && python server_SGL.py"
timeout /t 2 > nul

start cmd /k "title Calculator MCP Server && python server_CALC.py 8002"
timeout /t 2 > nul

start cmd /k "title Weather MCP Server && python server_WEATHER.py 8003"
timeout /t 2 > nul

echo All servers started!
echo KeyValue server: http://localhost:8000
echo Calculator server: http://localhost:8002
echo Weather server: http://localhost:8003
echo.
echo Use multi_server_client.py to connect to all servers