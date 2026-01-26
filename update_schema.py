from app.database import database, models

def update_schema():
    print("Updating database schema...")
    # create_all checks for existing tables and only creates missing ones.
    # successful for adding new tables like 'Digests'
    models.Base.metadata.create_all(bind=database.engine)
    print("Schema updated (new tables created if missing).")

if __name__ == "__main__":
    update_schema()
