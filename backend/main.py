from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from model import (
    extract_url_features,
    extract_network_features,
    compute_threat_score,
    risk_level,
    adaptive_response
)
from utils import known_url_check, log_event_db, read_logs_db
from database import engine, get_db
import sql_models
from auth import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Create tables
sql_models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Phishing Detection Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Request / Response Models
# -----------------------------

class URLRequest(BaseModel):
    url: str

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# -----------------------------
# Auth Endpoints
# -----------------------------

@app.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(sql_models.User).filter(sql_models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = sql_models.User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(sql_models.User).filter(sql_models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# -----------------------------
# Scan URL Endpoint
# -----------------------------

@app.post("/scan-url")
def scan_url(request: URLRequest, db: Session = Depends(get_db)):
    # ... existing implementation ...
    url = request.url

    # ML + Network Fusion (Always run to get diagnostics)
    url_features = extract_url_features(url)
    network_features = extract_network_features(url)

    status = known_url_check(url)

    if status == "BLACKLISTED":
        response = {
            "url": url,
            "threat_score": 1.0,
            "risk_level": "High",
            "action": "Blocked",
            "model": "Blacklist",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "details": {
                "url_features": url_features,
                "network_features": network_features
            }
        }
        log_event_db(db, response)
        return response

    if status == "WHITELISTED":
        response = {
            "url": url,
            "threat_score": 0.0,
            "risk_level": "Low",
            "action": "Allowed",
            "model": "Whitelist",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             "details": {
                "url_features": url_features,
                "network_features": network_features
            }
        }
        log_event_db(db, response)
        return response

    score = compute_threat_score(url_features, network_features)
    risk = risk_level(score)
    action = adaptive_response(risk)

    response = {
        "url": url,
        "threat_score": score,
        "risk_level": risk,
        "action": action,
        "model": "ML + Network Fusion",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "details": {
            "url_features": url_features,
            "network_features": network_features
        }
    }

    log_event_db(db, response)
    return response

# -----------------------------
# Logs Endpoint (SIEM) - PROTECTED
# -----------------------------

@app.get("/logs")
def get_logs(current_user: sql_models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return read_logs_db(db)