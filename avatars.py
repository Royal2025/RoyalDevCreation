import random
import logging
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
            url = f"https://api.dicebear.com/6.x/{style}/svg?seed={seed}"
            avatars.append(url)
        return avatars
    except Exception as e:
        logger.error(f"Error generating avatars: {str(e)}")
        raise Exception("Failed to generate avatars")
