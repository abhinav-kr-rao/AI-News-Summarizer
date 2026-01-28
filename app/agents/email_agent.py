from google import genai
import os
import logging
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
import re
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API
API_KEY = os.getenv("GOOGLE_API_KEY")

class EmailSection(BaseModel):
    title: str = Field(description="The headline of the news story.")
    date: str = Field(description="The date of the news story.")
    url: str = Field(description="The direct URL to the full story.")
    summary: str = Field(description="A detailed summary fully formatted in Markdown. Use ### headers for sub-sections. Do NOT use numbered lists.")
    category: str = Field(description="Category of the news (e.g. AI Models, Regulation, Industry).")

class EmailContent(BaseModel):
    subject: str = Field(description="A catchy, professional subject line for the email.")
    intro: str = Field(description="A warm, engaging introductory paragraph for the user.")
    sections: List[EmailSection] = Field(description="The list of news sections.")


class EmailAgent:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        if not API_KEY:
            logger.warning("GOOGLE_API_KEY not found. Agent will fail.")
            self.client = None
        else:
            self.client = genai.Client(api_key=API_KEY)
        self.model_name = model_name

    def generate_newsletter(self, user_name: str, news_items: List[Dict]) -> EmailContent:
        """
        Generates the full structured email content using Gemini.
        news_items should be a list of dicts with keys matching the source data (title, summary, reason, etc.)
        """
        if not self.client:
            # Return a dummy object if no client
            return EmailContent(
                subject="Daily Digest (Offline)",
                intro=f"Hello {user_name}, API unavailable.",
                sections=[]
            )

        # 1. Prepare Context
        items_text = ""
        for i, item in enumerate(news_items):
            items_text += (
                f"Item {i+1}:\n"
                f"Title: {item.get('title')}\n"
                f"Date: {item.get('date')}\n"
                f"URL: {item.get('url')}\n"
                f"Original Summary: {item.get('summary')}\n"
                f"Relevance: {item.get('reasoning')}\n"
                f"---\n"
            )

        prompt = (
            f"You are an expert AI News Curator writing for {user_name}.\n"
            f"Today is {datetime.now().strftime('%A, %B %d')}.\n\n"
            f"Task: Create a structured email newsletter from the following top news items.\n"
            f"Requirements:\n"
            f"1. **Subject**: MUST start with 'Daily News AI Digest...' followed by a short highlight of the top story.\n"
            f"2. **Intro**: Friendly, professional, mentioning top trends.\n"
            f"3. **Sections**: For each news item, write a structured section.\n"
            f"   - **URL**: You MUST use the EXACT URL provided in the input. Do NOT hallucinate or change the link.\n"
            f"   - **Summary**: A concise, informative summary of the news. Do NOT use markdown headers strings like '###'. Use clear paragraphs.\n"
            f"   - **Category**: Classify the news.\n\n"
            f"Input Data:\n{items_text}"
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': EmailContent,
                }
            )
            if response.parsed:
                return response.parsed
            else:
                logger.error("Failed to parse EmailContent.")
                return EmailContent(subject="Error", intro="Could not generate email.", sections=[])
        except Exception as e:
            logger.error(f"Error generating newsletter: {e}")
            return EmailContent(subject="Error", intro="Error generating email.", sections=[])

    def render_html(self, content: EmailContent) -> str:
        """
        Renders the EmailContent model into a clean, minimal HTML string.
        """
        def simple_format(text):
            # Convert basic markdown bold to html bold
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
            # Convert newlines to breaks
            text = text.replace('\n\n', '<br><br>')
            return text

        sections_html = ""
        for section in content.sections:
            summary_html = simple_format(section.summary)
            sections_html += f"""
                <div style="margin-bottom: 35px; border-bottom: 1px solid #eee; padding-bottom: 25px;">
                    <div style="font-size: 0.85em; color: #666; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">
                        {section.category} &bull; {section.date}
                    </div>
                    <h2 style="margin: 0 0 10px 0; font-size: 1.4em; font-weight: 600; line-height: 1.3;">
                        <a href="{section.url}" style="color: #111; text-decoration: none; border-bottom: 1px solid #111;">
                            {section.title}
                        </a>
                    </h2>
                    <div style="font-family: Georgia, serif; font-size: 1.05em; line-height: 1.6; color: #333; margin-bottom: 15px;">
                        {summary_html}
                    </div>
                    <div>
                        <a href="{section.url}" style="font-size: 0.9em; color: #0066cc; text-decoration: none; font-weight: 500;">
                            Read Source &rarr;
                        </a>
                    </div>
                </div>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; line-height: 1.6; color: #111; max-width: 680px; margin: 0 auto; padding: 40px 20px;">
            
            <!-- Header -->
            <div style="margin-bottom: 40px; text-align: center;">
                <h1 style="margin: 0; font-size: 24px; font-weight: 700; letter-spacing: -0.5px;">Daily News AI Digest</h1>
                <p style="margin: 5px 0 0 0; color: #666; font-size: 14px;">
                    {datetime.now().strftime("%A, %B %d, %Y")}
                </p>
            </div>

            <!-- Intro -->
            <div style="margin-bottom: 40px; font-family: Georgia, serif; font-size: 1.1em; color: #444; border-left: 3px solid #111; padding-left: 20px;">
                {simple_format(content.intro)}
            </div>

            <!-- Sections -->
            {sections_html}

            <!-- Footer -->
            <div style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #999; font-size: 12px;">
                <p>&copy; {datetime.now().year} AI News Aggregator. All rights served.</p>
            </div>

        </body>
        </html>
        """
        return html

if __name__ == "__main__":
    # Test
    agent = EmailAgent()
    print("Testing Email Agent...")
    intro = agent.generate_intro("Shashank", ["OpenAI releases GPT-5", "Anthropic updates Claude"])
    print(f"Intro: {intro}")
