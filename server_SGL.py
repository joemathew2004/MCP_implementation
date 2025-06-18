import json
import http.server
import socketserver
import sys
from urllib.parse import urlparse

# Simple in-memory key-value store
kv_store = {}

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
                        "name": "keyvalue___set",
                        "description": "Set a value for a key in the key-value store",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "key": {"type": "string", "description": "The key to set"},
                                "value": {"type": "string", "description": "The value to store"}
                            },
                            "required": ["key", "value"]
                        }
                    },
                    {
                        "name": "keyvalue___get",
                        "description": "Get a value for a key from the key-value store",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "key": {"type": "string", "description": "The key to retrieve"}
                            },
                            "required": ["key"]
                        }
                    },
                    {
                        "name": "keyvalue___list",
                        "description": "List all keys in the key-value store",
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
            
            if tool_name == "keyvalue___set":
                key = parameters.get("key")
                value = parameters.get("value")
                if key and value:
                    kv_store[key] = value
                    response = {"result": f"Key '{key}' set successfully"}
                else:
                    response = {"error": "Missing key or value parameters"}
            
            elif tool_name == "keyvalue___get":
                key = parameters.get("key")
                if key:
                    if key in kv_store:
                        response = {"result": kv_store[key]}
                    else:
                        response = {"error": f"Key '{key}' not found"}
                else:
                    response = {"error": "Missing key parameter"}
            
            elif tool_name == "keyvalue___list":
                response = {"result": list(kv_store.keys())}
        
        # Send response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

def run_server(port=8000):
    with socketserver.TCPServer(("", port), MCPHandler) as httpd:
        print(f"KeyValue MCP server running at http://localhost:{port}")
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