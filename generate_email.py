import sys
import os

# Ensure imports work from project root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import database, crud
from app.agents.ranking_agent import RankingAgent
from app.agents.email_agent import EmailAgent
from app.user_profile import default_profile

def generate_daily_email():
    print("--- Generating Daily Email ---")
    db = database.SessionLocal()
    
    try:
        # 1. Fetch & Rank (Reuse logic from rank_news, or import if refactored)
        # Fetching last 72h for demo purposes
        recent_digests = crud.get_recent_digests(db, hours=72)
        
        if not recent_digests:
            print("No recent news to generate email.")
            return

        digest_list = []
        digest_map = {}
        for d in recent_digests:
            digest_list.append({"id": d.id, "title": d.title, "summary": d.summary})
            digest_map[d.id] = d

        # Rank
        rank_agent = RankingAgent()
        ranked_items = rank_agent.rank_digests(default_profile, digest_list)
        ranked_items.sort(key=lambda x: x.score, reverse=True)
        
        # Take Top 10
        top_10 = ranked_items[:10]
        
        print(f"identifying top {len(top_10)} stories...")
        
        # Prepare Data for Email
        email_data = []
        top_titles = []
        
        for item in top_10:
            original = digest_map.get(item.digest_id)
            if original:
                # We need URL and Date from the original Article
                # The Digest model has a relationship to Article
                article = original.article
                
                email_data.append({
                    "title": original.title,
                    "url": article.url, # Access via relationship
                    "date": str(article.published_date), # Ensure string
                    "reasoning": item.reasoning,
                    "summary": original.summary
                })
                top_titles.append(original.title)

        # 2. Generate Intro
        email_agent = EmailAgent()
        intro = email_agent.generate_intro(default_profile.name, top_titles)
        print(f"Generated Intro: {intro}")
        
        # 3. Format Email
        email_html = email_agent.format_email(default_profile.name, intro, email_data)
        
        # 4. Save/Print
        output_file = "daily_digest.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(email_html)
            
        print(f"\nEmail generated successfully! Saved to {output_file}")
        print("You can open this file in your browser to preview.")

    finally:
        db.close()

if __name__ == "__main__":
    generate_daily_email()
