import random
import logging
import requests
from typing import List

logger = logging.getLogger(__name__)

# Using DiceBear API for avatars
AVATAR_STYLES = ['avataaars', 'human', 'bottts', 'gridy']

def get_random_avatars(count: int = 20) -> List[str]:
    """Generate random avatar URLs using DiceBear API"""
    try:
        avatars = []
        for _ in range(count):
            style = random.choice(AVATAR_STYLES)
            seed = random.randint(1, 1000000)
            url = f"https://api.dicebear.com/7.x/{style}/svg?seed={seed}"

            # Verify URL is accessible
            try:
                response = requests.head(url)
                if response.status_code == 200:
                    logger.debug(f"Successfully verified avatar URL: {url}")
                    avatars.append(url)
                else:
                    logger.warning(f"Failed to verify avatar URL: {url}, status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Error checking avatar URL {url}: {str(e)}")
                continue

        if not avatars:
            logger.error("Failed to generate any valid avatar URLs")
            # Fallback to a static avatar style if all attempts fail
            return [f"https://api.dicebear.com/7.x/avataaars/svg?seed={i}" for i in range(count)]

        return avatars
    except Exception as e:
        logger.error(f"Error generating avatars: {str(e)}")
        return []