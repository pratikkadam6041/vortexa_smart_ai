# vortexa.py

import asyncio
import traceback
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from database import Base
# --- Project Imports ---
import models, crud, schemas, security
from database import SessionLocal, engine
from api_handler import get_live_weather, get_soil_data, get_historical_weather
from suggestion_engine import suggest_crops

# This creates your database tables when the app starts
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Dependencies ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

# --- API Endpoints ---

# User and Field Management
@app.post("/users/", response_model=schemas.User)
def create_new_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/fields/", response_model=schemas.Field)
def create_field_for_user(
    field: schemas.FieldCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_user_field(db=db, field=field, user_id=current_user.id)

@app.get("/fields/", response_model=list[schemas.Field])
def read_user_fields(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    fields = crud.get_fields_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return fields

# Data and Suggestion Endpoints
@app.get("/weather")
async def get_weather_endpoint(lat: float, lon: float):
    data = await get_live_weather(lat, lon)
    return data
@app.get("/")
def root():
    return {"message": "Vortexa AI Crop Suggester API is live!"}
@app.get("/suggest-crop")
async def get_crop_suggestion_endpoint(lat: float, lon: float):
    try:
        soil_data, historical_weather = await asyncio.gather(
            get_soil_data(lat, lon),
            get_historical_weather(lat, lon)
        )

        if "error" in soil_data or "error" in historical_weather:
            print("Soil Data Response:", soil_data)
            print("Weather Data Response:", historical_weather)
            raise HTTPException(status_code=500, detail="Could not fetch data for suggestion.")

        suggestions = suggest_crops(soil_data, historical_weather)
        
        return {
            "location_data": {
                "latitude": lat, "longitude": lon,
                "soil": soil_data, "climate": historical_weather
            },
            "suggested_crops": suggestions
        }
    except Exception as e:
        traceback.print_exc() 
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")