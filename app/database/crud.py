from sqlalchemy.orm import Session
from . import models

def get_article_by_url(db: Session, url: str):
    return db.query(models.Article).filter(models.Article.url == url).first()

def create_article(db: Session, article_data: dict):
    # Check if article exists to avoid duplicates (though logic should handle this before calling create, safe to verify)
    existing = get_article_by_url(db, article_data.get("link"))
    if existing:
        return existing

    db_article = models.Article(
        title=article_data.get("title"),
        source=article_data.get("source"),
        published_date=str(article_data.get("date")), # Ensure string if model expects string
        url=article_data.get("link"),
        type=article_data.get("type"),
        content=article_data.get("content")
    )
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

def update_article_content(db: Session, article_id: int, content: str):
    db_article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if db_article:
        db_article.content = content
        db.commit()
        db.refresh(db_article)
    return db_article

def get_articles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Article).offset(skip).limit(limit).all()
