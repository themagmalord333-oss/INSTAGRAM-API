import httpx
from app.utils.exceptions import SourceUnavailableError, ProfileNotFoundError
from app.utils.logger import get_logger

logger = get_logger("fetcher_manager")

class AnysnapDirectAPI:
    async def fetch(self, username: str) -> dict:
        logger.info(f"🚀 Starting Anysnap Direct API for: {username}")
        url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "X-IG-App-ID": "936619743392459",
            "Accept": "*/*",
            "Referer": f"https://www.instagram.com/{username}/"
        }

        async with httpx.AsyncClient(timeout=10, http2=True) as client:
            try:
                response = await client.get(url, headers=headers)
                if response.status_code == 404:
                    raise ProfileNotFoundError(f"Profile '{username}' not found.")
                response.raise_for_status()
                data = response.json()
                user = data["data"]["user"]
                
                return {
                    "username": user.get("username"),
                    "full_name": user.get("full_name"),
                    "biography": user.get("biography"),
                    "profile_picture": user.get("profile_pic_url_hd") or user.get("profile_pic_url"),
                    "followers": user.get("edge_followed_by", {}).get("count", 0),
                    "following": user.get("edge_follow", {}).get("count", 0),
                    "posts": user.get("edge_owner_to_timeline_media", {}).get("count", 0),
                    "is_verified": user.get("is_verified", False),
                    "is_private": user.get("is_private", False),
                    "source": "Anysnap_Direct_API"
                }
            except ProfileNotFoundError as e:
                raise e
            except Exception as e:
                logger.info("Direct API blocked. Trying Anysnap Fallback Method...")
                try:
                    fallback_url = f"https://www.instagram.com/{username}/?__a=1&__d=dis"
                    fallback_response = await client.get(fallback_url, headers=headers)
                    if fallback_response.status_code == 404:
                        raise ProfileNotFoundError(f"Profile '{username}' not found.")
                    fallback_data = fallback_response.json()
                    user = fallback_data.get("graphql", {}).get("user", {})
                    if not user:
                        raise SourceUnavailableError("Blocked by Instagram.")
                        
                    return {
                        "username": user.get("username"),
                        "full_name": user.get("full_name"),
                        "biography": user.get("biography"),
                        "profile_picture": user.get("profile_pic_url_hd"),
                        "followers": user.get("edge_followed_by", {}).get("count", 0),
                        "following": user.get("edge_follow", {}).get("count", 0),
                        "posts": user.get("edge_owner_to_timeline_media", {}).get("count", 0),
                        "is_verified": user.get("is_verified", False),
                        "is_private": user.get("is_private", False),
                        "source": "Anysnap_Fallback_API"
                    }
                except Exception as ex:
                    raise SourceUnavailableError("AWS IP blocked by Instagram security.")

class FetcherManager:
    sources = [AnysnapDirectAPI()]
    @classmethod
    async def get_profile(cls, username: str) -> dict:
        for source in cls.sources:
            try:
                return await source.fetch(username)
            except ProfileNotFoundError as e:
                raise e
            except Exception as e:
                logger.error(f"Error fetching profile: {e}")
                continue
        raise SourceUnavailableError("Server IP permanently blocked by Instagram.")