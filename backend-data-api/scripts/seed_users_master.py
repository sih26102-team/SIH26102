from sqlalchemy import text
from app.database.database import SessionLocal
from app.models.all_models import User, State, District
from app.routers.auth_router import get_password_hash

def seed_master_users():
    db = SessionLocal()
    
    # Get 4 states
    states = db.query(State).limit(4).all()
    if len(states) < 4:
        print("Not enough states in DB!")
        return

    users = []
    
    # 1. Ministry (2)
    users.extend([
        {"username": "mplads.monitor01", "email": "monitor01@prototype.gov.in", "role": "MINISTRY", "password": "password123", "full_name": "Rajiv Menon", "designation": "MoSPI / MPLADS Monitoring Officer"},
        {"username": "mplads.monitor02", "email": "monitor02@prototype.gov.in", "role": "MINISTRY", "password": "password123", "full_name": "Neha Srivastava", "designation": "MoSPI / MPLADS Monitoring Officer"},
    ])
    
    state_names = ["S. Ananya Rao", "Vivek Reddy", "Meera Kulkarni", "Karthik Subramanian"]
    
    # 2. State Nodal (4)
    for i, state in enumerate(states):
        users.append({
            "username": f"state.{state.state_name.lower().replace(' ', '')}",
            "email": f"state{i+1}@prototype.gov.in",
            "role": "STATE_AUTHORITY",
            "password": "password123",
            "full_name": state_names[i],
            "designation": "State Nodal Authority",
            "state_id": state.state_id
        })
        
        # 3. District Authority (12) - 3 per state
        districts = db.query(District).filter(District.state_id == state.state_id).limit(3).all()
        for j, dist in enumerate(districts):
            users.append({
                "username": f"dist.{dist.district_name.lower().replace(' ', '')}",
                "email": f"dist_{state.state_id}_{dist.district_id}@prototype.gov.in",
                "role": "DISTRICT_AUTHORITY",
                "password": "password123",
                "full_name": f"District Mag. {j+1}",
                "designation": f"District Authority - {dist.district_name}",
                "state_id": state.state_id,
                "district_id": dist.district_id
            })
            
            # 4. Inspection Officer (24) - 2 per district
            for k in range(2):
                users.append({
                    "username": f"insp.{dist.district_name.lower().replace(' ', '')}.0{k+1}",
                    "email": f"insp_{dist.district_id}_{k+1}@prototype.gov.in",
                    "role": "INSPECTION_OFFICER",
                    "password": "password123",
                    "full_name": f"Inspection Officer {chr(65+k)}",
                    "designation": "Authorized Inspection Officer",
                    "state_id": state.state_id,
                    "district_id": dist.district_id
                })
                
    # Delete all existing users cleanly
    # db.execute(text("TRUNCATE TABLE users CASCADE"))
    
    for u in users:
        existing = db.query(User).filter(User.username == u["username"]).first()
        if existing:
            existing.role = u["role"]
            existing.state_id = u.get("state_id")
            existing.district_id = u.get("district_id")
            existing.designation = u["designation"]
            existing.full_name = u["full_name"]
            existing.email = u["email"]
        else:
            hashed = get_password_hash(u.pop("password"))
            user = User(**u, password=hashed)
            db.add(user)
        
    db.commit()
    print(f"Successfully seeded {len(users)} users.")

if __name__ == "__main__":
    seed_master_users()
