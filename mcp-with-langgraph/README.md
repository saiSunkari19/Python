### Setup 
```
# Create virtual environment and activate it
uv venv
source .venv/bin/activate
```

### Run & Debug
```
uv run main.py

npx @modelcontextprotocol/inspector uv run main.py 

```

### Config for claude desktop 
```
{
    "mcpServers": {
        "rss3-data": {
            "command": "/Users/sai/.local/bin/uv",
            "args": [
                "--directory",
                "/Users/sai/go/src/github.com/saiSunkari19/python/mcp-server-rss3",
                "run",
                "main.py"
            ]
        }
    }
}
```

### Sample Result 
![Sample test output](image.png)%    


## For SSE 
```
uv run mcpServerSSE.py
```


### Debug
```
npx @modelcontextprotocol/inspector uv run mcpServerSSE.py 
```

