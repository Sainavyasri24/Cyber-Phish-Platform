import pandas as pd
from database import engine, SessionLocal, Base
from sql_models import ScanLog
import json
from datetime import datetime

# localized timestamp format in CSV is problematic to parse perfectly if inconsistent
# we will try standard format, else fail gracefully

def migrate():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    
    try:
        print("Reading CSV logs...")
        try:
            df = pd.read_csv("siem_logs.csv")
        except FileNotFoundError:
            print("No CSV logs found. Starting fresh.")
            return

        print(f"Found {len(df)} logs. Migrating...")
        
        for _, row in df.iterrows():
            # Parse details JSON safely
            details = {}
            if isinstance(row.get("details"), str):
                try:
                    details = json.loads(row["details"].replace("'", "\"")) # Basic fix for single quotes
                except:
                    pass
            
            # Parse timestamp if possible, else now
            ts = datetime.utcnow()
            try:
                ts = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            except:
                pass

            log = ScanLog(
                url=row.get("url", ""),
                threat_score=row.get("threat_score", 0.0),
                risk_level=row.get("risk_level", "Unknown"),
                action=row.get("action", "Unknown"),
                model_used=row.get("model", "Unknown"),
                timestamp=ts,
                details=details
            )
            session.add(log)
        
        session.commit()
        print("Migration complete!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    migrate()
