import sys
sys.path.append(".")

from app.services.content_extractor import ContentExtractor

def test_extraction():
    # 1. Test YouTube
    yt_url = "https://www.youtube.com/watch?v=1fu2X4MSCPQ" # Some generic tech video or one known to have transcripts
    print(f"Testing YouTube: {yt_url}")
    article = {"link": yt_url, "type": "video", "source": "YouTube", "title": "Test Video"}
    enriched = ContentExtractor.enrich_article(article)
    content = enriched.get("content")
    if content:
        print(f"YouTube Success! Content length: {len(content)}")
        print(f"Snippet: {content[:200]}...")
    else:
        print("YouTube Failed or no transcript.")

    # 2. Test Blog
    blog_url = "https://openai.com/index/openai-o1-system-card/" # Example generic blog
    print(f"\nTesting Blog: {blog_url}")
    article = {"link": blog_url, "type": "article", "source": "OpenAI", "title": "Test Blog"}
    enriched = ContentExtractor.enrich_article(article)
    content = enriched.get("content")
    if content:
        print(f"Blog Success! Content length: {len(content)}")
        print(f"Snippet: {content[:200]}...")
    else:
        print("Blog Failed.")

if __name__ == "__main__":
    test_extraction()
