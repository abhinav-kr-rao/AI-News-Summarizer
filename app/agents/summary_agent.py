from google import genai
from google.genai import types
import os
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API
API_KEY = os.getenv("GOOGLE_API_KEY")

class SummaryAgent:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        if not API_KEY:
            logger.warning("GOOGLE_API_KEY not found. Agent will fail.")
            self.client = None
        else:
            self.client = genai.Client(api_key=API_KEY)
        self.model_name = model_name

    def summarize(self, text: str) -> str:
        """
        Summarizes the provided text into 4-6 concise lines capturing key technical details.
        """
        if not self.client:
            return "Configuration Error: No API Key."
            
        if not text or len(text) < 50:
            return "Content too short to summarize."

        try:

            # print("api key is ", API_KEY)
            prompt = (
                "You are a technical news summarizer. "
                "Summarize the following content into 4-6 concise lines. "
                "Focus on key technical details, announcements, or insights. "
                "Do not use markdown formatting like bolding or headers, just plain text bullets or sentences.\n\n"
                f"Content:\n{text[:30000]}" # Truncate to safe limit
            )
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            if response.text:
                return response.text.strip()
            return "No summary generated."
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            if "429" in str(e):
                logger.warning("Rate limit hit. Sleeping for 2 seconds...")
                time.sleep(2)
            return None

if __name__ == "__main__":
    # Test
    agent = SummaryAgent()
    print("Testing Summary Agent...")
    res = agent.summarize("Artificial Intelligence is evolving rapidly. Large Language Models are becoming more capable...")
    print(f"Result: {res}")
