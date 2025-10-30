from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db, engine, Base
from models import User, Advertisement
from schemas import UserCreate, UserOut, UserUpdate, Token, AdCreate, AdOut
from auth import get_current_user

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/user", response_model=UserOut)
def register(user_create: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_create.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    password = user_create.password[:72]
    new_user = User(email=user_create.email, role="user", hashed_password="")
    new_user.set_password(password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/login", response_model=Token)
def login(user_create: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_create.email).first()
    if not user or not user.verify_password(user_create.password[:72]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    user.set_token()
    db.commit()
    return {"access_token": user.token, "token_type": "bearer"}


@app.get("/user/{user_id}", response_model=UserOut)
def get_user(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.patch("/user/{user_id}", response_model=UserOut)
def update_user(user_id: int, user_update: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_update.email:
        user.email = user_update.email
    if user_update.password:
        user.set_password(user_update.password[:72])
    if user_update.role and current_user.role == "admin":
        user.role = user_update.role
    db.commit()
    db.refresh(user)
    return user


@app.delete("/user/{user_id}")
def delete_user(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted"}


@app.post("/advertisement", response_model=AdOut)
def create_ad(ad: AdCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_ad = Advertisement(title=ad.title, description=ad.description or "", owner_id=current_user.id)
    db.add(new_ad)
    db.commit()
    db.refresh(new_ad)
    return new_ad


@app.get("/advertisement/{advertisement_id}", response_model=AdOut)
def get_ad(advertisement_id: int, db: Session = Depends(get_db)):
    ad = db.query(Advertisement).filter(Advertisement.id == advertisement_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return ad


@app.patch("/advertisement/{advertisement_id}", response_model=AdOut)
def update_ad(advertisement_id: int, ad_update: AdCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ad = db.query(Advertisement).filter(Advertisement.id == advertisement_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    if ad.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not allowed to update")
    if ad_update.title:
        ad.title = ad_update.title
    if ad_update.description is not None:
        ad.description = ad_update.description
    db.commit()
    db.refresh(ad)
    return ad


@app.delete("/advertisement/{advertisement_id}")
def delete_ad(advertisement_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ad = db.query(Advertisement).filter(Advertisement.id == advertisement_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    if ad.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not allowed to delete")
    db.delete(ad)
    db.commit()
    return {"detail": "Advertisement deleted"}


@app.get("/advertisement", response_model=list[AdOut])
def search_ads(search: str = Query(None, min_length=1), db: Session = Depends(get_db)):
    query = db.query(Advertisement)
    if search:
        like_pattern = f"%{search}%"
        query = query.filter(Advertisement.title.ilike(like_pattern) | Advertisement.description.ilike(like_pattern))
    ads = query.all()
    return ads
