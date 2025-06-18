import json
import http.server
import socketserver
import random
import sys
from urllib.parse import urlparse
from datetime import datetime, timedelta

# Simulated weather data (no real API calls)
CITIES = {
    "new york": {"country": "USA", "latitude": 40.7128, "longitude": -74.0060},
    "london": {"country": "UK", "latitude": 51.5074, "longitude": -0.1278},
    "tokyo": {"country": "Japan", "latitude": 35.6762, "longitude": 139.6503},
    "paris": {"country": "France", "latitude": 48.8566, "longitude": 2.3522},
    "sydney": {"country": "Australia", "latitude": -33.8688, "longitude": 151.2093},
}

WEATHER_CONDITIONS = ["sunny", "partly cloudy", "cloudy", "rainy", "thunderstorm", "snowy", "windy", "foggy"]

class MCPHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        # Get the request data
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        request = json.loads(post_data)
        
        # Parse the path to determine the endpoint
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        response = {"error": "Unknown endpoint"}
        
        # Handle MCP endpoints
        if path == "/mcp/tools":
            # Return available tools - this is how the LLM discovers what tools are available
            response = {
                "tools": [
                    {
                        "name": "weather___current",
                        "description": "Get current weather for a city (simulated data)",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "city": {"type": "string", "description": "City name"}
                            },
                            "required": ["city"]
                        }
                    },
                    {
                        "name": "weather___forecast",
                        "description": "Get weather forecast for a city (simulated data)",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "city": {"type": "string", "description": "City name"},
                                "days": {"type": "integer", "description": "Number of days (1-7)"}
                            },
                            "required": ["city"]
                        }
                    },
                    {
                        "name": "weather___cities",
                        "description": "List available cities",
                        "parameters": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                ]
            }
        elif path == "/mcp/invoke":
            # Handle tool invocation - this is how the LLM calls the tools
            tool_name = request.get("name", "")
            parameters = request.get("parameters", {})
            
            if tool_name == "weather___current":
                city = parameters.get("city", "").lower()
                if city:
                    if city in CITIES:
                        # Generate simulated weather data
                        temp_c = round(random.uniform(5, 35), 1)
                        temp_f = round(temp_c * 9/5 + 32, 1)
                        condition = random.choice(WEATHER_CONDITIONS)
                        humidity = random.randint(30, 95)
                        wind_speed = round(random.uniform(0, 30), 1)
                        
                        response = {
                            "result": {
                                "city": city.title(),
                                "country": CITIES[city]["country"],
                                "temperature_c": temp_c,
                                "temperature_f": temp_f,
                                "condition": condition,
                                "humidity": humidity,
                                "wind_speed_kph": wind_speed,
                                "timestamp": datetime.now().isoformat()
                            }
                        }
                    else:
                        response = {"error": f"City '{city}' not found. Use weather___cities to see available cities."}
                else:
                    response = {"error": "Missing city parameter"}
            
            elif tool_name == "weather___forecast":
                city = parameters.get("city", "").lower()
                days = min(int(parameters.get("days", 3)), 7)  # Default 3 days, max 7
                
                if city:
                    if city in CITIES:
                        # Generate simulated forecast
                        forecast = []
                        for i in range(days):
                            date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
                            temp_high = round(random.uniform(10, 35), 1)
                            temp_low = round(random.uniform(0, temp_high-2), 1)
                            condition = random.choice(WEATHER_CONDITIONS)
                            
                            forecast.append({
                                "date": date,
                                "high_c": temp_high,
                                "low_c": temp_low,
                                "high_f": round(temp_high * 9/5 + 32, 1),
                                "low_f": round(temp_low * 9/5 + 32, 1),
                                "condition": condition,
                                "precipitation_chance": random.randint(0, 100)
                            })
                        
                        response = {
                            "result": {
                                "city": city.title(),
                                "country": CITIES[city]["country"],
                                "forecast": forecast
                            }
                        }
                    else:
                        response = {"error": f"City '{city}' not found. Use weather___cities to see available cities."}
                else:
                    response = {"error": "Missing city parameter"}
            
            elif tool_name == "weather___cities":
                cities_info = {}
                for city, info in CITIES.items():
                    cities_info[city.title()] = info
                
                response = {"result": cities_info}
        
        # Send response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

def run_server(port=8000):
    with socketserver.TCPServer(("", port), MCPHandler) as httpd:
        print(f"Weather MCP server running at http://localhost:{port}")
        httpd.serve_forever()

if __name__ == "__main__":
    # Get port from command line argument if provided
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}")
            sys.exit(1)
    
    run_server(port)