import sys
import os
import time

# Ensure imports work from project root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import database, crud
from app.agents.ranking_agent import RankingAgent
from app.user_profile import default_profile

def rank_news():
    print("--- Starting Personal News Ranking ---")
    db = database.SessionLocal()
    
    try:
        # 1. Fetch recent digests
        # Using a large window (e.g., 72 hours) to ensure we see data for this demo
        # Modify 'hours' as needed for production (e.g., 24)
        recent_digests = crud.get_recent_digests(db, hours=72)
        
        if not recent_digests:
            print("No recent digests found to rank.")
            return

        print(f"Found {len(recent_digests)} recent digests.")
        
        # 2. Prepare data for Agent
        digest_list = []
        digest_map = {} # Helper to look up details later
        for d in recent_digests:
            item = {"id": d.id, "title": d.title, "summary": d.summary}
            digest_list.append(item)
            digest_map[d.id] = d

        # 3. Call Ranking Agent
        agent = RankingAgent()
        print(f"Ranking items for profile: {default_profile.name}...")
        
        ranked_items = agent.rank_digests(default_profile, digest_list)
        
        # 4. Sort and Display
        # Sort by score descending
        ranked_items.sort(key=lambda x: x.score, reverse=True)
        
        print("\n=== TOP NEWS FOR YOU ===")
        for item in ranked_items:
            original = digest_map.get(item.digest_id)
            if original:
                print(f"[Score: {item.score}/10] {original.title}")
                print(f"Reason: {item.reasoning}")
                print(f"Summary: {original.summary[:150]}...") # Show snippet of summary
                print("-" * 40)

    finally:
        db.close()

if __name__ == "__main__":
    rank_news()
