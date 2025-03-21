from typing import Any
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import json, os
import httpx
from bs4 import BeautifulSoup
import logging,sys

load_dotenv()

# Initialize FastMCP Server
mcp = FastMCP("rss3-data")


docs_urls = {
    'base': "docs.base.org",
    'linea': "docs.linea.build"
}


# Config Logging
logging.basicConfig(
    level=logging.DEBUG,
    format=' %(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mcp_debug.log"),
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger("mcp-server")

# Get the associated links for query
async def search_web(query: str) -> dict | None :
    payload = json.dumps({"q":query, "num": 2})
    
    headers = {
        "X-API-KEY": os.getenv("SERPER_API_KEY"),
        "Content-Type" : "application/json"
    }
    
    logger.debug(f"Search query: {query}")
    logger.debug(f"Using SERPER_URL: {os.getenv('SERPER_URL')}")
    logger.debug(f"Headers: {headers}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                os.getenv("SERPER_URL"), headers=headers,
                data = payload, timeout=30.0
            )
            response.raise_for_status()
            
            logger.debug(f"Search results: {response.json()}")
            return response.json()
        except Exception as e:
            logger.error(f"Error in search_web: {str(e)}")
            return {"organic": []}
        
    
# Fetch Each link

async def fetch_url(url: str):
    logger.debug(f"Fetching URL: {url}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30.0)
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text()
            logger.debug(f"Successfully fetched URL: {url} (content length: {len(text)})")
            return text
        except Exception as e:
            logger.error(f"Error in fetch_url: {str(e)}")
            return "Timeout error"         

@mcp.tool()
async def get_data(query:str, chain: str):
    """
    Search the latest docs for a given query and chain.
    Support Base, Linea for now. 
    
    Args:
        query: The query to search for (e.g. "Network information of Base chain")
        chain: The chain to search in (e.g. "linea")
        
    Returns:
        Text from docs
    """
    

    logger.info(f"get_data called with query: {query}, chain: {chain}")

    if chain not in docs_urls:
        raise ValueError(f"Chain {chain} not supported by this tool")
    
    query = f"site:{docs_urls[chain]} {query}"
    logger.debug(f"Searching for: {query}")
    try:
        results = await search_web(query=query)
    
        print(f"Raw result type {type(results)}")
        print(f"Raw result  {results}")
        if len(results['organic'])==0:
            return "No result found"
        
        text = ""
        for result in results["organic"]:
            text+= await fetch_url(result['link'])
        logger.info(f"Successfully retrieved content (length: {len(text)})")
        return text
    except Exception as e:
        logger.error(f"Unhandled exception in get_data: {str(e)}", exc_info=True)
        return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport='stdio')


