import argparse
import server


server.generate()
def main():
    argparse.ArgumentParser(description="JEB Pro MCP Server")
    server.mcp.run(transport="sse", host="127.0.0.1", port=16160, path="/mcp")

if __name__ == "__main__":
    main()