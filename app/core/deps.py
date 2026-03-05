from app.core.db import SessionLocal

def get_db():
    """
    Provides a database session for a single request, ensuring it is closed afterward.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()