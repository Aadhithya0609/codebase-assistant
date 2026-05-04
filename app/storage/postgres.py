from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.config import POSTGRES_URL

Base = declarative_base()
engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(bind=engine)

class CodeChunk(Base):
    __tablename__ = "code_chunks"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    file_path       = Column(String, nullable=False)
    function_name   = Column(String, nullable=False)
    line_number     = Column(Integer, nullable=False)
    git_commit_hash = Column(String, nullable=False)
    language        = Column(String, nullable=False)
    last_indexed_at = Column(DateTime, default=datetime.utcnow)
    chunk_text      = Column(Text, nullable=False)

def create_tables():
    Base.metadata.create_all(engine)
    print("Tables created")

if __name__ == "__main__":
    create_tables()