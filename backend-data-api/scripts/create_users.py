from app.database.database import SessionLocal
from app.models.all_models import User
from app.routers.auth_router import get_password_hash

def create_users():
    db = SessionLocal()
    users = [
        {"username": "ministry_admin", "email": "admin@mplads.gov.in", "role": "Ministry", "password": "password123", "full_name": "Ministry Admin"},
        {"username": "state_nodal", "email": "state@mplads.gov.in", "role": "State Nodal Authority", "password": "password123", "full_name": "State Nodal Officer", "state_id": 1},
        {"username": "district_auth", "email": "district@mplads.gov.in", "role": "District Authority", "password": "password123", "full_name": "District Magistrate", "district_id": 1},
        {"username": "inspector", "email": "inspector@mplads.gov.in", "role": "Inspection Officer", "password": "password123", "full_name": "Field Inspector", "district_id": 1}
    ]
    for u in users:
        existing = db.query(User).filter(User.username == u["username"]).first()
        if not existing:
            hashed = get_password_hash(u.pop("password"))
            user = User(**u, password=hashed)
            db.add(user)
    db.commit()
    print("Users created successfully!")

if __name__ == "__main__":
    create_users()
