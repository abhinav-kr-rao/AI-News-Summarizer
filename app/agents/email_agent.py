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
            f"1. **Subject**: Catchy and relevant to the key themes.\n"
            f"2. **Intro**: Friendly, professional, mentioning top trends.\n"
            f"3. **Sections**: For each news item, write a structured section.\n"
            f"   - **Summary**: Rewrite the summary to be engaging and formatted in **Markdown**. "
            f"Use **### headers** for internal structure if deep diving. "
            f"Avoid simple numbered lists; use paragraphs and bullet points where appropriate.\n"
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
        Renders the EmailContent model into an HTML string.
        """
        def md_to_html(text):
            # Very basic markdown converter
            # Bold
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
            # Headers ###
            text = re.sub(r'### (.*?)\n', r'<h4>\1</h4>', text)
            # Bullets
            text = re.sub(r'- (.*?)\n', r'<li>\1</li>', text)
            # Wrap bullets in ul (simplistic)
            if '<li>' in text:
                text = text.replace('<li>', '<ul><li>', 1) # This is hacky, but robust options need regex blocks
                # Better: just leave as is, CSS handles it or browsers handle text.
                # Let's do a slightly better bullet handler:
                lines = text.split('\n')
                in_list = False
                new_lines = []
                for line in lines:
                    if line.startswith('<li>'):
                        if not in_list:
                            new_lines.append('<ul>')
                            in_list = True
                    else:
                        if in_list:
                            new_lines.append('</ul>')
                            in_list = False
                    new_lines.append(line)
                if in_list: new_lines.append('</ul>')
                text = "\n".join(new_lines)
            
            # Paragraphs (double newlines)
            text = text.replace('\n\n', '<br><br>')
            return text

        sections_html = ""
        for section in content.sections:
            summary_html = md_to_html(section.summary)
            sections_html += f"""
                <div style="margin-bottom: 30px; border-bottom: 1px solid #eee; padding-bottom: 20px;">
                    <span style="background-color: #eef; color: #33a; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold;">{section.category}</span>
                    <h3 style="margin-top: 5px;"><a href="{section.url}" style="color: #2c3e50; text-decoration: none;">{section.title}</a></h3>
                    <p style="font-size: 0.9em; color: #888; margin-bottom: 10px;">{section.date}</p>
                    <div style="font-family: inherit; line-height: 1.6;">
                        {summary_html}
                    </div>
                </div>
            """

        html = f"""
        <html>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #ddd;">
                <h1 style="color: #2c3e50; text-align: center;">{content.subject}</h1>
                <p style="font-size: 1.1em; color: #555; text-align: center;">{datetime.now().strftime("%B %d, %Y")}</p>
                <hr>
                <div style="font-size: 1.1em; margin-bottom: 30px;">
                    {content.intro}
                </div>
                {sections_html}
                <div style="text-align: center; color: #aaa; font-size: 0.8em; margin-top: 50px;">
                    Generated by AI News Aggregator
                </div>
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
