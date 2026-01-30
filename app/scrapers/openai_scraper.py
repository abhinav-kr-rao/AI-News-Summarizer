import feedparser
from pydantic import BaseModel
from typing import List, Optional
import datetime
from dateutil import parser
import trafilatura

class OpenAINewsItem(BaseModel):
    title: str
    link: str
    published: str
    description: Optional[str] = None
    guid: Optional[str] = None
    content_markdown: Optional[str] = None

class OpenAIScraper:
    def __init__(self):
        pass

    def get_latest_news(self, rss_url: str = "https://openai.com/news/rss.xml", limit: int = 10) -> List[OpenAINewsItem]:
        """
        Fetches the latest news from the OpenAI RSS feed.
        """
        print(f"Fetching OpenAI RSS feed: {rss_url}")
        feed = feedparser.parse(rss_url)

        if feed.bozo:
            print(f"Error parsing RSS feed: {feed.bozo_exception}")
            return []

        news_items = []
        for entry in feed.entries[:limit]:
            try:
                # Parse date to ensure standard format if needed, though RSS usually has it.
                # Accessing keys safely
                title = entry.get('title', 'No Title')
                link = entry.get('link', '')
                published = entry.get('published', '')
                description = entry.get('description', '') # OpenAI feed usually has description/summary
                guid = entry.get('guid', '')

                # Basic date parsing to ISO format if possible, else keep original string
                try:
                    dt = parser.parse(published)
                    published = dt.isoformat()
                except:
                    pass # Keep original string if parsing fails of empty

                item = OpenAINewsItem(
                    title=title,
                    link=link,
                    published=published,
                    description=description,
                    guid=guid
                )
                news_items.append(item)
            except Exception as e:
                print(f"Error processing entry {entry.get('title', 'Unknown')}: {e}")
                continue

        return news_items

    def scrape_article(self, url: str) -> Optional[str]:
        """
        Scrapes the content of a single article URL and converts it to Markdown using Trafilatura.
        """
        try:
            print(f"Scraping article: {url}")
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                # Extract content in Markdown format
                result = trafilatura.extract(downloaded, output_format="markdown")
                return result
            return None
        except Exception as e:
            print(f"Error scraping article {url}: {e}")
            return None

if __name__ == "__main__":
    scraper = OpenAIScraper()
    print("--- Fetching OpenAI News ---")
    news = scraper.get_latest_news(limit=3)
    print(f"Found {len(news)} items.")
    
    for item in news[:1]: # Test scraping on the first item
        print(f"\nProcessing: {item.title}")
        print(f"Link: {item.link}")
        
        markdown_content = scraper.scrape_article(item.link)
        if markdown_content:
            print("--- Markdown Content Preview ---")
            print(markdown_content[:500] + "...") # Print first 500 chars
            item.content_markdown = markdown_content
        else:
            print("Failed to scrape markdown content.")
