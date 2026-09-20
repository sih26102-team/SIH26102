import random
from app.database.database import SessionLocal
from app.models.all_models import User

def generate_users():
    db = SessionLocal()
    users = db.query(User).all()
    
    first_names = ["Arjun", "Neha", "Vikram", "Priya", "Rahul", "Anjali", "Suresh", "Meera", "Karthik", "Sneha", "Rajesh", "Kavita", "Amit", "Pooja", "Sanjay", "Ritu", "Vivek", "Anita"]
    last_names = ["Sharma", "Verma", "Reddy", "Patel", "Kumar", "Singh", "Rao", "Iyer", "Nair", "Das", "Gupta", "Joshi", "Desai", "Menon", "Pillai"]
    
    for u in users:
        if u.role == "MINISTRY":
            # Ministry keeps the original mplads.monitor01 etc
            continue
            
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        u.full_name = f"{fname} {lname}"
        
        if u.role == "STATE_AUTHORITY":
            u.username = f"{fname.lower()}.{lname.lower()}{u.id}"
        elif u.role == "DISTRICT_AUTHORITY":
            u.username = f"{fname.lower()}.dm{u.id}"
        elif u.role == "INSPECTION_OFFICER":
            emp_id = random.randint(1000, 9999)
            u.username = f"emp{emp_id}.{lname.lower()}{u.id}"
            
    db.commit()
    print("Usernames updated!")
    
    state = db.query(User).filter(User.role=="STATE_AUTHORITY").first()
    dist = db.query(User).filter(User.role=="DISTRICT_AUTHORITY").first()
    insp = db.query(User).filter(User.role=="INSPECTION_OFFICER").first()
    
    print(f"State: {state.username}")
    print(f"District: {dist.username}")
    print(f"Inspector: {insp.username}")

if __name__ == "__main__":
    generate_users()
