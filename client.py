import httpx
from dotenv import load_dotenv
import os

load_dotenv()
NASA_API_KEY = os.getenv("NASA_API_KEY")

BASE = "https://api.nasa.gov"

async def nasa_get(endpoint: str, params: dict = None)
    if params is None:
        params = {}

    params["api_key"] = NASA_API_KEY

    async with httpx.AsyncClient(base_url=BASE) as client:
        r = await client.get(f"{BASE}/{endpoint}", params=params)
        return r.json()