import re
from playwright.async_api import async_playwright
from app.utils.exceptions import SourceUnavailableError, ProfileNotFoundError
from app.utils.logger import get_logger

logger = get_logger("browser_fetcher")

class BrowserInstagramSource:
    async def fetch(self, username: str) -> dict:
        logger.info(f"Triggering Browser Fallback for: {username}")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                # Mimic a real user browser to prevent instant blocking
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={'width': 1280, 'height': 720}
                )
                page = await context.new_page()
                
                # Load the page and wait for DOM
                response = await page.goto(f"https://www.instagram.com/{username}/", timeout=20000)
                
                if response and response.status == 404:
                    await browser.close()
                    raise ProfileNotFoundError(f"Profile '{username}' not found.")

                await page.wait_for_load_state("domcontentloaded")
                
                title = await page.title()
                if "Page Not Found" in title:
                    await browser.close()
                    raise ProfileNotFoundError(f"Profile '{username}' not found.")

                # Extracting data reliably using Meta Tags (DOM independent)
                description_content = await page.get_attribute("meta[property='og:description']", "content")
                title_content = await page.get_attribute("meta[property='og:title']", "content")
                image_content = await page.get_attribute("meta[property='og:image']", "content")

                if not description_content:
                    await browser.close()
                    raise SourceUnavailableError("Browser blocked by Instagram login wall.")

                # Parsing the description string: "123 Followers, 456 Following, 789 Posts - See..."
                followers, following, posts = 0, 0, 0
                stats_match = re.search(r'([\d.,KMB]+)\s+Followers,\s+([\d.,KMB]+)\s+Following,\s+([\d.,KMB]+)\s+Posts', description_content, re.IGNORECASE)
                
                if stats_match:
                    followers = self._parse_number(stats_match.group(1))
                    following = self._parse_number(stats_match.group(2))
                    posts = self._parse_number(stats_match.group(3))

                # Extracting full name from title: "Full Name (@username) • Instagram..."
                full_name = username
                if title_content:
                    name_match = re.match(r'^(.*?)\s+\(@', title_content)
                    if name_match:
                        full_name = name_match.group(1).strip()

                await browser.close()

                return {
                    "username": username,
                    "full_name": full_name,
                    "biography": None, # Biography is hidden deep in React DOM, keeping safe
                    "profile_picture": image_content,
                    "followers": followers,
                    "following": following,
                    "posts": posts,
                    "is_verified": False, 
                    "is_private": False, 
                    "source": "browser"
                }
                
        except ProfileNotFoundError as e:
            raise e
        except Exception as e:
            logger.error(f"Browser fetch failed for {username}: {e}")
            raise SourceUnavailableError("Browser fallback failed or was blocked by Instagram.")

    def _parse_number(self, text: str) -> int:
        text = text.replace(',', '').upper()
        if 'K' in text:
            return int(float(text.replace('K', '')) * 1000)
        if 'M' in text:
            return int(float(text.replace('M', '')) * 1000000)
        if 'B' in text:
            return int(float(text.replace('B', '')) * 1000000000)
        try:
            return int(float(text))
        except ValueError:
            return 0