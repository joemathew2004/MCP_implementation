# MCP (Model Context Protocol) Implementation

This project demonstrates a comprehensive implementation of the Model Context Protocol (MCP), which allows AI models to communicate with external tools through a standardized interface.

## What is MCP?

MCP is an open protocol that standardizes how applications provide context to large language models (LLMs). It enables communication between AI systems and locally running MCP servers that provide additional tools and resources to extend AI capabilities.

## Project Structure

### Servers
- `server_SGL.py` - Key-Value store server (Set, Get, List operations)
- `server_CALC.py` - Calculator server (add, subtract, multiply, divide, sqrt)
- `server_WEATHER.py` - Weather information server (current weather, forecast, cities)

### Clients
- `multi_server_client.py` - Main client that connects to multiple MCP servers and uses Groq API
- `groq_mcp_client.py` - Client that connects to a single MCP server using Groq API
- `llm_client.py` - Simple pattern-matching client (no external LLM API)
- `test_client.py` - Test client that demonstrates the MCP protocol flow

### Documentation
- `mcp_flow.md` - Detailed explanation of how MCP works
- `README.md` - This file

### Utilities
- `start_servers.bat` - Batch file to start all servers on different ports
- `.env` - Environment file for API keys (not included in repository)
- `requirements_groq.txt` - Dependencies for Groq integration

## Getting Started

1. Set up the virtual environment:
   ```
   # Create virtual environment
   python -m venv venv
   
   # Activate the virtual environment
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On macOS/Linux
   
   # Install dependencies
   pip install -r requirements_groq.txt
   ```

2. Create a `.env` file with your Groq API key:
   ```
   GROQ_API_KEY=your_api_key_here
   ```

3. Start the MCP servers (each on a different port):
   ```
   # On Windows
   .\start_servers.bat
   
   # Or start them individually
   python server_SGL.py
   python server_CALC.py 8002
   python server_WEATHER.py 8003
   ```

4. Run the multi-server client:
   ```
   python multi_server_client.py
   ```

## Available Tools

### Key-Value Store (port 8000)
- `keyvalue___set`: Store a value with a key
- `keyvalue___get`: Retrieve a value by key
- `keyvalue___list`: List all stored keys

### Calculator (port 8002)
- `calc___add`: Add two numbers
- `calc___subtract`: Subtract second number from first
- `calc___multiply`: Multiply two numbers
- `calc___divide`: Divide first number by second
- `calc___sqrt`: Calculate square root of a number

### Weather Information (port 8003)
- `weather___current`: Get current weather for a city (simulated)
- `weather___forecast`: Get weather forecast for a city (simulated)
- `weather___cities`: List available cities

## MCP Protocol Details

Each MCP server implements two main endpoints:

1. `/mcp/tools` - Returns a list of available tools
2. `/mcp/invoke` - Executes a tool with provided parameters

See `mcp_flow.md` for a detailed explanation of the protocol flow.

## Integration with LLMs

This project demonstrates integration with Groq's LLM API, but the MCP protocol can be used with any LLM that supports function calling, including:

- OpenAI (GPT models)
- Anthropic Claude
- Amazon Bedrock models
- Local models via tools like Ollama

## License

This project is provided as an educational example of the MCP protocol.