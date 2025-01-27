import argparse
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.models.models import Patron
from app.utils.auth import get_password_hash
from app.database.database import SessionLocal

def create_superuser(email: str, username: str, password: str):
    db = SessionLocal()
    
    # Check if user already exists
    existing_user = db.query(Patron).filter(
        (Patron.email == email) | (Patron.username == username)
    ).first()
    
    if existing_user:
        print(f"Error: User with email '{email}' or username '{username}' already exists.")
        return False
    
    try:
        admin = Patron(
            email=email,
            username=username,
            hashed_password=get_password_hash(password),
            is_superuser=True
        )
        db.add(admin)
        db.commit()
        print(f"Superuser '{username}' created successfully!")
        return True
    except Exception as e:
        print(f"Error creating superuser: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description='Create a superuser for the library management system')
    parser.add_argument('--email', required=True, help='Email address for the superuser')
    parser.add_argument('--username', required=True, help='Username for the superuser')
    parser.add_argument('--password', required=True, help='Password for the superuser')
    
    args = parser.parse_args()
    create_superuser(args.email, args.username, args.password)

if __name__ == "__main__":
    main()
