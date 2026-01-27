from google import genai
from pydantic import BaseModel
from typing import List, Optional
import os
import logging
from app.user_profile import UserProfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API
API_KEY = os.getenv("GOOGLE_API_KEY")

class RankedItem(BaseModel):
    digest_id: int
    score: int # 1 to 10
    reasoning: str

class RankingResponse(BaseModel):
    ranked_items: List[RankedItem]

class RankingAgent:
    def __init__(self, model_name: str = "gemini-2.5-flash"): # Using latest capable model for reasoning
        if not API_KEY:
            logger.warning("GOOGLE_API_KEY not found. Agent will fail.")
            self.client = None
        else:
            self.client = genai.Client(api_key=API_KEY)
        self.model_name = model_name

    def rank_digests(self, user_profile: UserProfile, digests: List[dict]) -> List[RankedItem]:
        """
        Ranks a list of digests based on the user profile.
        Input digests should be a list of dicts: {'id': int, 'title': str, 'summary': str}
        """
        if not self.client:
            logger.error("Client not initialized.")
            return []

        if not digests:
            return []

        # Construct the context
        digest_text = ""
        for d in digests:
            digest_text += f"ID: {d['id']}\nTitle: {d['title']}\nSummary: {d['summary']}\n---\n"

        prompt = (
            f"You are a personalized news curator. \n"
            f"User Profile: {user_profile.get_prompt_description()}\n\n"
            f"Task: Rank the following news digests based on relevance to the user's interests. "
            f"Assign a score from 1 (irrelevant) to 10 (highly relevant/must read). "
            f"Provide a brief reasoning for the score.\n\n"
            f"News Items:\n{digest_text}"
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': RankingResponse,
                },
            )
            
            # The SDK with response_schema returns a parsed object if successful
            # Depending on version it might be object or dict, widely strict check:
            if response.parsed:
                 return response.parsed.ranked_items
            else:
                logger.error("Failed to parse ranking response.")
                return []

        except Exception as e:
            logger.error(f"Error ranking digests: {e}")
            return []

if __name__ == "__main__":
    # Test
    from app.user_profile import default_profile
    agent = RankingAgent()
    
    test_digests = [
        {"id": 1, "title": "New Python Feature", "summary": "Python 3.14 adds new typing features."},
        {"id": 2, "title": "Cooking Lasagna", "summary": "Best recipe for homemade lasagna."}
    ]
    
    print("Testing Ranking Agent...")
    results = agent.rank_digests(default_profile, test_digests)
    for res in results:
        print(f"ID: {res.digest_id} | Score: {res.score} | Reason: {res.reasoning}")
