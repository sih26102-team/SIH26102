import pandas as pd
from datetime import datetime
from app.database.database import SessionLocal, engine, Base
from app.models import State, District, Constituency, MP, Agency, Project, Expenditure

print("Dropping all tables and recreating...")
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def seed():
    db = SessionLocal()
    import os
    csv_dir = os.path.join(os.path.dirname(__file__), "../..", "data-pipeline", "processed_data")
    
    print("Seeding States...")
    states_df = pd.read_csv(os.path.join(csv_dir, "states.csv"))
    for _, row in states_df.iterrows():
        db.add(State(**{k: v for k, v in row.to_dict().items() if hasattr(State, k)}))
    db.commit()

    print("Seeding Districts...")
    districts_df = pd.read_csv(os.path.join(csv_dir, "districts.csv"))
    for _, row in districts_df.iterrows():
        db.add(District(**{k: v for k, v in row.to_dict().items() if hasattr(District, k)}))
    db.commit()

    print("Seeding Constituencies...")
    constituencies_df = pd.read_csv(os.path.join(csv_dir, "constituencies.csv"))
    for _, row in constituencies_df.iterrows():
        db.add(Constituency(**{k: v for k, v in row.to_dict().items() if hasattr(Constituency, k)}))
    db.commit()

    print("Seeding Agencies...")
    agencies_df = pd.read_csv(os.path.join(csv_dir, "agencies.csv"))
    for _, row in agencies_df.iterrows():
        db.add(Agency(**{k: v for k, v in row.to_dict().items() if hasattr(Agency, k)}))
    db.commit()

    print("Seeding MPs...")
    mps_df = pd.read_csv(os.path.join(csv_dir, "mps.csv"))
    for _, row in mps_df.iterrows():
        db.add(MP(**{k: v for k, v in row.to_dict().items() if hasattr(MP, k)}))
    db.commit()

    print("Seeding Projects...")
    projects_df = pd.read_csv(os.path.join(csv_dir, "projects.csv"))
    projects_df = projects_df.drop_duplicates(subset=['project_id'])
    for _, row in projects_df.iterrows():
        d = {k: v for k, v in row.to_dict().items() if pd.notna(v)}
        if 'expected_completion_date' in d and isinstance(d['expected_completion_date'], str):
            d['expected_completion_date'] = datetime.strptime(d['expected_completion_date'], '%Y-%m-%d').date()
        if 'start_date' in d:
            if isinstance(d['start_date'], float): 
                del d['start_date']
            elif isinstance(d['start_date'], str):
                d['start_date'] = datetime.strptime(d['start_date'], '%Y-%m-%d').date()
        if 'actual_completion_date' in d:
            if isinstance(d['actual_completion_date'], float): 
                del d['actual_completion_date']
            elif isinstance(d['actual_completion_date'], str):
                d['actual_completion_date'] = datetime.strptime(d['actual_completion_date'], '%Y-%m-%d').date()
        db.add(Project(**{k: v for k, v in d.items() if hasattr(Project, k)}))
    db.commit()

    if os.path.exists(os.path.join(csv_dir, "expenditures.csv")):
        print("Seeding Expenditures...")
        exp_df = pd.read_csv(os.path.join(csv_dir, "expenditures.csv"))
        for _, row in exp_df.iterrows():
            d = {k: v for k, v in row.to_dict().items() if pd.notna(v)}
            if 'date' in d and isinstance(d['date'], str):
                d['date'] = datetime.strptime(d['date'], '%Y-%m-%d').date()
            db.add(Expenditure(**{k: v for k, v in d.items() if hasattr(Expenditure, k)}))
        db.commit()

if __name__ == "__main__":
    seed()
