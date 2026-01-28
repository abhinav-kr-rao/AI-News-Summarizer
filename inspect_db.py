from app.database import database, crud, models
from sqlalchemy import select

def check_urls():
    db = database.SessionLocal()
    try:
        stmt = select(models.Article).order_by(models.Article.id.desc()).limit(10)
        articles = db.scalars(stmt).all()
        
        print(f"Checking top {len(articles)} recent articles:")
        for article in articles:
            print(f"ID: {article.id}")
            print(f"Title: {article.title}")
            print(f"URL: {article.url}")
            print(f"Source: {article.source}")
            print("-" * 30)
    finally:
        db.close()

if __name__ == "__main__":
    check_urls()
