import json
import requests
import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MCP server configurations
MCP_SERVERS = {
    "keyvalue": {"url": "http://localhost:8000", "description": "Key-value storage operations"},
    "calc": {"url": "http://localhost:8002", "description": "Calculator operations"},
    "weather": {"url": "http://localhost:8003", "description": "Weather information"}
}

# Function to get available tools from all MCP servers and format for Groq
def get_all_mcp_tools():
    all_tools = []
    
    for server_name, server_info in MCP_SERVERS.items():
        try:
            response = requests.post(f"{server_info['url']}/mcp/tools", json={})
            mcp_tools = response.json().get("tools", [])
            
            # Format tools for Groq API
            for tool in mcp_tools:
                groq_tool = {
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": f"[{server_name.upper()}] {tool.get('description', '')}",
                        "parameters": tool["parameters"]
                    }
                }
                all_tools.append(groq_tool)
                
            print(f"Connected to {server_name} server: {len(mcp_tools)} tools found")
        except Exception as e:
            print(f"Error connecting to {server_name} server: {e}")
    
    return all_tools

# Function to invoke an MCP tool
def invoke_mcp_tool(tool_name, parameters):
    # Determine which server to use based on tool name prefix
    server_name = None
    for prefix in ["keyvalue___", "calc___", "weather___"]:
        if tool_name.startswith(prefix):
            server_name = prefix.replace("___", "")
            break
    
    if not server_name or server_name not in MCP_SERVERS:
        return {"error": f"Unknown tool prefix in {tool_name}"}
    
    server_url = MCP_SERVERS[server_name]["url"]
    
    try:
        response = requests.post(f"{server_url}/mcp/invoke", json={
            "name": tool_name,
            "parameters": parameters
        })
        return response.json()
    except Exception as e:
        return {"error": f"Error invoking tool: {str(e)}"}

def main():
    # Get API key from .env file
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY not found in .env file")
        return
    
    # Initialize Groq client
    client = Groq(api_key=api_key)
    
    # Get available tools from all MCP servers
    tools = get_all_mcp_tools()
    if not tools:
        print("Failed to get tools from any MCP server. Make sure at least one server is running.")
        return
    
    # Extract tool names for display
    tool_names = [tool["function"]["name"] for tool in tools]
    
    print("\nConnected to Groq API")
    print(f"Total available tools: {len(tools)}")
    print("Type 'exit' to quit")
    
    # Chat loop
    messages = [
        {
            "role": "system", 
            "content": f"""You are an AI assistant with access to multiple tool sets:

1. Key-Value Store (keyvalue___*):
   - keyvalue___set: Store a value with a key
   - keyvalue___get: Retrieve a value by key
   - keyvalue___list: List all stored keys

2. Calculator (calc___*):
   - calc___add: Add two numbers
   - calc___subtract: Subtract second number from first
   - calc___multiply: Multiply two numbers
   - calc___divide: Divide first number by second
   - calc___sqrt: Calculate square root of a number

3. Weather Information (weather___*):
   - weather___current: Get current weather for a city
   - weather___forecast: Get weather forecast for a city
   - weather___cities: List available cities

Choose the appropriate tool based on the user's request.
"""
        }
    ]
    
    while True:
        # Get user input
        user_input = input("\nYou: ")
        if user_input.lower() == "exit":
            break
        
        # Add user message to conversation
        messages.append({"role": "user", "content": user_input})
        
        try:
            # Call Groq API with function calling
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=messages,
                tools=tools,
                tool_choice="auto",
                max_tokens=1000
            )
            
            # Process the response
            message = response.choices[0].message
            
            # Check if the model wants to call a tool
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    # Extract tool name and parameters
                    tool_name = tool_call.function.name
                    tool_params = json.loads(tool_call.function.arguments)
                    
                    print(f"[Tool Call] {tool_name} with parameters: {tool_params}")
                    
                    # Call the MCP tool
                    tool_result = invoke_mcp_tool(tool_name, tool_params)
                    
                    # Add the tool call and result to the conversation
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "type": "function",
                                "function": {
                                    "name": tool_name,
                                    "arguments": json.dumps(tool_params)
                                }
                            }
                        ]
                    })
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_result)
                    })
                
                # Get the final response after tool use
                response = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=messages,
                    max_tokens=1000
                )
                message = response.choices[0].message
            
            # Display the assistant's response
            print(f"AI: {message.content}")
            
            # Add the assistant's response to the conversation
            messages.append({"role": "assistant", "content": message.content})
            
        except Exception as e:
            print(f"Error: {e}")
            print("Continuing conversation...")

if __name__ == "__main__":
    main()