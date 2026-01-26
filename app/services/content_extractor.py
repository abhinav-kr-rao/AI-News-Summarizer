from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import trafilatura
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentExtractor:
    @staticmethod
    def get_youtube_transcript(video_url: str) -> str:
        """
        Extracts transcript from a YouTube video URL.
        Returns None if no transcript is found or error occurs.
        """
        try:
            # video_id extraction might need to be more robust for different url formats, 
            # but this covers standard watch?v=
            if "v=" not in video_url:
                return None
            video_id = video_url.split("v=")[1].split("&")[0]

            print("the video id is ", video_id)
            
            ytt=YouTubeTranscriptApi()
            transcript = ytt.fetch(video_id)
            formatter = TextFormatter()
            return formatter.format_transcript(transcript)
        except Exception as e:
            logger.error(f"Error fetching YouTube transcript for {video_url}: {e}")
            return None

    @staticmethod
    def get_url_markdown(url: str) -> str:
        """
        Extracts main content from a URL and converts to generic text/markdown.
        Returns None if extraction fails.
        """
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                result = trafilatura.extract(downloaded, include_comments=False, include_tables=False, no_fallback=True)
                return result
            return None
        except Exception as e:
            logger.error(f"Error fetching article content for {url}: {e}")
            return None

    @staticmethod
    def enrich_article(article_data: dict) -> dict:
        """
        Enriches the article data dictionary with a 'content' field if possible.
        """
        url = article_data.get("link")
        type_ = article_data.get("type")
        
        if not url:
            return article_data
            
        content = None
        
        # Simple routing logic
        if type_ == "video" or "youtube.com" in url or "youtu.be" in url:
            content = ContentExtractor.get_youtube_transcript(url)
        else:
            # Default to markdown extraction for blogs/articles
            content = ContentExtractor.get_url_markdown(url)
            
        if content:
            article_data["content"] = content
            
        return article_data
