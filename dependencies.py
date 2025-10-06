from fastapi import Depends, HTTPException
from main import SECRET_KEY, ALGORITHM, oath2_schema
from models import db
from sqlalchemy.orm import Session, sessionmaker
from models import User
from jose import jwt, JWTError

def get_session():
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session
    finally:
        session.close()
        
def verify_token(token: str = Depends(oath2_schema), session: Session = Depends(get_session)):
    try:
        dict_info = jwt.decode(token, SECRET_KEY, ALGORITHM)
        user_id = int(dict_info.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Access denied, check token validity")
    user = session.query(User).filter(User.id==user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid access")
    return user