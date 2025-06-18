import json
import http.server
import socketserver
import math
import sys
from urllib.parse import urlparse

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
                        "name": "calc___add",
                        "description": "Add two numbers",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "a": {"type": "number", "description": "First number"},
                                "b": {"type": "number", "description": "Second number"}
                            },
                            "required": ["a", "b"]
                        }
                    },
                    {
                        "name": "calc___subtract",
                        "description": "Subtract second number from first",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "a": {"type": "number", "description": "First number"},
                                "b": {"type": "number", "description": "Second number"}
                            },
                            "required": ["a", "b"]
                        }
                    },
                    {
                        "name": "calc___multiply",
                        "description": "Multiply two numbers",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "a": {"type": "number", "description": "First number"},
                                "b": {"type": "number", "description": "Second number"}
                            },
                            "required": ["a", "b"]
                        }
                    },
                    {
                        "name": "calc___divide",
                        "description": "Divide first number by second",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "a": {"type": "number", "description": "First number (dividend)"},
                                "b": {"type": "number", "description": "Second number (divisor)"}
                            },
                            "required": ["a", "b"]
                        }
                    },
                    {
                        "name": "calc___sqrt",
                        "description": "Calculate square root of a number",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "n": {"type": "number", "description": "Number to find square root of"}
                            },
                            "required": ["n"]
                        }
                    }
                ]
            }
        elif path == "/mcp/invoke":
            # Handle tool invocation - this is how the LLM calls the tools
            tool_name = request.get("name", "")
            parameters = request.get("parameters", {})
            
            if tool_name == "calc___add":
                a = parameters.get("a")
                b = parameters.get("b")
                if a is not None and b is not None:
                    try:
                        result = float(a) + float(b)
                        response = {"result": result}
                    except Exception as e:
                        response = {"error": f"Error calculating: {str(e)}"}
                else:
                    response = {"error": "Missing a or b parameters"}
            
            elif tool_name == "calc___subtract":
                a = parameters.get("a")
                b = parameters.get("b")
                if a is not None and b is not None:
                    try:
                        result = float(a) - float(b)
                        response = {"result": result}
                    except Exception as e:
                        response = {"error": f"Error calculating: {str(e)}"}
                else:
                    response = {"error": "Missing a or b parameters"}
            
            elif tool_name == "calc___multiply":
                a = parameters.get("a")
                b = parameters.get("b")
                if a is not None and b is not None:
                    try:
                        result = float(a) * float(b)
                        response = {"result": result}
                    except Exception as e:
                        response = {"error": f"Error calculating: {str(e)}"}
                else:
                    response = {"error": "Missing a or b parameters"}
            
            elif tool_name == "calc___divide":
                a = parameters.get("a")
                b = parameters.get("b")
                if a is not None and b is not None:
                    try:
                        if float(b) == 0:
                            response = {"error": "Division by zero"}
                        else:
                            result = float(a) / float(b)
                            response = {"result": result}
                    except Exception as e:
                        response = {"error": f"Error calculating: {str(e)}"}
                else:
                    response = {"error": "Missing a or b parameters"}
            
            elif tool_name == "calc___sqrt":
                n = parameters.get("n")
                if n is not None:
                    try:
                        if float(n) < 0:
                            response = {"error": "Cannot calculate square root of negative number"}
                        else:
                            result = math.sqrt(float(n))
                            response = {"result": result}
                    except Exception as e:
                        response = {"error": f"Error calculating: {str(e)}"}
                else:
                    response = {"error": "Missing n parameter"}
        
        # Send response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

def run_server(port=8000):
    with socketserver.TCPServer(("", port), MCPHandler) as httpd:
        print(f"Calculator MCP server running at http://localhost:{port}")
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