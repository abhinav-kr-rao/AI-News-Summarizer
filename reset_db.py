from app.database import database, models

def reset_database():
    print("Resetting database schema...")
    # This will drop the 'articles' table and any others defined in Base
    models.Base.metadata.drop_all(bind=database.engine)
    print("Tables dropped.")
    
    # This recreates them with the latest schema (including 'content' column)
    models.Base.metadata.create_all(bind=database.engine)
    print("Tables created successfully with new schema.")

if __name__ == "__main__":
    reset_database()
