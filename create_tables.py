import sys
import os

# Ensure app imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.database import engine
from app.database import models

def create_tables():
    print("Creating tables...")
    try:
        print("models: ", models)
        models.Base.metadata.create_all(engine)
        print("Tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    create_tables()
