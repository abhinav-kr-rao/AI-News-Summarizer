import sys
import os
import time

# Ensure imports work from project root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import database, crud, models
from app.agents.summary_agent import SummaryAgent

def process_digests():
    print("--- Starting Digest Processing ---")
    db = database.SessionLocal()
    agent = SummaryAgent()
    
    try:
        # Get all articles
        articles = crud.get_articles(db, limit=1000) # Process batches
        print(f"Found {len(articles)} articles to check.")
        
        processed_count = 0
        skipped_count = 0
        failed_count = 0

        for article in articles:
            # Check if digest already exists
            existing_digest = crud.get_digest_by_article_id(db, article.id)
            if existing_digest:
                # print(f"Skipping {article.id}: Digest exists.")
                skipped_count += 1
                continue
            
            print(f"Summarizing Article {article.id}: {article.title[:50]}...")
            
            if not article.content:
                print("   -> No content to summarize.")
                failed_count += 1
                continue

            # Generate Summary
            summary = agent.summarize(article.content)
            
            if summary and "Error" not in summary:
                # Save to DB
                digest_data = {
                    "article_id": article.id,
                    "title": article.title,
                    "summary": summary
                }
                crud.create_digest(db, digest_data)
                print(f"   -> Digest created! Length: {len(summary)}")
                processed_count += 1
                
                # Sleep to respect rate limits (Gemini Free has limits per minute)
                time.sleep(4) 
            else:
                print(f"   -> Failed to generate summary: {summary}")
                failed_count += 1
        
        print("\n" + "="*30)
        print(f"Digest Processing Complete.")
        print(f"Created: {processed_count}")
        print(f"Skipped: {skipped_count}")
        print(f"Failed: {failed_count}")
        print("="*30)

    finally:
        db.close()

if __name__ == "__main__":
    process_digests()
