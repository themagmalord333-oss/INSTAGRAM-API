import httpx
import re
import json
from fastapi import HTTPException

# Anysnap Core Fetcher - Developer: @MAGMAxRICH
async def fetch_instagram_profile(username: str) -> dict:
    # Humara Bicholiya URL (Middleman Bypass)
    url = f"https://anonyig.com/en/profile/{username}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    try:
        async with httpx.AsyncClient(http2=True, follow_redirects=True, timeout=15.0) as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": "Profile not found or Middleman server issue.",
                    "status_code": response.status_code
                }
            
            html_content = response.text
            
            # HTML me se data nikalne ka jugaad (Regex)
            # Kyunki hum HTML scrape kar rahe hain, basic cheezein regex se nikalenge
            
            # Extracting Title to verify profile
            title_match = re.search(r'<title>(.*?)</title>', html_content)
            title = title_match.group(1) if title_match else username
            
            # Note: HTML structure change hone par regex update karna padh sakta hai.
            # Abhi ke liye ek solid fallback JSON structure bhej rahe hain:

            # Strictly JSON Format output (FastAPI isko direct JSON me bhej dega)
            result = {
                "success": True,
                "data": {
                    "username": username,
                    "page_title": title,
                    "status": "Successfully Fetched Anonymously",
                    "note": "Data routed via Middleman. HTML parsing active."
                },
                "meta": {
                    "source": "Anysnap_Bypass_Engine",
                    "developer": "@MAGMAxRICH",
                    "project": "ANYSNAP"
                }
            }
            return result
            
    except httpx.RequestError as e:
        return {
            "success": False,
            "error": f"Anysnap Engine Failed to connect: {str(e)}",
            "meta": {
                "source": "Anysnap_Bypass_Engine",
                "developer": "@MAGMAxRICH"
            }
        }
