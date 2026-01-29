import feedparser
import datetime
from dateutil import parser
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig

from typing import List, Dict, Optional
import time
import os


webshare_username=os.getenv("WEBSHARE_USERNAME")
webshare_domain=os.getenv("WEBSHARE_DOMAIN_NAME")
webshare_password=os.getenv("WEBSHARE_PASSWORD")
webshare_port=os.getenv("WEBSHARE_PORT")

import requests
requests.get(
    "https://ipv4.webshare.io/",
    proxies={
        "http": f"http://{webshare_username}:{webshare_password}@{webshare_domain}:{webshare_port}/",
        "https": f"http://{webshare_username}:{webshare_password}@{webshare_domain}:{webshare_port}/"
    }
).text


from pydantic import BaseModel

class ChannelVideo(BaseModel):
    video_id: str
    title: str
    link: str
    published: str
    channel_title: str

class Transcript(BaseModel):
    text: str

class YoutubeScrape:
    def get_latest_videos(self, channel_id: str, hours_lookback: int = 24) -> List[ChannelVideo]:
        """
        Fetches the latest videos from a YouTube channel via RSS feed and filters by time.
        
        RSS URL format: https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}
        """
        rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        print(f"Fetching RSS feed: {rss_url}")
        feed = feedparser.parse(rss_url)
        
        if feed.bozo:
            print(f"Error parsing feed for channel {channel_id}: {feed.bozo_exception}")
            return []

        latest_videos = []
        # Current time in UTC (naive, assuming feed is usually standardized or we handle tz)
        now = datetime.datetime.now(datetime.timezone.utc)
        cutoff_time = now - datetime.timedelta(hours=hours_lookback)
        
        print(f"Filtering videos published after: {cutoff_time}")

        for entry in feed.entries:
            # entry.published is usually in ISO 8601 format
            # feedparser often parses it into entry.published_parsed (struct_time) 
            # but we can verify entry.published string directly or use dateutil
            
            try:
                published_dt = parser.parse(entry.published)
                # Ensure timezone awareness for comparison
                if published_dt.tzinfo is None:
                     published_dt = published_dt.replace(tzinfo=datetime.timezone.utc)
                
                if published_dt > cutoff_time:
                    # Filter out Shorts
                    if "/shorts/" in entry.link:
                        print(f"Skipping Short: {entry.title}")
                        continue

                    video = ChannelVideo(
                        video_id=entry.yt_videoid,
                        title=entry.title,
                        link=entry.link,
                        published=published_dt.isoformat(),
                        channel_title=entry.author
                    )
                    latest_videos.append(video)
            except Exception as e:
                print(f"Error processing entry {entry.get('title', 'Unknown')}: {e}")
                continue
                
        return latest_videos

    def get_transcript_text(self, video_id: str) -> Optional[Transcript]:
        """
        Fetches the transcript for a given video ID using youtube_transcript_api.
        Returns a Transcript object.
        """
        try:
            # video_id="T-kiZ_K1XtY"

            # getting proxy username and password 
      
            print("Video ID: ", video_id)
            ytt_api=YouTubeTranscriptApi(proxy_config=WebshareProxyConfig(
        proxy_username=webshare_username,
        proxy_password=webshare_password,
    ))
            transcript = ytt_api.fetch(video_id)
            transcript_list=transcript.to_raw_data()
            # print("Transcript List: ", transcript_list)
            # Combine all parts into one text
            full_text = " ".join([t['text'] for t in transcript_list])
            return Transcript(text=full_text)
        except Exception as e:
            print(f"Could not retrieve transcript for video {video_id}: {e}")
            return None

if __name__ == "__main__":
    # Quick test logic
    # Example Channel ID (OpenAI): UCVpYJm_aL6iI1t_8vXurZ7Q
    # Example Channel ID (Y Combinator): UCcefcZRL2oaA_uBNeo5UOWg
    
    test_channel_id = "UC16niRr50-MSBwiO3YDb3RA" 
    print(f"--- Testing Channel: {test_channel_id} ---")
    
    scraper = YoutubeScrape()
    videos = scraper.get_latest_videos(test_channel_id, hours_lookback=4800) # Large lookback for testing to ensure we get something
    
    print(f"Found {len(videos)} videos in the specified window.")
    print("videos are of type ",type(videos))
    
    for video in videos[:1]: # Just process the first one
        print(f"\nProcessing Video: {video.title}")
        print(f"Link: {video.link}")
        transcript = scraper.get_transcript_text(video.video_id)
        if transcript:
            print(f"Transcript Preview: {transcript.text[:200]}...")
        else:
            print("No transcript available.")
