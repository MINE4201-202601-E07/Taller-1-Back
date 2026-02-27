from sqlalchemy.orm import Session
from modules.users.user_model import User

class UserService:
    @staticmethod
    def create_user(db: Session, email: str, name: str, password: str):
        user = User(email=email, name=name, password=password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_all_users(db: Session):
        return db.query(User).all()

    @staticmethod
    def update_user(db: Session, user_id: int, data: dict):
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            for key, value in data.items():
                setattr(user, key, value)
            db.commit()
            db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        return False