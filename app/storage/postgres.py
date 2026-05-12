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
    chunk_id        = Column(String, unique=True, nullable=False)
    file_path       = Column(String, nullable=False)
    function_name   = Column(String, nullable=False)
    line_number     = Column(Integer, nullable=False)
    git_commit_hash = Column(String, nullable=False)
    language        = Column(String, nullable=False)
    last_indexed_at = Column(DateTime, default=datetime.utcnow)
    chunk_text      = Column(Text, nullable=False)
    repo_name       = Column(String, nullable=False)

def create_tables():
    Base.metadata.create_all(engine)

def save_chunks(chunks: list[dict]):
    session = SessionLocal()
    try:
        for chunk in chunks:
            existing = session.query(CodeChunk).filter_by(chunk_id=chunk["chunk_id"]).first()
            if not existing:
                record = CodeChunk(
                    chunk_id        = chunk["chunk_id"],
                    file_path       = chunk["file_path"],
                    function_name   = chunk["function_name"],
                    line_number     = chunk["line_number"],
                    git_commit_hash = chunk.get("git_commit_hash", "unknown"),
                    language        = chunk["language"],
                    chunk_text      = chunk["chunk_text"],
                    repo_name       = chunk["repo_name"],
                    last_indexed_at = datetime.utcnow()
                )
                session.add(record)
        session.commit()
        print(f"Saved {len(chunks)} chunks to PostgreSQL")
    except Exception as e:
        session.rollback()
        print(f"PostgreSQL save failed: {e}")
    finally:
        session.close()

def get_chunk_by_id(chunk_id: str):
    session = SessionLocal()
    try:
        return session.query(CodeChunk).filter_by(chunk_id=chunk_id).first()
    finally:
        session.close()

create_tables()
