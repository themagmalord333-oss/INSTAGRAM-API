import httpx
import re
import logging

logger = logging.getLogger("fetcher_manager")

class FetcherManager:
    # Orchestrator file jo bhi variable bheje (jaise db ya redis), ye usko chupchap accept kar lega
    def __init__(self, *args, **kwargs):
        pass

    # Teri main file inme se jo bhi function call karegi, dono ready hain
    async def fetch_profile(self, username: str) -> dict:
        return await self._get_bicholiya_data(username)

    async def get_profile(self, username: str) -> dict:
        return await self._get_bicholiya_data(username)

    # Ye raha tera asli ANYSNAP Bypass Logic (Strict JSON Format ke sath)
    async def _get_bicholiya_data(self, username: str) -> dict:
        logger.info(f"🚀 Anysnap Bypass Engine starting for: {username}")
        url = f"https://anonyig.com/en/profile/{username}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Connection": "keep-alive"
        }

        try:
            async with httpx.AsyncClient(http2=True, follow_redirects=True, timeout=15.0) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": "Profile not found or blocked by Middleman.",
                        "meta": {"developer": "@MAGMAxRICH", "project": "ANYSNAP"}
                    }
                
                html_content = response.text
                title_match = re.search(r'<title>(.*?)</title>', html_content)
                title = title_match.group(1) if title_match else username
                
                # Ye strictly JSON output dega tere endpoint par
                return {
                    "success": True,
                    "data": {
                        "username": username,
                        "page_title": title,
                        "status": "Successfully Fetched Anonymously"
                    },
                    "meta": {
                        "source": "Anysnap_Bypass_Engine",
                        "developer": "@MAGMAxRICH",
                        "project": "ANYSNAP"
                    }
                }
                
        except Exception as e:
            logger.error(f"Error fetching: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "meta": {"developer": "@MAGMAxRICH", "project": "ANYSNAP"}
            }