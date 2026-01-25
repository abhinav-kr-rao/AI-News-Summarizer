import feedparser
from pydantic import BaseModel
from typing import List, Optional
import datetime
from dateutil import parser
from docling.document_converter import DocumentConverter

class AnthropicNewsItem(BaseModel):
    title: str
    link: str
    published: str
    description: Optional[str] = None
    guid: Optional[str] = None
    category: Optional[str] = None  # To track which feed it came from
    content_markdown: Optional[str] = None

class AnthropicScraper:
    FEEDS = [
        "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_research.xml",
        "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_engineering.xml",
        "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml"
    ]

    def __init__(self):
        self.converter = DocumentConverter()

    def get_latest_news(self, limit_per_feed: int = 5) -> List[AnthropicNewsItem]:
        """
        Fetches news from all Anthropic RSS feeds and combines them.
        """
        all_items = []
        
        for feed_url in self.FEEDS:
            print(f"Fetching Anthropic RSS feed: {feed_url}")
            feed = feedparser.parse(feed_url)

            # Handle "bozo" bit (soft errors like encoding or content-type mismatch)
            if feed.bozo:
                if not feed.entries:
                    # If there are no entries, it's a fatal error
                    print(f"Error parsing RSS feed {feed_url}: {feed.bozo_exception}")
                    continue
                else:
                    # If entries exist, it's likely a soft warning (e.g. text/plain header)
                    # We log it but proceed to parse what we found.
                    print(f"Warning: Issue parsing {feed_url} (continuing): {feed.bozo_exception}")
            
            # Determine category from URL or feed title
            category = "General"
            if "research" in feed_url:
                category = "Research"
            elif "engineering" in feed_url:
                category = "Engineering"
            elif "news" in feed_url:
                category = "News"

            for entry in feed.entries[:limit_per_feed]:
                try:
                    title = entry.get('title', 'No Title')
                    link = entry.get('link', '')
                    published = entry.get('published', '')
                    description = entry.get('description', '')
                    guid = entry.get('guid', '')

                    try:
                        dt = parser.parse(published)
                        published = dt.isoformat()
                    except:
                        pass 

                    item = AnthropicNewsItem(
                        title=title,
                        link=link,
                        published=published,
                        description=description,
                        guid=guid,
                        category=category
                    )
                    all_items.append(item)
                except Exception as e:
                    print(f"Error processing entry {entry.get('title', 'Unknown')}: {e}")
                    continue
        
        # Sort all items by date (descending), handling potential date parsing issues gracefully
        # If date string is standard ISO (which we tried to ensure), this works. 
        # If not, it might sort lexicographically which is 'okay' for similar formats.
        all_items.sort(key=lambda x: x.published, reverse=True)
        
        return all_items

    def scrape_article(self, url: str) -> Optional[str]:
        """
        Scrapes the content of a single article URL and converts it to Markdown.
        """
        try:
            print(f"Scraping article: {url}")
            result = self.converter.convert(url)
            doc = result.document
            markdown = doc.export_to_markdown()
            return markdown
        except Exception as e:
            print(f"Error scraping article {url}: {e}")
            return None

if __name__ == "__main__":
    scraper = AnthropicScraper()
    print("--- Fetching Anthropic News ---")
    news = scraper.get_latest_news(limit_per_feed=3)
    print(f"Found {len(news)} total items from all feeds.")
    
    for item in news[:5]: # Show top 5 recent from all combined
        print(f"\n[{item.category}] {item.title}")
        print(f"Date: {item.published}")
        print(f"Link: {item.link}")
    
    if news:
        print(f"\n--- Testing Scraper on: {news[0].title} ---")
        md = scraper.scrape_article(news[0].link)
        if md:
            print("Markdown Preview:")
            print(md[:500] + "...")
