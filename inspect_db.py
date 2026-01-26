from app.database import database, models

def inspect_data():
    db = database.SessionLocal()
    try:
        articles = db.query(models.Article).order_by(models.Article.created_at.desc()).limit(5).all()
        print(f"--- Database Inspection (Top {len(articles)} recent) ---")
        for a in articles:
            content_status = f"✅ (Length: {len(a.content)})" if a.content else "❌ None"
            print(f"ID: {a.id} | Type: {a.type} | Source: {a.source}")
            print(f"Title: {a.title[:50]}...")
            print(f"Content: {content_status}")
            print("-" * 30)
    finally:
        db.close()

if __name__ == "__main__":
    inspect_data()
