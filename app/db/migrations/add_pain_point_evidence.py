"""Migration to add pain_point_evidence table"""
import sqlite3
import logging

logger = logging.getLogger(__name__)

def migrate(db_path: str):
    """Add pain_point_evidence table"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create pain_point_evidence table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pain_point_evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                idea_id INTEGER NOT NULL,
                platform VARCHAR(50) NOT NULL,
                source_url TEXT NOT NULL,
                title VARCHAR(500),
                snippet TEXT NOT NULL,
                author VARCHAR(255),
                upvotes INTEGER,
                date_posted TIMESTAMP,
                date_found TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                relevance_score REAL,
                FOREIGN KEY (idea_id) REFERENCES startup_ideas(id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_evidence_idea_id ON pain_point_evidence(idea_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_evidence_platform ON pain_point_evidence(platform)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_evidence_relevance ON pain_point_evidence(relevance_score)')
        
        conn.commit()
        logger.info("Successfully created pain_point_evidence table")
        
    except Exception as e:
        logger.error(f"Error creating pain_point_evidence table: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()