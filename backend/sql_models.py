from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from datetime import datetime
from database import Base

class ScanLog(Base):
    __tablename__ = "scan_logs"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    threat_score = Column(Float)
    risk_level = Column(String)
    action = Column(String)
    model_used = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON)  # Stores features & diagnostics

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")  # 'admin' or 'user'
