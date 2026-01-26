import sys
import os
from datetime import datetime, timedelta, timezone
from dateutil import parser

# Ensure imports work from project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import YOUTUBE_CHANNELS, LOOKBACK_HOURS
from app.scrapers.youtube import YoutubeScrape
from app.scrapers.openai_scraper import OpenAIScraper
from app.scrapers.anthropic_scraper import AnthropicScraper
from app.database import crud, database
from app.services.content_extractor import ContentExtractor

def is_within_lookback(date_str, hours):
    """
    Checks if a date string is within the last 'hours' hours.
    """
    if not date_str:
        return False
    try:
        dt = parser.parse(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=hours)
        return dt > cutoff
    except Exception:
        # If we can't parse the date, assume strictly it's not news or handle otherwise.
        # For now, let's exclude it to be safe, or include? 
        return False

def collect_all_news():
    print(f"--- Starting AI News Collection (Lookback: {LOOKBACK_HOURS} hours) ---\n")
    all_news = []
    youtube_news = []
    openai_news = []
    anthropic_news = []

    # 1. YouTube
    print(">>> 1. YouTube Scraper")
    yt_scraper = YoutubeScrape()
    for channel_id in YOUTUBE_CHANNELS:
        try:
            # YouTube scraper already filters by hours_lookback internally
            videos = yt_scraper.get_latest_videos(channel_id, hours_lookback=LOOKBACK_HOURS)
            print(f"   - Channel {channel_id}: Found {len(videos)} videos")
            for video in videos:
                all_news.append({
                    "source": "YouTube",
                    "title": video.title,
                    "date": video.published,
                    "link": video.link,
                    "type": "video"
                })
                 ## adding to youtube_news list
                youtube_news.append({
                "title": video.title,
                "date": video.published,
                "link": video.link,
                "type": "video"
                })


          
        except Exception as e:
            print(f"   ! Error: {e}")

    # 2. OpenAI
    print("\n>>> 2. OpenAI Scraper")
    try:
        openai_scraper = OpenAIScraper()
        # Fetching a bit more than we might need to ensure we cover the time window
        items = openai_scraper.get_latest_news(limit=20) 
        count = 0
        for item in items:
            if is_within_lookback(item.published, LOOKBACK_HOURS):
                all_news.append({
                    "source": "OpenAI",
                    "title": item.title,
                    "date": item.published,
                    "link": item.link,
                    "type": "article"
                })
                ## adding to openai_news list
                openai_news.append({
                "title": item.title,
                "date": item.published,
                "link": item.link,
                "type": "article"
                })
                count += 1
        print(f"   - Found {count} items within last {LOOKBACK_HOURS} hours")
    except Exception as e:
        print(f"   ! Error: {e}")

    # 3. Anthropic
    print("\n>>> 3. Anthropic Scraper")
    try:
        anthropic_scraper = AnthropicScraper()
        items = anthropic_scraper.get_latest_news(limit_per_feed=10)
        count = 0
        for item in items:
             if is_within_lookback(item.published, LOOKBACK_HOURS):
                all_news.append({
                    "source": f"Anthropic ({item.category})",
                    "title": item.title,
                    "date": item.published,
                    "link": item.link,
                    "type": "article"
                })
                ## adding to anthropic_news list
                anthropic_news.append({
                "title": item.title,
                "date": item.published,
                "link": item.link,
                "type": "article"
                })
                count += 1
        print(f"   - Found {count} items within last {LOOKBACK_HOURS} hours")
    except Exception as e:
         print(f"   ! Error: {e}")

    # Save to Database
    print("\n>>> Saving to Database...")
    db = database.SessionLocal()
    try:
        saved_count = 0
        for item in all_news:
            try:
                # Enrich with content (transcripts/markdown)
                # print(f"   > Fetching content for: {item.get('title')[:30]}...")
                item = ContentExtractor.enrich_article(item)
                
                crud.create_article(db, item)
                saved_count += 1
            except Exception as e:
                print(f"   ! Failed to save article {item.get('title')}: {e}")
        print(f"   - processed {saved_count} articles for database storage.")
    except Exception as e:
        print(f"   ! Database Connection Error: {e}")
    finally:
        db.close()

    return [all_news, youtube_news, openai_news, anthropic_news]

if __name__ == "__main__":
    news_items = collect_all_news()
    all_news, youtube_news, openai_news, anthropic_news = news_items
    
    print("\n" + "="*50)
    print(f" SUMMARY: Collected {len(all_news)} items")

    print("Youtube News",youtube_news)
    print("OpenAI News",openai_news)
    print("Anthropic News",anthropic_news)
    # print("="*50)
    
    for item in all_news:
        print(f"[{item['source']}] {item['title']}")
        print(f"Link: {item['link']}")
        print("-" * 30)
