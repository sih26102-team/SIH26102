import os
import random
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend-data-api')))
from app.models.all_models import (
    Base, State, District, Constituency, MP, Agency, Project, Expenditure, SyntheticGroundTruth, User
)

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://neondb_owner:npg_HASgTI2vt1su@ep-old-dream-b5v0rw4n-pooler.c-7.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def clear_db(db):
    db.query(User).update({User.district_id: None, User.state_id: None})
    db.commit()
    db.query(SyntheticGroundTruth).delete()
    db.query(Expenditure).delete()
    db.query(Project).delete()
    db.query(MP).delete()
    db.query(Agency).delete()
    db.query(Constituency).delete()
    db.query(District).delete()
    db.query(State).delete()
    db.commit()

def generate_synthetic_data():
    db = SessionLocal()
    
    print("Clearing old DB records...")
    clear_db(db)
    print("Old DB records cleared.")
    
    # 1. State
    state = State(state_id=1, state_name="Uttar Pradesh")
    db.add(state)
    db.commit()
    db.refresh(state)
    
    # 2. Districts & Constituencies
    districts = []
    constituencies = []
    mps = []
    agencies = []
    
    for i in range(1, 6): # 5 districts
        dist = District(district_name=f"District {i}", state_id=state.state_id)
        db.add(dist)
        db.commit()
        db.refresh(dist)
        districts.append(dist)
        
        agency = Agency(agency_name=f"PWD {dist.district_name}", agency_type="Government", district_id=dist.district_id)
        db.add(agency)
        agencies.append(agency)
        
        for j in range(1, 3): # 2 constituencies per district
            const = Constituency(constituency_name=f"Constituency {i}-{j}", district_id=dist.district_id)
            db.add(const)
            db.commit()
            db.refresh(const)
            constituencies.append(const)
            
            mp = MP(name=f"MP {i}-{j}", constituency_id=const.constituency_id, state_id=state.state_id, parliamentary_house="Lok Sabha", active_period="2024-2029")
            db.add(mp)
            db.commit()
            db.refresh(mp)
            mps.append(mp)
            
    db.commit()
    
    projects = []
    expenditures = []
    truths = []
    
    # Generate 50 normal projects
    for i in range(50):
        mp = random.choice(mps)
        rec_date = datetime(2024, 1, 15) + timedelta(days=random.randint(0, 100))
        sanc_date = rec_date + timedelta(days=random.randint(30, 70)) # Within 75 days
        
        proj = Project(
            project_id=f"PRJ-NORMAL-{i}",
            project_title=f"Normal Project {i}",
            category="Infrastructure",
            mp_id=mp.mp_id,
            constituency_id=mp.constituency_id,
            state_id=state.state_id,
            district_id=mp.constituency.district_id,
            agency_id=agencies[0].agency_id,
            sanctioned_amount=2000000,
            cost_estimate=2000000,
            released_amount=2000000,
            expenditure=2000000,
            project_status="completed",
            recommendation_date=rec_date,
            sanction_date=sanc_date,
            start_date=sanc_date + timedelta(days=15),
            expected_completion_date=sanc_date + timedelta(days=200),
            actual_completion_date=sanc_date + timedelta(days=190),
            progress_percentage=100.0,
            latitude=26.0 + random.uniform(0.1, 1.0),
            longitude=80.0 + random.uniform(0.1, 1.0),
            sc_st_area_flag=True if random.random() > 0.5 else False,
            data_source="SYNTHETIC_DEMO"
        )
        db.add(proj)
        projects.append(proj)
        
    # Scenario 1: Statutory Delay (> 75 days)
    mp = random.choice(mps)
    rec_date = datetime(2024, 1, 15)
    sanc_date = rec_date + timedelta(days=120) # 120 days later
    proj_delay = Project(
        project_id=f"PRJ-ANOMALY-DELAY",
        project_title=f"Delayed Sanction Project",
        category="Infrastructure",
        mp_id=mp.mp_id,
        constituency_id=mp.constituency_id,
        state_id=state.state_id,
        district_id=mp.constituency.district_id,
        sanctioned_amount=5000000,
        project_status="ongoing",
        recommendation_date=rec_date,
        sanction_date=sanc_date,
        data_source="SYNTHETIC_DEMO"
    )
    db.add(proj_delay)
    truths.append(SyntheticGroundTruth(project_id=proj_delay.project_id, injected_scenario="Delay > 75 days", expected_detection=True))

    # Scenario 2: Financial Anomaly (Expenditure > Sanction)
    proj_fin = Project(
        project_id=f"PRJ-ANOMALY-FIN",
        project_title=f"Overspending Project",
        category="Health",
        mp_id=mp.mp_id,
        constituency_id=mp.constituency_id,
        state_id=state.state_id,
        district_id=mp.constituency.district_id,
        sanctioned_amount=1000000,
        expenditure=1500000,
        project_status="ongoing",
        recommendation_date=datetime(2024, 2, 1),
        sanction_date=datetime(2024, 3, 1),
        data_source="SYNTHETIC_DEMO"
    )
    db.add(proj_fin)
    truths.append(SyntheticGroundTruth(project_id=proj_fin.project_id, injected_scenario="Expenditure > Sanction", expected_detection=True))

    # Scenario 3: Geospatial Concentration (out-of-constituency up to 50 lakh rule abuse)
    # Modeling UP 2026 case: Multiple MPs funding works in a specific district
    target_district = districts[0]
    for i in range(10):
        out_mp = mps[i % len(mps)]
        if out_mp.constituency.district_id == target_district.district_id:
            continue # Needs to be out of constituency
        proj_out = Project(
            project_id=f"PRJ-ANOMALY-OUT-{i}",
            project_title=f"Trust/NGO Support {i}",
            category="Education",
            mp_id=out_mp.mp_id,
            constituency_id=target_district.constituencies[0].constituency_id, # Different constituency
            state_id=state.state_id,
            district_id=target_district.district_id,
            sanctioned_amount=4500000, # Just under 50 lakh limit
            project_status="ongoing",
            recommendation_date=datetime(2024, 2, 1),
            sanction_date=datetime(2024, 3, 1),
            latitude=26.50 + random.uniform(0.01, 0.05), # Clustered tightly
            longitude=80.50 + random.uniform(0.01, 0.05),
            data_source="SYNTHETIC_DEMO"
        )
        db.add(proj_out)
        truths.append(SyntheticGroundTruth(project_id=proj_out.project_id, injected_scenario="Out-of-constituency spatial concentration", expected_detection=True))
        
    db.commit()
    for t in truths:
        db.add(t)
    db.commit()
    
    print("Synthetic data generated and ingested directly into Neon DB via SQLAlchemy.")

if __name__ == "__main__":
    generate_synthetic_data()
