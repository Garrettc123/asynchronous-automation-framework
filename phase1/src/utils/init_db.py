"""
Database initialization script
Creates all tables in the database
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from dotenv import load_dotenv
from phase1.src.models.revenue_models import Base

# Load environment variables
load_dotenv()

def init_database():
    """Initialize database with all tables"""
    database_url = os.getenv('DATABASE_URL', 'sqlite:///revenue.db')
    
    print(f"Initializing database at: {database_url}")
    
    # Create engine
    engine = create_engine(database_url)
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    print("Database tables created successfully!")
    print("Tables created:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")

if __name__ == '__main__':
    init_database()
