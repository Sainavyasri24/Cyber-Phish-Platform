import pandas as pd
from datetime import datetime
import os

LOG_FILE = "siem_logs.csv"

THREAT_INTEL_FILE = "datasets/threat_intel.csv"
blacklist = set()
whitelist = set()

def load_threat_intel():
    global blacklist, whitelist
    if not os.path.exists(THREAT_INTEL_FILE):
        return
    
    try:
        df = pd.read_csv(THREAT_INTEL_FILE)
        # Handle "bad" / "malicious" for blacklist
        blacklist = set(df[df["type"].isin(["malicious", "bad"])]["url"].values)
        # Handle "benign" / "good" for whitelist
        whitelist = set(df[df["type"].isin(["benign", "good"])]["url"].values)
    except Exception as e:
        print(f"Error loading threat intel: {e}")

# Load on startup (or when module is imported)
load_threat_intel()

def known_url_check(url):
    # Reload every time for demo purposes (optional, better to cache)
    # load_threat_intel() 
    
    if url in blacklist:
        return "BLACKLISTED"
    elif url in whitelist:
        return "WHITELISTED"
    return "UNKNOWN"

from sqlalchemy.orm import Session
from sql_models import ScanLog
from datetime import datetime

# ... (keep known_url_check)

def log_event_db(db: Session, data: dict):
    # Ensure details is valid JSON or dict
    if "details" not in data:
        data["details"] = {}
        
    db_log = ScanLog(
        url=data.get("url"),
        threat_score=data.get("threat_score"),
        risk_level=data.get("risk_level"),
        action=data.get("action"),
        model_used=data.get("model"),
        timestamp=datetime.now(),
        details=data.get("details")
    )
    db.add(db_log)
    try:
        db.commit()
        db.refresh(db_log)
        print(f"[DEBUG] Log saved successfully: ID={db_log.id}, URL={db_log.url}")
    except Exception as e:
        print(f"[ERROR] Failed to save log: {e}")
        db.rollback()
    return db_log

def read_logs_db(db: Session):
    return db.query(ScanLog).order_by(ScanLog.timestamp.desc()).all()